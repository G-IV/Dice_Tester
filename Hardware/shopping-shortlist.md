# Shopping Shortlist (Cap-Tuned Under $1500)

Date: 2026-04-18
Goal: Option B+ build using Orin NX 16 GB-class compute with deterministic MCU PWM, global-shutter USB3 camera, and enclosure-ready lighting.

## Current Recommended Build Status
- Status: **Primary SBC purchase locked in** (Waveshare Jetson Orin NX 16GB Dev Kit, SKU 24222 at $1,175.99).
- Budget target: Original $1500 cap exceeded due to confirmed SBC cost; realistic total ~$1,650-$1,700 with reused peripherals.
- Architecture: SBC for vision/UI/storage + MCU for 333 Hz servo PWM.
- Storage target: 256 GB NVMe (included with kit); sufficient for 50-100 dice at 1,000 samples per die.

## Cap-Tuned Shopping List (Primary Candidates)

1. Compute
- Candidate SKU: Waveshare Jetson Orin NX AI Development Kit, 16 GB module, SKU 24222 (JETSON-ORIN-NX-16G-DEV-KIT)
- Qty: 1
- Price: $1,175.99 (confirmed)
- Includes: 256 GB NVMe SSD, cooling fan, dual-band WiFi/BT card, power supply, cables
- Notes: JetPack support confirmed in wiki; see Waveshare wiki for flashing guide.

2. Storage
- Candidate SKU: Included with kit above (256 GB).
- Qty: 1 (included)
- Price: Included in compute package ($0 additional)
- Notes: 256 GB is sufficient for current workflow (50-100 dice at 1000 samples each). Plan external USB SSD (~$60-$90 for 1 TB) if expanding beyond current scope or for active offload/archiving.

3. SBC Power
- Candidate SKU: Included with kit above.
- Qty: 1 (included)
- Price: Included in compute package ($0 additional)
- Notes: Power adapter included in Waveshare kit.

4. Camera
- Candidate SKU: Arducam USB3 Global Shutter Camera, AR0234 sensor, M12-mount variant
- Qty: 1
- Est. Price: $169
- Notes: Confirm UVC mode and manual exposure/gain/white-balance controls. Current assumption is M12 lens mount, not C/CS. Balanced-build target is approximately 3 inches standoff.

5. Lens
- Candidate SKU: M12 manual-focus lens in the 2.8-3.2 mm range
- Qty: 1
- Est. Price: $35
- Notes: Balanced-build default for a 3.5 inch landing circle is about 3 inches lens-to-surface distance. Target a lens around 2.8-3.2 mm for better lens availability and lower distortion than the 2.1 mm ultra-wide option. A 2.1 mm lens remains the compact-height fallback.

6. Polarization
- Candidate SKU: 52 mm circular polarizer for lens + linear polarizer sheet for light output
- Qty: 1 set
- Est. Price: $20
- Notes: Use cross-polarization to suppress specular glare.

7. Motor Controller
- Candidate SKU: Raspberry Pi Pico 2 (RP2350)
- Qty: 1
- Est. Price: $8
- Notes: Dedicated PWM coprocessor at 333 Hz.

8. PWM Signal Stage
- Candidate SKU: SN74AHCT125 buffer breakout (3.3 V in, 5 V logic out)
- Qty: 1
- Est. Price: $8
- Notes: Use only if servo signal input requires stronger 5 V logic threshold.

9. Servo Power Rail
- Candidate SKU: Mean Well LRS-50-5 (5 V, 10 A)
- Qty: 1
- Est. Price: $25
- Notes: Keep servo on dedicated rail; do not power from SBC header.

10. Power Distribution and Protection
- Candidate SKU: 5x20 mm inline fuse holder + automotive blade fuse block + terminal strip
- Qty: 1 set
- Est. Price: $15
- Notes: Add per-rail protection and serviceability.

11. Display
- Candidate SKU: Waveshare 10.1 inch HDMI IPS non-touch display (non-touch model)
- Qty: 1
- Est. Price: $99
- Notes: Check brightness, viewing angle, and mounting tabs.

12. Input Devices
- Candidate SKU: Logitech MK270 keyboard/mouse combo (or existing devices)
- Qty: 1
- Est. Price: $0-$25
- Notes: Zero cost if reusing existing peripherals.

13. Lighting
- Candidate SKU: High-CRI LED bar strips, 5600 K class, dimmable, low-density profile
- Qty: 2
- Est. Price: $70 total
- Notes: Prefer larger emitting area over high-intensity hotspot source.

14. LED Control
- Candidate SKU: PWM dimmer, 12 V/24 V compatible
- Qty: 1
- Est. Price: $10
- Notes: Keep brightness tunable for repeatable camera settings.

15. Diffusion and Mounting
- Candidate SKU: Opal acrylic diffuser sheet plus standoffs/mount clips
- Qty: 1 set
- Est. Price: $15
- Notes: Improves uniformity and reduces glare.

16. Enclosure Airflow
- Candidate SKU: Noctua NF-A8 5V PWM fan (or equivalent low-noise fan)
- Qty: 1-2
- Est. Price: $18
- Notes: One exhaust minimum; add filtered intake path.

17. Cables and Integration Materials
- Candidate SKU: USB3 cable (short, shielded), HDMI cable, ferrules, heat-shrink, fasteners
- Qty: 1 set
- Est. Price: $25
- Notes: Keep USB3 runs short and strain-relieved.

## Lens Shortlist (Balanced Build)

Primary goal: cover a 3.5 inch landing circle with roughly 2.7 to 3.3 inches lens-to-surface distance using the AR0234 M12 camera.

Priority order:

1. First-choice lens class
- M12 manual-focus lens, 2.8 mm focal length
- Sensor coverage: rated for 1/2.7 inch or larger preferred
- Aperture target: around F2.0 to F2.8
- Focus requirement: close focus to about 70-80 mm or better
- Why: best balance of compact build, lens availability, and moderate distortion

2. Second-choice lens class
- M12 manual-focus lens, 3.0 mm focal length
- Sensor coverage: rated for 1/2.7 inch or larger preferred
- Aperture target: around F2.0 to F2.8
- Focus requirement: close focus to about 75-90 mm or better
- Why: very similar to 2.8 mm, slightly cleaner geometry if you can tolerate a little more height

3. Third-choice lens class
- M12 manual-focus lens, 3.2 mm focal length
- Sensor coverage: rated for 1/2.7 inch or larger preferred
- Aperture target: around F2.0 to F2.8
- Focus requirement: close focus to about 80-95 mm or better
- Why: useful if your actual mounted standoff ends up just above 3 inches

Fallback options:
- 2.1 mm M12 manual-focus: use only if enclosure height becomes the dominant constraint
- 4.0 mm M12 manual-focus: use only if you later accept a taller build for cleaner geometry

What to look for in listings:
- M12 x 0.5 mount
- Manual focus, not fixed focus
- Compatible with 1/2.7 inch or larger sensor format
- Low distortion or board-camera lens intended for machine vision preferred
- Visible-light / color use support
- Mechanical lock ring preferred so focus does not drift

Avoid if possible:
- Lenses only rated for smaller sensors if they show corner shading on AR0234
- Fixed-focus mobile-style lenses
- Listings that omit close-focus distance entirely
- Extremely wide fisheye-style M12 lenses unless compact height becomes more important than geometry

## Cost Summary (With Confirmed SBC)
- Core system (Waveshare Orin NX 16GB kit + all listed peripherals except optional input devices):
  - Subtotal without contingency: about $1666 (reusing existing keyboard/mouse, no extras)
  - Subtotal without contingency: about $1691 (new keyboard/mouse combo)
  - Contingency reserve (about 10 percent): about $167 to $169
  - Total with contingency: about $1833 to $1860

- Breakdown:
  - Waveshare Compute Kit (SBC + 256GB SSD + PSU): $1,175.99
  - Camera + lens + polarizers: $224
  - Motor control (MCU + signal stage + power rail): $41
  - Display + input devices (if purchased): $99 to $124
  - Lighting + thermal + integration: $118 to $143

Result: Original $1500 cap is exceeded due to actual SBC cost, but the Waveshare kit at $1,175.99 is a solid foundation. Remaining peripherals (~$490-$520) are flexible; reuse existing input devices and optimize lighting/thermal choices to bring total closer to $1,650-$1,700.

## Storage Sizing Rationale (256 GB Included)
- 256 GB is the baseline, included with your Waveshare kit.
- Rough planning model:
  - OS + tools + models + logs: about 40-80 GB
  - Database and metadata: about 5-20 GB
  - Remaining working space on 256 GB drive: often about 150-190 GB usable headroom
- For 50-100 dice at 1,000 samples each:
  - At ~230 KB per image: 50 dice = ~11.5 GB images, 100 dice = ~23 GB images
  - This leaves ample room on 256 GB for OS, tools, and active work.
- Plan: Use built-in 256 GB for active work and DB. If capturing beyond 100 dice or needing to keep all images on-device, add an external USB SSD (~$60-$90 for 1 TB).

## Optional Upgrades (Add Later)
- Second lens (2.1 mm ultra-wide or 4.0 mm lower-distortion option) for depth tradeoff testing: +$20 to +$60
- Better industrial USB3 camera tier: +$60 to +$120
- 11.6 to 13.3 inch non-touch display: +$30 to +$80

## Pre-Purchase Validation Checklist
1. Confirm exact Orin module included is 16 GB, not 8 GB.
2. Confirm JetPack version support and flashing workflow from vendor.
3. Confirm camera exposes manual controls under Linux UVC.
4. Confirm display is non-touch HDMI model and mounting dimensions.
5. Confirm servo control signal threshold before finalizing buffer stage.
6. Confirm total power draw and connector compatibility across all rails.

## Shopping Links (Quick Reference)

### Compute
- Waveshare Jetson Orin NX 16GB Dev Kit (SKU 24222): https://www.waveshare.com/jetson-orin-nx-16g-dev-kit.htm?sku=24222

### Vision (Camera, Lens, Polarization)
- Camera: 
- Lens shortlist target: M12 manual-focus 2.8 mm first, 3.0 mm second, 3.2 mm third
- Polarizers: 

### Motor Control
- MCU Board: 
- Signal Stage: 
- Servo Power Supply: 

### Display and Input
- Display: 
- Keyboard/Mouse: 

### Lighting and Thermal
- LED Strips: 
- LED Dimmer: 
- Enclosure Fan: 

### Integration Materials
- Cables and Hardware: 
