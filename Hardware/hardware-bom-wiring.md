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
- Level/buffer stage if needed: $10-$20
- Dedicated 5 V servo supply: $30-$45
- Fuse/distribution/wiring parts: $20-$35
Subtotal: $68-$115

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

## Power and Wiring Architecture

### Topology
- SBC and servo use separate power rails.
- MCU is a motion coprocessor connected to SBC over USB/UART.
- All grounds are tied at one star-point distribution location.

### Rails
- Rail A (Compute): per Orin kit spec (often 12-19 V input).
- Rail B (Servo): regulated 5 V rail sized for stall current margin.
- Rail C (Lighting): as required by LED driver (often 12 V).

### Connections
- Camera -> SBC via USB3.
- Display -> SBC via HDMI.
- Keyboard/mouse -> SBC via USB.
- SBC <-> MCU via USB serial.
- MCU PWM -> signal conditioning (if needed) -> servo signal input.
- Servo power -> dedicated 5 V rail (not SBC 5 V pin).

### ASCII Wiring Diagram

[AC Mains]
   |
   +--> [PSU A: SBC] ---------> [Orin NX Carrier + Module] ---- HDMI ---> [Display]
   |                                   |    |    |
   |                                   |    |    +-- USB --> [Keyboard/Mouse]
   |                                   |    +------- USB3 -> [Global Shutter Camera]
   |                                   +------------ USB --> [MCU]
   |
   +--> [PSU B: 5V Servo Rail] -> [Fuse] -> [Servo V+]
   |                                         [Servo GND] ---+
   |
   +--> [PSU C: Lighting Rail] -> [LED Driver/Dimmer] -> [LED Bars/Panels]

[MCU PWM Pin] -> [Level/Buffer Stage if required] -> [Servo Signal]

Common Ground Star Point:
- SBC GND
- MCU GND
- Servo PSU GND
- Servo GND
- Lighting PSU GND (if shared reference needed)

## Control Split
- SBC handles camera, inference, UI, DB, and storage.
- MCU handles deterministic 333 Hz PWM and future limit-switch/encoder processing.

## Thermal Notes
- Keep LEDs thermally separated from SBC/camera volume.
- Prefer larger low-power-density lighting over small hot emitters.
- Use at least one forced exhaust path plus passive intake path.
