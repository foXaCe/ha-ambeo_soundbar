

# Ambeo Soundbar for Home Assistant
[![GitHub Release](https://img.shields.io/github/v/release/faizpuru/ha-ambeo_soundbar?style=flat)](https://github.com/faizpuru/ha-ambeo_soundbar/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)](LICENSE)

Home Assistant integration to control your Sennheiser AMBEO soundbar directly from your smart home system.

[![Sennheiser](https://raw.githubusercontent.com/home-assistant/brands/refs/heads/master/custom_integrations/ambeo_soundbar/logo.png)](https://www.sennheiser-hearing.com/soundbars/)

## Compatible Devices
- AMBEO Soundbar Max
- AMBEO Soundbar Mini
- AMBEO Soundbar Plus

## Features
### Audio Features

| Feature | Max | Plus | Mini | Description |
|---------|----------|---------|---------|-------------|
| Night Mode | ✅ | ✅ | ✅ | Reduces dynamic range and bass intensity for quiet listening environments |
| Ambeo Mode | ✅ | ✅ | ✅ | Enables 3D virtualization technology for immersive sound experience |
| Voice Enhancement | ✅ | ✅ | ✅ | Emphasizes dialogue frequencies for clearer speech in media content |
| Sound Feedback | ✅ | ✅ | ✅ | Enables/disables audio confirmation for user actions |
| Subwoofer Support | ✅ | ✅ | ✅ | Controls for external subwoofer connection, volume and power status |

### Sources Management

| Feature | Max | Plus | Mini | Description |
|---------|----------|---------|---------|-------------|
| Source Selection | ✅ | ✅ | ✅ | Controls input source selection (HDMI, Optical, Bluetooth, etc.) |
| Audio Presets | ✅ | ✅ | ✅ | Sound profiles optimized for different content types |

### Display Controls

| Feature | Max | Plus | Mini | Description |
|---------|----------|---------|---------|-------------|
| Ambeo Logo | ✅ | ✅ | ✅ | Controls the illuminated Ambeo logo brightness on device |
| LED Bar | ❌ | ✅ | ✅ | Controls front LED display bar brightness for visual feedback |
| Main Display | ✅ | ❌ | ❌ | Controls device's screen brightness and display settings |
| Codec LED | ❌ | ✅ | ✅ | Controls LED indicator showing active audio codec |

### Media Player Controls

| Feature | Max | Plus | Mini | Description |
|---------|----------|---------|---------|-------------|
| Play/Pause | ✅ | ✅ | ✅ | Controls media playback state |
| Next/Previous | ✅ | ✅ | ✅ | Skip to next or previous track |
| Volume | ✅ | ✅ | ✅ | Adjusts audio volume level |
| Mute | ✅ | ✅ | ✅ | Toggles audio mute state |

### Additional Features

| Feature | Max | Plus | Mini | Description |
|---------|----------|---------|---------|-------------|
| Bluetooth Pairing | ❌ | ✅ | ✅ | Manages Bluetooth device pairing mode and connected devices |
| Standby Control | ✅ | ❌ | ❌ | Controls device power state between active and standby mode |
| Restart | ✅ | ✅ | ✅ | Reboots the device |

## 🚀 Quick Start

### 📦 Using HACS (Recommended)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=faizpuru&repository=ha-ambeo_soundbar&category=integration)

1. Use the button above or search for "Ambeo Soundbar" in HACS
2. Download the integration and restart Home Assistant

### ⚙️ Manual Installation
1. Download the `custom_components/ambeo_soundbar` directory to your Home Assistant configuration directory
2. Restart Home Assistant

## 🔧 Setup
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ambeo_soundbar)

### Automatic Discovery (Recommended)
Your AMBEO Soundbar will be automatically discovered on your network using Zeroconf/mDNS. When detected, you'll receive a notification in Home Assistant to add the device with just one click.

### Manual Setup
1. Go to the Integrations page in Home Assistant
2. Click "Add Integration" and search for "Ambeo Soundbar"
3. Enter your soundbar's hostname (e.g., `ambeo.local`) or IP address (e.g., `192.168.1.100`)
4. Integration will be ready within a few seconds

## 🎛️ Advanced Features

### Custom Services

The integration provides advanced services for fine-tuning your soundbar:

#### `ambeo_soundbar.set_expert_audio_levels`
Configure expert audio levels for AMBEO Soundbar Max:
- **Voice Enhancement Level** (-6 to 6): Adjust dialogue clarity
- **Center Speaker Level** (-6 to 6): Control center channel output
- **Side Firing Level** (-6 to 6): Adjust width/surround speakers
- **Up Firing Level** (-6 to 6): Control height/Atmos speakers

```yaml
service: ambeo_soundbar.set_expert_audio_levels
data:
  voice_enhancement_level: 2
  center_speaker_level: 0
  side_firing_level: 1
  up_firing_level: 1
```

#### `ambeo_soundbar.set_eq_preset`
Apply predefined equalizer presets via service:
```yaml
service: ambeo_soundbar.set_eq_preset
data:
  preset: "Movies"  # Options: Neutral, Movies, Sport, News, Music
```

#### `ambeo_soundbar.reset_expert_settings`
Reset all expert audio settings to factory defaults (Max only):
```yaml
service: ambeo_soundbar.reset_expert_settings
```

### Audio Preset Selector

A **Select entity** is automatically created to change audio presets directly from the UI:
- **Entity**: `select.ambeo_soundbar_audio_preset`
- **Available presets**: Automatically detected from your soundbar model
  - **Max**: Neutral, Movies, Sport, News, Music
  - **Plus/Mini**: Adaptive, Music, Movie, News, Voice (dynamically loaded)
- Change presets with a simple dropdown in Lovelace cards or automations

Example automation:
```yaml
automation:
  - alias: "Movie mode at night"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: select.select_option
        target:
          entity_id: select.ambeo_soundbar_audio_preset
        data:
          option: "Movies"
```

### Direct Device Access

A **configuration link** is automatically added to the device information page, allowing you to:
- Click the device card in Home Assistant
- Access the **"Visit Device"** link
- Open the soundbar's web interface directly in your browser
- Configure advanced settings, firmware updates, and more

The link points to `http://[soundbar-ip]` and provides direct access to the Sennheiser web UI.

### Built-in Diagnostics

Access comprehensive device diagnostics from Home Assistant:
- Settings → Devices & Services → Ambeo Soundbar → (device) → Download Diagnostics

Includes:
- Device information (model, firmware, serial)
- Current state snapshot
- API capabilities
- Configuration data

### Adaptive Polling

The integration automatically adjusts its update frequency based on device state:
- **Playing**: 5 seconds (real-time updates)
- **Idle**: 30 seconds (standard monitoring)
- **Standby**: 60 seconds (minimal network traffic)

### Automatic Reconnection

Built-in retry logic with exponential backoff ensures reliable connectivity:
- Automatic reconnection on network issues
- Smart backoff timing (1s → 2s → 4s → 8s → 10s max)
- Graceful degradation on persistent errors

## ❓ Troubleshooting

### Device Unavailable / Connection Errors

If you encounter any issues:
1. Verify that your soundbar is powered on and connected to your network
2. Double-check that the configured IP address is correct
3. Check Home Assistant logs for any error details
4. Download diagnostics from the device page for detailed troubleshooting

### Reducing Log Verbosity (Device Offline)

When your soundbar is powered off or disconnected, Home Assistant may show detailed error logs. To reduce log verbosity, add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    # Reduce integration logs to info level (hides debug details)
    custom_components.ambeo_soundbar: info

    # Hide traceback from HA Core when device is unavailable (optional)
    homeassistant.config_entries: warning
```

After adding this configuration:
1. Save `configuration.yaml`
2. Restart Home Assistant
3. You'll only see brief "device unavailable" messages instead of full tracebacks

**Note**: When the device is unavailable, the integration will automatically retry connection and restore functionality once the device comes back online.


## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest improvements
- 🔀 Submit pull requests

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This project is a community development and is not affiliated with or endorsed by Sennheiser. All product names, logos, and brands are property of their respective owners.

---

If you find this integration helpful, please consider giving it a ⭐️ on GitHub!
