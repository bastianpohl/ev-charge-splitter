"""Sensor platform for EV Charge Splitter."""
import logging
from typing import Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    DOMAIN,
    CONF_CHARGER_POWER_SENSOR,
    CONF_GRID_IMPORT_SENSOR,
    CONF_BATTERY_DISCHARGE_SENSOR,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the EV Charge Splitter sensors."""
    config = hass.data[DOMAIN][config_entry.entry_id]

    charger_sensor = config[CONF_CHARGER_POWER_SENSOR]
    grid_sensor = config[CONF_GRID_IMPORT_SENSOR]
    battery_sensor = config[CONF_BATTERY_DISCHARGE_SENSOR]

    entities = []
    for sensor_type, name in SENSOR_TYPES.items():
        entities.append(
            EVChargeSplitterSensor(
                config_entry.entry_id,
                sensor_type,
                name,
                charger_sensor,
                grid_sensor,
                battery_sensor,
            )
        )

    async_add_entities(entities)


class EVChargeSplitterSensor(SensorEntity):
    """Representation of an EV Charge Splitter sensor."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_should_poll = False

    def __init__(
        self,
        entry_id: str,
        sensor_type: str,
        name: str,
        charger_sensor: str,
        grid_sensor: str,
        battery_sensor: str,
    ) -> None:
        """Initialize the sensor."""
        self._entry_id = entry_id
        self._type = sensor_type
        self._charger_sensor = charger_sensor
        self._grid_sensor = grid_sensor
        self._battery_sensor = battery_sensor

        self._attr_name = f"EV Charge Splitter {name}"
        self._attr_unique_id = f"{entry_id}_{sensor_type}"
        self._state: Optional[float] = None

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        def async_state_changed_listener(event):
            """Handle child updates."""
            self.async_schedule_update_ha_state(True)

        # Track state changes of all three input sensors
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._charger_sensor, self._grid_sensor, self._battery_sensor],
                async_state_changed_listener,
            )
        )
        # Set initial state
        self.async_schedule_update_ha_state(True)

    def _get_float_state(self, entity_id: str) -> float:
        """Helper to safely get float state of an entity and convert kW to W if needed."""
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable"):
            return 0.0

        try:
            val = float(state.state)
        except ValueError:
            return 0.0

        # Automatic unit detection and conversion:
        unit = state.attributes.get("unit_of_measurement")
        if unit == UnitOfPower.KILOWATT or (unit and "kW" in str(unit)):
            val = val * 1000.0

        return val

    @property
    def native_value(self) -> Optional[float]:
        """Return the state of the sensor."""
        return self._state

    async def async_update(self) -> None:
        """Update the sensor value based on the formula."""
        # 1. Fetch values
        charger_power = self._get_float_state(self._charger_sensor)
        grid_import = self._get_float_state(self._grid_sensor)
        battery_discharge = self._get_float_state(self._battery_sensor)

        # 2. Priority Logic
        # - Grid Share (First Priority)
        grid_share = max(0.0, min(charger_power, grid_import))
        remaining_power = charger_power - grid_share

        # - Battery Share (Second Priority)
        battery_share = max(0.0, min(remaining_power, battery_discharge))

        # - Solar Share (Remaining)
        solar_share = max(0.0, charger_power - grid_share - battery_share)

        # 3. Assign correct value depending on the type of this sensor
        if self._type == "grid_share":
            val = grid_share
        elif self._type == "battery_share":
            val = battery_share
        elif self._type == "solar_share":
            val = solar_share
        else:
            val = 0.0

        self._state = round(val, 1)
