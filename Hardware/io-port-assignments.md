# Jetson Orin NX I/O Port Assignment Tracker

**Device**: Waveshare Jetson Orin NX 16GB Dev Kit (SKU 24222)  
**Last Updated**: 2026-04-18

## Port Inventory

### USB Ports
| Port | Type | Status | Assignment | Notes |
|------|------|--------|------------|-------|
| USB-A #1 | USB 3.0 Type-A | **ASSIGNED** | Pico (power + serial control) | RP2350 MCU for servo PWM at 333 Hz |
| USB-A #2 | USB 3.0 Type-A | **ASSIGNED** | Camera (IMX296 USB3) | Single USB 3 cable provides both camera power and data |
| USB-A #3 | USB 3.0 Type-A | **ASSIGNED** | Display touch/power (USB-A to USB-C cable) | Powers touch interface for Waveshare capacitive display |
| USB-A #4 | USB 3.0 Type-A | AVAILABLE | — | Reserve for future peripherals or external SSD |
| USB-C | USB Type-C | **RESERVED** | Development/debugging (keep free) | Alternate for serial console, power input, or future expansion |

### Display & Video
| Port | Type | Status | Assignment | Notes |
|------|------|--------|------------|-------|
| HDMI | HDMI 2.1 | **ASSIGNED** | Waveshare 10.1EP-CAPLCD | 1920×1200 capacitive touch display |

### Power Input
| Port | Type | Status | Assignment | Notes |
|------|------|--------|------------|-------|
| 5.5×2.5 mm DC jack | Barrel connector | **ASSIGNED** | 12V main supply (from WUPP distribution block) | External Mean Well GST120A12 or equivalent; 12V 10A input |

### Wireless
| Interface | Status | Assignment | Notes |
|-----------|--------|------------|-------|
| WiFi/BT | INCLUDED | — | Dual-band card included in kit; available for future use (not required for dice tester core function) |

### Storage
| Interface | Status | Assignment | Notes |
|-----------|--------|------------|-------|
| NVMe M.2 | INCLUDED | Internal OS + working storage | 256 GB pre-installed; sufficient for 50–100 dice at 1000 samples each |
| Micro-SD | NOT INCLUDED | Optional external storage | Not required for current scope; consider if expanding beyond 100 dice |

## Summary

### Currently Assigned:
- **USB-A #1**: Pico (MCU servo control)
- **USB-A #2**: Camera (IMX296)
- **USB-A #3**: Display touch/power (USB-A to USB-C)
- **HDMI**: Display (Waveshare 10.1EP-CAPLCD)
- **DC Jack (12V)**: Main power from WUPP distribution block

### Still Available:
- **USB-A #4**: Expansion slot (external SSD, future sensors, etc.)
- **USB-C**: Reserved for development but can be repurposed if needed
- **WiFi/BT**: Available for network/wireless expansion

## Allocation Rules
- Do **not** use USB-C for regular peripherals unless absolutely necessary; keep for debug/development.
- If adding external storage, prefer USB 3.0 Type-A port #4 over USB-C.
- If adding additional sensors or cameras, check available USB-A ports and power budget from WUPP distribution block.
- If mounting display externally, use one combined HDMI + USB-C panel feedthrough (selected xiwai part) for display video and touch/power routing.
- **Always update this document** before adding new peripherals to avoid port conflicts.

## Notes
- The Jetson can draw up to ~10A from the 12V input under full load (GPU + all peripherals); the Mean Well GST120A12 (10A) is properly sized for this.
- USB power draw is minimal (Pico ~300 mA, camera ~500–800 mA) and well within Jetson's USB hub capacity.
- Camera uses USB bus power from Jetson USB-A #2; no separate fused 5 V/12 V branch is required for the camera.
- The servo power rail is isolated on the Pololu D24V50F5 buck and does not share the Jetson's USB power.
