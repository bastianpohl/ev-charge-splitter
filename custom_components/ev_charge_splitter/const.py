"""Constants for the EV Charge Splitter integration."""

DOMAIN = "ev_charge_splitter"

CONF_CHARGER_POWER_SENSOR = "charger_power_sensor"
CONF_GRID_IMPORT_SENSOR = "grid_import_sensor"
CONF_BATTERY_DISCHARGE_SENSOR = "battery_discharge_sensor"

SENSOR_TYPES = {
    "grid_share": "Grid Share",
    "battery_share": "Battery Share",
    "solar_share": "Solar Share",
}
