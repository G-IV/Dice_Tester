# Hardware Plan

## Project Context
- Dice-testing system with camera capture, YOLO inference, and motor control.
- Current motor PWM is generated via Analog Discovery 2 as a temporary convenience.
- Long-term preference is direct SBC pin control or a tiny dedicated PWM device.
- Goal: avoid outgrowing hardware; price is secondary.

## Recommended Architecture
- Compute: high-end Jetson-class SBC, AGX Orin class preferred for long-term headroom.
- Motor/PWM: dedicated microcontroller (RP2040/STM32/Arduino-class) for deterministic PWM if SBC PWM is limiting.
- Storage: SSD/NVMe preferred.
- Cooling: active cooling for sustained inference workloads.

## Camera Guidance
- Prefer dedicated global-shutter camera over consumer webcam.
- Target: 1080p at 60 fps, with manual exposure/gain/white balance control.
- Interface: USB3 UVC first for easiest OpenCV integration; CSI later only if needed.
- Under $250 starters: ELP/Arducam global-shutter USB options; watch used industrial cameras for upgrades.

## Imaging Quality Strategy
- Use diffuse lighting with cross-polarization to suppress reflections.
- Lock exposure, gain, and white balance for repeatable color performance.

## Continuation Note
- Resume from this hardware baseline before selecting exact SKU stack and wiring split (SBC PWM vs MCU PWM).

## Updated Requirements (2026-04-18)
- Servo requirement: 5V PWM at 333 Hz for position control.
- Camera must support manual focus control and short working distance; wide-angle lens preferred to reduce enclosure depth.
- SBC needs: video out, keyboard/mouse input, camera input, and support for a more user-friendly UI.
- Storage should handle DB plus video/image capture; external storage is acceptable for cost optimization.
- Display target: approximately tablet-sized (around iPad size), non-touch preferred unless touch is significantly cheaper.
- Lighting must be safe in enclosed space with low heat generation.
- Polarization plan: cross-polarization using one polarizer on light path and one on camera lens.
- Budget target: around $500 preferred, hard cap $1500.
- Open to distributed architecture (e.g., separate controller for motor/PWM, smart camera offload) if it improves value or scalability.

## Candidate Build Direction: Option B+ (Orin NX 16 GB Class)
- Keep the balanced architecture, but raise compute tier to Orin NX 16 GB-class module for additional memory headroom.
- Maintain dedicated MCU for deterministic 333 Hz PWM and future I/O expansion.
- Prefer USB3 global-shutter camera with C/CS lens ecosystem.
- Keep 1 TB NVMe, non-touch HDMI display, dimmable high-CRI lighting, and active thermal management.
- Expected system budget range likely shifts upward vs original Option B, often around upper end of prior range or slightly above depending on camera and display choices.
