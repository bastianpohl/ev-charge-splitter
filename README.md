# ⚡ EV Charge Splitter for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Add to My Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg?style=for-the-badge)](https://my.home-assistant.io/redirect/hacs_repository/?owner=chewie&repository=ev-charge-splitter&category=integration)

A premium, native Home Assistant integration that splits your EV/Wallbox charging power in real-time into three separate sensors: **Grid Share**, **Battery Share**, and **Solar (PV) Share**.

---

## ✨ Features

- 🔌 **Universal Compatibility:** Works with any Wallbox or EV integration (Tesla, Easee, go-e, etc.).
- 🛠️ **Full UI Setup (Config Flow):** No YAML templating required! Select your source sensors from simple dropdowns.
- ⚙️ **Smart Unit Detection:** Automatically detects if your charger power is in `kW` or `W` and converts it automatically.
- 🛡️ **Fail-Safe Logic:** Gracefully handles `unavailable` or `unknown` states (e.g. when your car goes offline).

---

## 📐 The Priority Math

The splitter calculates energy allocation based on actual physical priorities:
1. **Grid Share (1st Priority):** EV power is first matched against grid import (since grid energy is imported directly).
2. **Battery Share (2nd Priority):** Remaining EV power is matched against house battery discharge.
3. **Solar/PV Share (3rd Priority):** Any leftover charging power is attributed to excess solar production.

---

## 🚀 Installation

### Option 1: HACS (Recommended)
1. Click the **Add to My Home Assistant** button above, or manually add `https://github.com/chewie/ev-charge-splitter` as a **Custom Repository** in HACS (Category: *Integration*).
2. Download the integration.
3. Restart Home Assistant.

### Option 2: Manual Installation
1. Download the `custom_components/ev_charge_splitter/` folder from this repository.
2. Copy it into your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.

---

## ⚙️ Configuration

1. In Home Assistant, go to **Settings > Devices & Services** (Einstellungen > Geräte & Dienste).
2. Click **Add Integration** in the bottom right.
3. Search for **EV Charge Splitter** and select it.
4. Fill in your input sensors in the UI form:
   - **Charger Power Sensor** (e.g., `sensor.tesla_charger_power`)
   - **Grid Import Power Sensor** (e.g., `sensor.grid_power_import`)
   - **Battery Discharge Power Sensor** (e.g., `sensor.battery_discharge`)
5. Click **Submit**!

Three new sensors will be created:
- `sensor.ev_charge_splitter_grid_share`
- `sensor.ev_charge_splitter_battery_share`
- `sensor.ev_charge_splitter_solar_share`

---

## 📊 Dashboard Visualization (ApexCharts Card)

To get a gorgeous stacked view of your EV charging source distribution (similar to the Tesla app), install the HACS **ApexCharts Card** and add this Lovelace configuration to your dashboard:

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: "🔋 Ladeleistungs-Verteilung (Letzte 24 Std.)"
  show_states: true
  colorize_states: true
chart_type: area
stacked: true
graph_span: 24h
span:
  end: now
yaxis:
  - min: 0
    apex_config:
      title:
        text: "Leistung (Watt)"
series:
  - entity: sensor.ev_charge_splitter_solar_share
    name: "Solar / PV"
    color: "#F4B400"
    type: area
    group_by:
      func: avg
      duration: 5m
  - entity: sensor.ev_charge_splitter_battery_share
    name: "Hausbatterie"
    color: "#0F9D58"
    type: area
    group_by:
      func: avg
      duration: 5m
  - entity: sensor.ev_charge_splitter_grid_share
    name: "Netzstrom"
    color: "#4285F4"
    type: area
    group_by:
      func: avg
      duration: 5m
```
