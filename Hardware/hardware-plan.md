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

## Polarization Layout For Camera-Under-Acrylic Setup
- Camera is mounted below the acrylic cap, looking upward at the resting die.
- Main glare source is reflection from external light on the acrylic cap.
- Use one polarizer on the imaging path and one on the illumination path; do not stack both near the camera.

Recommended optical layout:

Imaging path, bottom to top:
1. Camera lens
2. Rotatable linear polarizer in front of the lens
3. Enclosed air gap
4. Clear acrylic cap
5. Die resting on acrylic

Lighting path, from light to scene:
1. LED source
2. Diffuser
3. Linear polarizer sheet on the light output
4. Light enters chamber from side or upper angle
5. Acrylic and die scene

Setup guidance:
- Keep the lighting-side polarizer fixed.
- Rotate the lens-side polarizer to minimize specular reflections from the acrylic.
- Side lighting is preferred over direct axial lighting for this geometry.
- Linear polarizer film is preferred over circular polarizers for the machine-vision setup.

## Folded Optical Path Decision (Mirror Route)
- Adopt folded optical path to reduce vertical tower requirements and improve mechanical stability.
- Camera can be mounted horizontally and view the underside scene via an angled mirror.
- Use a first-surface mirror (front-surface), not a household rear-surface mirror, to avoid ghosting/double images.
- Mount mirror near 45 degrees and lock the bracket to prevent framing drift.
- Treat focus distance as folded path length: camera-to-mirror plus mirror-to-scene.
- Re-tune cross-polarization angles after mirror installation.
- Image may need software flip correction depending on mirror orientation.

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
