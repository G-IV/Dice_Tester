# Hardware BOM + Wiring (Option B+ Orin NX 16 GB Class)

Date: 2026-04-18
Context: Dice-testing system with camera capture, YOLO inference, UI, database, and 333 Hz servo control.

## Assumptions
- Compute target is Orin NX 16 GB-class capability (official or third-party kit).
- Servo control is offloaded to MCU for deterministic 333 Hz PWM.
- Camera path starts with USB3 UVC for easiest OpenCV integration.
- Enclosure is light-controlled and uses cross-polarization.

## Variant 1: Cost-Controlled B+ (target about $1250-$1350)

### Cost Blocks
1. Compute core
- Orin NX 16 GB-class kit/carrier: $650-$760
- NVMe 500 GB to 1 TB: $45-$80
- SBC PSU: $35-$55
Subtotal: $730-$895

2. Vision
- USB3 global-shutter camera (starter industrial tier): $140-$190
- Manual-focus lens (wide to wide-normal): $45-$70
- Polarizer(s): $20-$35
Subtotal: $205-$295

3. Motion control
- RP2040 board: $8-$15
- Level/buffer stage: not required (direct 3.3 V PWM confirmed)
- Dedicated 5 V servo supply: $30-$45
- Fuse/distribution/wiring parts: $20-$35
Subtotal: $58-$95

4. UI and peripherals
- 10.1 inch HDMI non-touch display: $90-$130
- Keyboard/mouse (reuse if possible): $0-$35
Subtotal: $90-$165

5. Lighting/thermal/integration
- High-CRI dimmable LED setup: $60-$95
- Enclosure fans + airflow hardware: $20-$35
- Cables, mounts, misc hardware: $35-$55
Subtotal: $115-$185

Estimated System Total: about $1208-$1655 before optimization.
Practical optimized target for this variant: about $1250-$1350 (requires lower-end of compute/camera ranges and reuse of some peripherals).

## Variant 2: Performance-Forward B+ (target about $1450-$1550)

### Cost Blocks
1. Compute core
- Better-validated Orin NX 16 GB-class kit/carrier: $760-$900
- 1 TB higher-endurance NVMe: $80-$110
- Higher-margin PSU: $45-$70
Subtotal: $885-$1080

2. Vision
- Better USB3 global-shutter camera: $200-$280
- Two-lens strategy (one wider + one lower-distortion): $80-$130
- Polarizer pair + mounts: $30-$50
Subtotal: $310-$460

3. Motion control
- RP2040/STM32 board + robust IO staging: $20-$45
- Dedicated servo 5 V supply + protection/distribution: $60-$95
Subtotal: $80-$140

4. UI and peripherals
- 11.6-13.3 inch HDMI non-touch display: $120-$180
- Keyboard/mouse: $20-$40
Subtotal: $140-$220

5. Lighting/thermal/integration
- Higher-quality high-CRI dimmable lighting: $90-$140
- Improved fans/ducting/filter path: $30-$50
- Cables/mounts/misc: $45-$70
Subtotal: $165-$260

Estimated System Total: about $1580-$2160 before optimization.
Cap-tuned target for this variant: about $1450-$1550 by selecting lower-mid camera/display choices and avoiding premium carrier options.

## Practical Recommendation
- If hard cap is $1500, run a cap-tuned Variant 2 or a strong Variant 1.
- The largest cost lever is module+carrier pricing.
- Keep MCU split regardless of variant for deterministic 333 Hz PWM and future expansion.
- Recommended power stack for the current build:
   - main external supply: 12 V 10 A desktop brick, Mean Well GST120A12 class
   - dedicated servo buck: Pololu D24V50F5 (5 V, 5 A)
   - auxiliary 5 V buck: Pololu D24V22F5 (5 V, 2.5 A)

## Power and Wiring Architecture

### Topology
- SBC and servo use separate power rails.
- MCU is a motion coprocessor connected to SBC over USB/UART.
- All grounds are tied at one star-point distribution location.
- Preferred clean-build strategy: one external 12 V main supply, with internal rail generation/distribution.

### Rails
- Rail A (Compute): 12 V main input direct to Waveshare Orin IO base DC jack. The base board accepts 9-19 V on 5.5 x 2.5 mm barrel input.
- Rail B (Servo): dedicated regulated 5 V rail for the selected HobbyPark 35KG servo. Confirmed servo figures are about 220 mA running and about 2.2 A stall at 5 V, so a 5 V buck in the 5 A class is a practical choice with margin.
- Rail C (Lighting): preferably 12 V lighting rail direct from the main supply.
- Rail D (Display/logic auxiliaries): regulated 5 V rail for display touch/power path and small accessories if needed.

### Connections
- Camera -> SBC via USB3.
- Display -> SBC via HDMI.
- Display touch/power -> 5 V auxiliary rail and/or USB connection as required by display wiring.
- Keyboard/mouse -> SBC via USB.
- SBC <-> MCU via USB serial.
- MCU PWM -> servo signal input (direct 3.3 V logic confirmed).
- Servo power -> dedicated 5 V rail (not SBC 5 V pin).

### ASCII Wiring Diagram

[AC Mains]
   |
   +--> [12V Main PSU] --------> [Fuse/Distribution]
                                     |         |         |
                                     |         |         +--> [12V Lighting Rail] -> [LED Driver/Dimmer] -> [LED Bars/Panels]
                                     |         |
                                     |         +--> [5V Buck: Servo Rail] -> [Fuse] -> [Servo V+]
                                     |                                      [Servo GND] ---+
                                     |
                                     +--> [Orin NX Carrier + Module] ---- HDMI ---> [Display]
                                                   |    |    |                 |
                                                   |    |    |                 +--> [5V Aux Rail / USB as required]
                                                   |    |    +-- USB --> [Keyboard/Mouse]
                                                   |    +------- USB3 -> [Global Shutter Camera]
                                                   +------------ USB --> [MCU]

[5V Aux Buck] ----------------------------------------------> [Display touch/power path if needed]

[MCU PWM Pin] ------------------------------------> [Servo Signal]

Common Ground Star Point:
- SBC GND
- MCU GND
- Servo PSU GND
- Servo GND
- Lighting PSU GND (if shared reference needed)

### Servo Branch Sizing Note
- Servo model in use: HobbyPark waterproof 35KG digital servo.
- Confirmed current figures: about 220 mA running, about 2.2 A stall.
- Recommended branch sizing:
   - 5 V servo buck: 5 A class
   - Servo branch fuse: start around 3 A to 4 A and validate against startup/stall behavior in the real mechanism
   - Wiring: use enough copper cross-section to avoid voltage sag during stall events

### Wire Gauge and Fuse Plan

**Trunk (PSU to Distribution Block)**
- Wire gauge: 14 AWG (recommended for main 12 V path carrying all system current).
- Connectors: Same Sky PP3-002B (male plug on PSU side) to Same Sky PJ-005B (female jack on distribution side) via custom soldered/heat-shrunk assembly.
- Fuse: main distribution fuse, typically 10-12 A automotive blade or 5x20 mm inline cartridge. Start at the PSU/distribution block entry.

**Branch 1: Distribution Block to Jetson (12 V input)**
- Wire gauge: 16 AWG.
- Expected current: ~2 A sustained (Jetson alone at typical load).
- Fuse: 3 A automotive blade or 5x20 mm cartridge fuse.
- Location: at the distribution block, before Jetson lead.

**Branch 2: Distribution Block to Servo 5 V Buck Input (12 V)**
- Wire gauge: 16 AWG (conservative for potential transient swings).
- Expected current: ~1.5 A sustained (servo 220 mA + buck overhead).
- Fuse: 3 A automotive blade or 5x20 mm cartridge fuse.
- Location: at the distribution block, before servo buck input lead.

**Branch 3: Distribution Block to Auxiliary 5 V Buck Input (12 V)**
- Wire gauge: 16 AWG.
- Expected current: ~0.5-0.8 A sustained (display touch/power, Pico logic, small accessories).
- Fuse: 1-2 A automotive blade or 5x20 mm cartridge fuse.
- Location: at the distribution block, before aux buck input lead.

**Branch 4: Distribution Block to Lighting (12 V)**
- Wire gauge: 16 AWG (typical for dimmable LED current).
- Expected current: ~2-3 A sustained (depends on LED wattage; estimate 24-36 W).
- Fuse: 4 A automotive blade or 5x20 mm cartridge fuse.
- Location: at the distribution block, before lighting/dimmer control lead.

**Branch 5: Secondary Branches from Distribution Block (Display, Keyboard, Misc)**
- Wire gauge: 18 AWG (low-current auxiliary lines).
- Fuse: 1-2 A fuses if these branches carry any power; data-only lines (HDMI, USB) do not require fusing.
- Location: at the distribution block.

**Notes**
- All fuses should be rated for 12 V DC operation (5x20 mm cartridge fuses or ATO automotive blade fuses).
- Use a fuse block with clear labeling so each branch is individually protected.
- If a branch draws unexpectedly high current or nuisance-trips a fuse, investigate and re-fuse accordingly (do not just upsize fuse without understanding the cause).
- Servo brake branch is the highest-inrush risk; 3-4 A fuse may be aggressive on startup. Monitor on bring-up and be prepared to adjust.

### Preferred Power Parts
- Main external supply: Mean Well GST120A12 class 12 V 10 A desktop power supply
- Servo rail regulator: Pololu D24V50F5
- Auxiliary 5 V regulator: Pololu D24V22F5

Implementation note:
- Check barrel-plug compatibility at final purchase. The Waveshare Orin IO base uses a 5.5 x 2.5 mm DC jack, so the chosen 12 V brick either needs the correct plug natively or a clean adapter lead.

## Control Split
- SBC handles camera, inference, UI, DB, and storage.
- MCU handles deterministic 333 Hz PWM and future limit-switch/encoder processing.

### Suggested PWM Interface Contract
- PWM frequency: 333 Hz
- Transport: USB serial between SBC and MCU
- Suggested command format:
   - SET_US <pulse_width_microseconds>
- MCU behavior:
   - apply clamped pulse widths only
   - acknowledge command with current applied value
   - fall back to safe default on timeout or parse error

## Thermal Notes
- Keep LEDs thermally separated from SBC/camera volume.
- Prefer larger low-power-density lighting over small hot emitters.
- Use at least one forced exhaust path plus passive intake path.
