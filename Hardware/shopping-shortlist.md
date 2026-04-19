# Shopping Shortlist (Cap-Tuned Under $1500)

Date: 2026-04-18
Goal: Option B+ build using Orin NX 16 GB-class compute with deterministic MCU PWM, global-shutter USB3 camera, and enclosure-ready lighting.

## Current Recommended Build Status
- Status: **Primary SBC purchase locked in** (Waveshare Jetson Orin NX 16GB Dev Kit, SKU 24222 at $1,175.99).
- Budget target: Original $1500 cap exceeded due to confirmed SBC cost; realistic total ~$1,650-$1,700 with reused peripherals.
- Architecture: SBC for vision/UI/storage + MCU for 333 Hz servo PWM.
- Storage target: 256 GB NVMe (included with kit); sufficient for 50-100 dice at 1,000 samples per die.
- Optics direction: folded optical path (mirror route) to reduce vertical constraints and make manual-focus lens sourcing easier.
- Camera decision: primary IMX296 USB3 camera locked for purchase.
- Display decision: Waveshare 10.1EP-CAPLCD locked as primary display; other display links remain backups.
- Power direction: prefer one external 12 V supply with internal distribution and 5 V buck rails where needed.

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
- Candidate SKU: Included with kit above for bring-up, but preferred final system architecture is one external 12 V main supply feeding internal rails.
- Qty: 1 (included)
- Price: Included in compute package ($0 additional)
- Notes: The Waveshare Orin IO base accepts 9-19 V on a 5.5 x 2.5 mm DC jack. For the cleaner enclosure build, use a single external 12 V main supply and distribute power internally.

3b. Main System Power (Preferred Clean Build)
- Selected SKU: EDGELIGHT LLC AD-EL-1201200-Z external desktop power supply, 12 V, 10 A, 120 W, 5.5 mm x 2.5 mm barrel connector
- Qty: 1
- Est. Price: check listing
- Notes: Selected for connector compatibility with the project 5.5 mm x 2.5 mm barrel requirement. Recommended as the single external supply for the whole system. Feed Jetson directly from 12 V input, run 12 V lighting directly if selected, and generate dedicated 5 V rails internally with buck converters.
- URL: https://www.digikey.com/en/products/detail/edgelight-llc/AD-EL-1201200-Z/18625578

4. Camera
- Candidate SKU (Primary): Arducam USB 3.0 IMX296 Global Shutter Camera, 1.58MP, bundled 6 mm CS lens
- Qty: 1
- Est. Price: ~$180.99
- Notes: UVC camera with manual controls and CS-mount manual-focus lens included. Strong fit for folded-path mirror geometry when total folded path is about 4.8-5.2 inches for 4 inch landing-area coverage with the included 6 mm lens. Confirm close-focus performance at the intended folded path during bring-up.
- Wiring path: camera is powered and connected by one USB 3 data cable to Jetson USB-A #2 (no separate power rail required).
- Camera cable check: verify included cable and camera-side connector type (often USB-C or USB 3 micro-B), and confirm length reaches the planned internal mount point.
- URL: https://www.amazon.com/Arducam-IMX296-Shutter-High-Speed-Windows/dp/B0DBV4CBDQ

4b. Camera (Backup)
- Candidate SKU: Arducam USB3 Global Shutter Camera, AR0234 sensor, M12-mount variant
- Qty: 1
- Est. Price: ~$169
- Notes: Keep as fallback if pricing/availability for the primary camera changes. M12 lens ecosystem remains viable but may require additional lens selection work under folded-path geometry.
- URL: https://www.arducam.com/arducam-2-3mp-ar0234-color-global-shutter-usb-3-0-camera-module.html

5. Lens
- Candidate SKU: M12 manual-focus lens in the 2.8-3.2 mm range
- Qty: 1
- Est. Price: $35
- Notes: Balanced-build default for a 3.5 inch landing circle is about 3 inches lens-to-surface distance. Target a lens around 2.8-3.2 mm for better lens availability and lower distortion than the 2.1 mm ultra-wide option. A 2.1 mm lens remains the compact-height fallback.

6. Polarization
- Candidate SKU: linear polarizer film for lens-side mount + linear polarizer sheet for light output
- Qty: 1 set
- Est. Price: $20
- Notes: Use cross-polarization to suppress acrylic glare. For an M12 lens, prefer a small rotatable linear polarizer film mount in front of the lens rather than a standard threaded circular camera filter.
- Selected camera-side filter: rotatable linear polarizer (Tiffen 52mm Linear Polarizer)
  - https://www.amazon.com/dp/B00004ZCAU/
  - Mounting plan: use a custom Fusion 360 adapter/cap so filter angle can be rotated during calibration, then mechanically locked after tuning.

6b. Folded-path mirror component
- Candidate SKU: first-surface mirror panel (front-surface), mounted at approximately 45 degrees
- Qty: 1
- Est. Price: $20-$80
- Notes: Avoid household rear-surface mirrors. Mechanical stiffness and stable mount angle are critical for repeatable framing.
- Selected nominal mirror size: approximately 4.5 in x 6.3 in first-surface mirror panel (160 x 115 x 3 mm listing)
- Selected mirror link: https://www.amazon.com/HHDLMTOYS-Reflector-Accessories-Reflectivity-160x115x3mm/dp/B0F8HFS58F/
- Sizing note: chosen from folded-path sizing with 4.5 in capture envelope; if alignment margin is tight, step up to 5 in x 7 in.
- Fit note: this selected mirror is slightly larger than the minimum calculation, which is preferred for easier alignment and edge clearance.

7. Motor Controller
- Candidate SKU: Raspberry Pi Pico 2 (RP2350)
- Qty: 1
- Est. Price: $8
- Notes: Dedicated PWM coprocessor at 333 Hz.

8. PWM Signal Stage
- Candidate SKU: Not required (direct 3.3 V PWM accepted by motor)
- Qty: 0
- Est. Price: $0
- Notes: Confirmed in-project that motor runs correctly from 3.3 V PWM signal.

9. Servo Power Rail
- Candidate SKU: Pololu D24V50F5, 5 V 5 A step-down regulator
- Qty: 1
- Est. Price: $25
- Notes: Keep servo on dedicated regulated 5 V rail; do not power from SBC header. Use this rail off the single 12 V main supply. Based on confirmed servo specs of about 220 mA running current and about 2.2 A stall current, a solid 5 A buck has comfortable margin for transient load and wiring losses.

9c. Auxiliary 5 V Rail (Deferred)
- Candidate SKU: Pololu D24V22F5 or similar 5 V 2.5 A step-down regulator
- Qty: 1 (deferred)
- Est. Price: $10-$15
- Notes: Deferred — Pico is USB-powered from Jetson USB-A #1 and display touch/power is USB-powered from Jetson USB-A #3, so a separate 5V rail has no current assignment. Order only if brownout issues appear on Pico or display during servo stall events during commissioning.

9b. Servo (In-Use Hardware Reference)
- Candidate SKU: HobbyPark Waterproof 35KG High Torque Digital Servo, 180 degree, HV programmable
- Qty: 1
- Est. Price: $29.97
- Notes: User-confirmed 5 V drive is sufficient in this project. Confirmed electrical figures from listing image: about 220 mA running current and about 2.2 A stall current.
- URL: https://www.amazon.com/dp/B0F2JCXWRX?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1

10. Power Distribution and Protection
- Candidate SKU: 5x20 mm inline fuse holder + automotive blade fuse block + terminal strip
- Qty: 1 set
- Est. Price: $15
- Notes: Add per-rail protection and serviceability. A 3 A to 4 A fuse is a sensible starting point for the dedicated servo branch if nuisance trips do not occur.

11. Display
- Candidate SKU: Waveshare 10.1EP-CAPLCD (1920x1200, capacitive touch)
- Qty: 1
- Est. Price: $99
- Notes: Locked as primary display choice. Uses HDMI for video and Type-C for touch/power path.

12. Input Devices
- Candidate SKU: Logitech MK270 keyboard/mouse combo (or existing devices)
- Qty: 1
- Est. Price: $0-$25
- Notes: Spare keyboard and mouse are on hand. Zero cost unless a new combo is preferred.

13. Lighting
- Candidate SKU: High-CRI LED bar strips, 5600 K class, dimmable, low-density profile, preferably 12 V type
- Qty: 2
- Est. Price: $70 total
- Notes: Prefer larger emitting area over high-intensity hotspot source. 12 V lighting integrates cleanly with the single external 12 V main supply.

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

16b. Enclosure Wall Panels
- Selected material: black ABS plastic sheet pack, 12 x 16 in, 10-pack
- Qty: 1 pack
- Est. Price: ~$50
- Notes: Selected as most cost-effective wall solution versus single large aluminum sheet. Opaque, easy to cut/drill, and modular for panelized enclosure walls.

17. Cables and Integration Materials
- Candidate SKU: USB3 cable (short, shielded), HDMI cable, ferrules, heat-shrink, fasteners
- Qty: 1 set
- Est. Price: $25
- Notes: Keep USB3 runs short and strain-relieved. HDMI display cable is on hand. Add selected DC barrel connector parts for custom 12 V cabling: Same Sky PJ-005B (female jack) and PP3-002B (male plug).

## Lens Shortlist (Balanced Build)

Primary goal: cover a 3.5 inch landing circle with roughly 2.7 to 3.3 inches lens-to-surface distance using the AR0234 M12 camera.

Current note:
- Because folded-path geometry is now preferred, final lens shortlist is pending camera mount finalization (stay M12 vs move to C/CS for sourcing ease).
- Keep this shortlist as a reference if staying with M12.

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
  - Motor control (MCU + power rail): $33
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

## Recommended Power Stack (Buy This Unless Better Local Pricing Appears)
1. Main PSU
- EDGELIGHT LLC AD-EL-1201200-Z, 12 V 10 A desktop brick, 5.5 mm x 2.5 mm barrel connector

2. Servo buck
- Pololu D24V50F5 (5 V, 5 A)

3. Aux buck
- Pololu D24V22F5 (5 V, 2.5 A)

Why this stack:
- Keeps one clean external 12 V source.
- Gives the Jetson direct 12 V input.
- Isolates servo transients from the display and Pico.
- Uses known, reputable regulator parts rather than anonymous buck boards.

## Shopping Links (Quick Reference)

### Compute
- Waveshare Jetson Orin NX 16GB Dev Kit (SKU 24222): https://www.waveshare.com/jetson-orin-nx-16g-dev-kit.htm?sku=24222

### Vision (Camera, Lens, Polarization)
- Camera (Primary): https://www.amazon.com/Arducam-IMX296-Shutter-High-Speed-Windows/dp/B0DBV4CBDQ
- Camera (Backup): https://www.arducam.com/arducam-2-3mp-ar0234-color-global-shutter-usb-3-0-camera-module.html
- Lens shortlist target: M12 manual-focus 2.8 mm first, 3.0 mm second, 3.2 mm third
- Polarizers: linear film/sheet for cross-polarization, with rotatable lens-side mount
  - Selected camera-side linear polarizer (rotatable): https://www.amazon.com/dp/B00004ZCAU/
  - Selected light-side polarizer sheet: https://www.amazon.com/dp/B0BS6FMZNL/
  - Polarizer sheet alternate: https://www.amazon.com/Selens-15-8x11-9in-Educational-Experiments-Non-Adhesive/dp/B0FSR6D15C/ref=sr_1_12?crid=384QB5TG5NPQU&dib=eyJ2IjoiMSJ9.24_bJwi3nNj09qVsHIKiDTleZ1dT_6VhufJWKKP7RVuGMYamcmYfHNojBG8gckNGlYl1DQlg9rRSc94MR8y5-bAJsAK5wk7wB9BNKga9InBfKEbEqTgbTpt4Zuw65ZZcdbRnsL_f0wrGpy6IC6Wf8qiZyJ8oXEhjdyxcgcRSSzPAlICNm8HDbBdLmBrEAeYayfVq5DDDaxhuswsBeazM1nOhX1bu6nSL_y2uBeuOBTDrlOt8Lk5-f1MRKIcnYsA8u88xGMucn78huWYyEOMZVK0TPOdl1Ua1pMn6phwMMgY.RwUosXxjdGqoU-mvKoYpjI1U_Q8Fhdd8IrXY3NAlJtY&dib_tag=se&keywords=polarizing+sheet&qid=1776547291&s=electronics&sprefix=polarizing+sheet%2Celectronics%2C141&sr=1-12
- Mirror (selected nominal size): approximately 4.5 in x 6.3 in first-surface mirror panel, approximately 45 degree mounting
- Mirror (selected link): https://www.amazon.com/HHDLMTOYS-Reflector-Accessories-Reflectivity-160x115x3mm/dp/B0F8HFS58F/
- Mirror fallback size: 5 in x 7 in first-surface mirror panel for extra alignment margin

### Motor Control
- MCU Board (selected): Raspberry Pi Pico 2 WH Basic Kit (used as PWM controller MCU)
  - https://www.amazon.com/Pico-WH-Basic-Kit-Microcontroller/dp/B0DCLF3QYB/ref=sr_1_1?dib=eyJ2IjoiMSJ9.N7n6fRFCwlZ-JESZaEy4tSSa3r2zYojtqcKlxb_NtHfaobIaIi-uNZVPBWtTaRBXw3IQ_eWl3-V-TvaHS000kaD5ReUFVNIMiyWCu3NCvAOFxczCqyOCmZNXeeTP7vxRubkAoI93QR3ABo7WnvXytXC1TQIzCKcFjfm7MjssNjuMYFnHVhH5qtUVLvcBdYHNlWOV_vn2-Sb8vm89sFDb8mcADd59f4VTxugRp2Yiw5o.DfrgEmZg_bOgr5ddflmcZIOEyDSVqEX3aUKYbSwTyAU&dib_tag=se&keywords=Raspberry%2BPi%2BPico%2B2&qid=1776548747&sr=8-1&th=1
- Signal Stage: Not required (direct 3.3 V PWM confirmed)
- Servo (current project hardware): HobbyPark Waterproof 35KG Digital Servo
  - https://www.amazon.com/dp/B0F2JCXWRX?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1
- Main system power (preferred): EDGELIGHT LLC AD-EL-1201200-Z 12 V 10 A external supply feeding internal buck rails
- Servo Power Supply: Pololu D24V50F5 (5 V, 5 A) step-down regulator
  - https://www.pololu.com/product/4892
- Auxiliary 5 V Supply: Pololu D24V22F5 (5 V, 2.5 A) or equivalent

## Jetson to Pico PWM Control Plan

Connection plan:
1. Jetson <-> Pico via USB cable (data + power for Pico logic)
2. Pico PWM output pin -> motor PWM input (direct 3.3 V logic)
3. Motor power from dedicated 5 V rail
4. Common ground shared between Pico and motor power rail

Recommended signal mapping:
- Pico PWM output: GP15 (or any hardware PWM-capable GPIO)
- PWM frequency: 333 Hz
- Control protocol: USB serial from Jetson to Pico

Suggested command interface:
- Jetson sends ASCII commands over USB serial, for example:
  - SET_US 1500
  - SET_US 1200
  - SET_US 1800
- Pico maps pulse width command to 333 Hz PWM output
- Pico returns ACK and current setting for logging/debug

Safety defaults:
- On Pico boot: set neutral/default pulse width
- On command timeout: return to safe default pulse width
- Clamp pulse width range to validated motor limits

### Display and Input
- Display (selected): Waveshare 10.1EP-CAPLCD (1920x1200, capacitive touch)
  - https://www.waveshare.com/10.1ep-caplcd.htm?sku=28881
- Display (budget backup): Waveshare 10.1DP-CAPLCD (1280x800, capacitive touch)
  - https://www.waveshare.com/10.1dp-caplcd.htm
- Display (secondary fallback): Hosyond 7-inch 1024x600 capacitive HDMI display
  - https://www.amazon.com/Hosyond-Display-1024%C3%97600-Capacitive-Raspberry/dp/B09XKC53NH/ref=sr_1_4?crid=9P679HBQGJSX&dib=eyJ2IjoiMSJ9.3PMO2XCtROfHo84ZcgeC4NXcAYlWQBqJlPNxu0IjI72ev0Yx0sZjc3puJjdbFN-Y9WcNBG1eMdLsjssz6HXncmLAGxXniSrKjVP9pMllnelVuDyCHFMqG9MohgZhxJnx5GcEvkAcpama_YfmDTfxKW3SqWbcaHuBd4meoj6Shirrt8gCBkqUtlPE5-6ANpAAYTdYQL_lwypSpbrUDl7qSJhksrWHgF0fvVWPGSE3lAesabVXtDQzUtmNP9CH-g_RIa9QUKJ2PwFLHsqjuZvUztim1UxJYSjpSHaXmR8SnT0.M3Ak8ize3u2sLKBbSiAvCLrixNZDvHG8Kc9FGGdRKb4&dib_tag=se&keywords=mini%2Bdisplay&qid=1776550537&s=electronics&sprefix=mini%2Bdisplay%2Celectronics%2C149&sr=1-4&th=1
- Display integration decision notes:
  - Option A (preferred for light control): touch glass and bezel external, display body internal, foam gasket around cutout to prevent light leaks.
  - Option B (external bracket): display fully external with a single combined HDMI + USB-C panel feedthrough.
  - I/O reservation for Option B: one HDMI path plus one USB path (Jetson USB-A to display USB-C cable), routed through the combined feedthrough.
  - Cable check status: HDMI cable for the monitor is on hand.
- Keyboard/Mouse: on-hand spare set confirmed.

### Lighting and Thermal
- Lighting architecture (recommended): 12 V high-CRI COB LED strips in aluminum channels with diffuser, 3-zone layout (left, right, top-fill)
- LED strips (selected spec target):
  - Type: 12 V COB strip, 5000 K (daylight), CRI 90+
  - Density: 320+ LEDs/m equivalent COB density
  - Target power: ~8-12 W per side zone, ~4-8 W top-fill (roughly 20-30 W total)
  - Notes: Prefer high-CRI COB over low-density SMD strips to reduce hotspots and improve texture consistency on dice faces.
- Selected LED strip: BTF-LIGHTING FCOB 12V 5000K, CRI 90+, 480 LEDs/m
  - https://www.amazon.com/BTF-LIGHTING-Flexible-Daylight-Dimmable-Controller/dp/B0FNMGVWVV/
- Mounting/channel (selected spec target):
  - Type: Aluminum U-channel with snap-on diffusers for thermal management and smoother output
  - Notes: Mount at shallow inward angles toward landing zone; avoid direct specular reflections into camera axis.
- Selected aluminum channel kit: Muzata U1SW aluminum channel with milky diffuser
  - https://www.amazon.com/Muzata-Aluminum-Extrusion-Diffuser-U1SW/dp/B01MXWL3X9/
  - Why selected: enclosed profile with snap-in diffuser and hardware ecosystem that is easy to cut and fixture for short enclosure segments.
- LED dimmer (selected spec target):
  - Type: 12 V PWM dimmer (knob-style) rated >=8 A
  - Usage: Inline between 12 V fused branch and lighting zones
  - Notes: Use one dimmer for all zones initially; split to per-zone dimming only if shadow balancing requires it.
- LED dimmer strategy (recommended):
  - Primary: digital-readout PWM dimmer so brightness can be restored to a documented value after accidental changes.
  - Fallback: software/app controlled single-color PWM controller with brightness memory.
- Selected LED dimmer: SuperlightingLED PWM LED dimmer controller with digital readout (12V/24V class)
  - https://www.amazon.com/SuperlightingLED-Controller-Digital-Flicker-Free-Aluminum/dp/B07B7GDLWM/
  - Usage note: record the final readout value in calibration notes so the level can be restored exactly if bumped.
- PWM frequency and exposure pairing (recommended for vision stability):
  - Goal: avoid visible brightness banding/flicker in captured frames.
  - Preferred controller behavior: PWM frequency >=20 kHz for best robustness at short exposures.
  - If PWM frequency is known and lower, use camera exposure long enough to average multiple PWM cycles.
  - Quick rule: exposure >= 2 / PWM_frequency (seconds) averages at least two full PWM periods.
  - Practical pairings:
    - 500 Hz PWM -> exposure >=4.0 ms
    - 1 kHz PWM -> exposure >=2.0 ms
    - 2 kHz PWM -> exposure >=1.0 ms
    - 4 kHz PWM -> exposure >=0.5 ms
    - 20 kHz PWM -> exposure >=0.1 ms
  - Setup flow:
    - Set a fixed PWM duty target (for example 35%-55%) and do not tune brightness by camera gain.
    - Lock exposure first, then lock gain, then fine-adjust PWM duty once.
    - Save these values as the capture preset and keep dimmer controls inaccessible during normal operation.
- Lighting electrical target:
  - Branch source: 12 V lighting branch from WUPP block
  - Fuse context: 5 A fuse currently available in selected kit
  - Design limit: keep steady-state lighting current <=3 A (about <=36 W at 12 V) for margin and thermal headroom
- Lighting product shortlist (direct links):
  - LED strip candidate A (alternate): YUNBO 12V COB 5000K, CRI 93+, 480 LEDs/m
    - https://www.amazon.com/YUNBO-Daylight-Brightness-Cuttable-Flexible/dp/B0BXNCVJ26/
  - LED strip candidate B (alternate, cooler CCT): VOEWT 12V COB 6000K, CRI 95Ra+
    - https://www.amazon.com/VOEWT-Daylight-Flexible-Bedroom-Included/dp/B0DHV85VCR/
  - LED strip candidate C: selected above
  - PWM dimmer candidate A: selected above (digital readout PWM)
  - PWM dimmer candidate B (software-controlled alternate): BTF-LIGHTING C01W monochrome PWM Tuya WiFi controller (12V/24V)
    - https://www.amazon.com/BTF-LIGHTING-FUT036W-Monochrome-Controller-Compatible/dp/B096VP2SMZ/
    - Why: app-based level control reduces accidental brightness drift, and scene/brightness state can be re-applied after setup.
  - PWM dimmer candidate C (software + RF remote alternate): PAUTIX RF WiFi smart remote dimmer for single-color strips (12V/24V)
    - https://www.amazon.com/PAUTIX-Remote-Dimmer-Wireless-Controller/dp/B0D5GRZ3PF/
    - Why: adds remote fallback while still allowing app-managed brightness memory.
  - PWM dimmer candidate D (lockable hardware alternate): Acegoo all-aluminum high-side dimmer, 6A upgrade
    - https://www.amazon.com/acegoo-Aluminum-High-Side-Perfect-6A-Upgrade/dp/B0DMSZZTSQ/
    - Why: robust panel-style hardware dimmer that is less likely to move accidentally than open inline knobs.
  - PWM dimmer candidate E (bench/economy backup): Hiletgo DC12V-24V 8A PWM dimmer controllers
    - https://www.amazon.com/Hiletgo-DC12-24V-Controller-compatible-LEDwholesaler/dp/B073R7H52B/
  - PWM dimmer candidate F (panel-style alternate): PWM LED Slide Dimmer 8A wall plate, 12V/24V DC
    - https://www.amazon.com/Slide-Dimmer-Switch-Wall-Plate/dp/B00FAAPHQW/
  - Aluminum channel candidate A: selected above (Muzata U1SW)
  - Aluminum channel candidate B (alternate): Muzata U-shape 10-pack 6.6ft with milky cover
    - https://www.amazon.com/Muzata-Aluminum-Channel-Mounting-Profile/dp/B074K1FKRM/
  - Aluminum channel candidate C (value alternate): hunhun U-shape 10-pack 6.6ft with milky cover
    - https://www.amazon.com/hunhun-Aluminum-Mounting-Installations-Installation/dp/B07F923CXW/
  - Aluminum channel candidate D (wider profile alternate): Muzata wider U102 10-pack 6.6ft with milky cover
    - https://www.amazon.com/Muzata-Aluminum-Extrusion-Diffuser-U102/dp/B07VQSJKQ1/
  - Selection guidance: choose one strip + one dimmer + one channel set first, then validate brightness and glare before buying extras.
- Enclosure Fan: 
- Selected light-side polarizer sheet:
  - https://www.amazon.com/dp/B0BS6FMZNL/
- Light-side polarizer sheet alternate:
  - https://www.amazon.com/Diffusion-Anti-Glare-Downlight-Spotlight-11-8x11-8x0-039in/dp/B0FHHL1RQZ/

### Integration Materials
- Cables and Hardware: 
- Selected DC barrel connector (female jack): Same Sky PJ-005B
  - https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/PJ-005B/172263
- Selected DC barrel connector (male plug): Same Sky PP3-002B
  - https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/PP3-002B/992137
- Selected wire (14 AWG stranded red): CNC Tech 3132-14-1-0100-004-1-TS
  - https://www.digikey.com/en/products/detail/cnc-tech/3132-14-1-0100-004-1-TS/22477320
- Selected wire (14 AWG stranded black): CNC Tech 3132-14-1-0100-001-1-TS
  - https://www.digikey.com/en/products/detail/cnc-tech/3132-14-1-0100-001-1-TS/22477336
- Selected wire (16 AWG stranded red): TE Connectivity/Raychem 55A0111-16-2
  - https://www.digikey.com/en/products/detail/te-connectivity-raychem-cable-protection/55A0111-16-2/5328786
- Selected wire (16 AWG stranded black): CNC Tech 3239-16-1-0500-001-1-TS
  - https://www.digikey.com/en/products/detail/cnc-tech/3239-16-1-0500-001-1-TS/9450103
- Selected wire (18 AWG stranded red): TE Connectivity/Raychem 55A0111-18-2
  - https://www.digikey.com/en/products/detail/te-connectivity-raychem-cable-protection/55A0111-18-2/2399820
- Selected wire (18 AWG stranded black): TE Connectivity/Raychem 55A0111-18-0
  - https://www.digikey.com/en/products/detail/te-connectivity-raychem-cable-protection/55A0111-18-0/2399856
- Wiring build note (for custom 12 V cable assembly):
  - Polarity: center pin is positive (+), outer sleeve is negative (-). Verify with a meter before first power-up.
  - Heat-shrink: use small tubing on each soldered terminal first, then one larger outer adhesive-lined sleeve over the rear cable exit for insulation and strain support.
  - Soldering: pre-tin wire and terminal, keep dwell time short to avoid softening connector insulation.
  - Strain relief: do not rely on solder joints or heat-shrink alone; secure the cable jacket to the enclosure with a clamp, zip-tie anchor, or cable gland near the connector.
  - Bring-up check: continuity check, polarity check, then run a loaded test for 20-30 minutes and confirm connector/wire temperature stays reasonable.
- Selected fused distribution block: WUPP 12 Volt 6-circuit fused block
  - https://www.amazon.com/Standard-Assortment-Automotive-Current-Ratings/dp/B0DNCJRX18/
  - Features: 6 circuits with integrated ATC/ATO blade fuses, LED indicators, waterproof damp-proof cover, 100A continuous rating
  - Usage: main fused distribution point fed from female barrel jack, routing to all branch rails (Jetson, servo buck, aux buck, lighting, secondary)
  - Note: WUPP block includes 5A fuses by default; replace with proper-rated fuses per circuit design (see fuse assortment below)
- Selected ATC/ATO fuse assortment: Standard Assortment Automotive Fuse Kit (2A, 3A, 5A, 10A)
  - https://www.amazon.com/Standard-Assortment-Automotive-Current-Ratings/dp/B0DNCJRX18/
  - Qty: 1 assortment pack
  - Contains: 2A (aux buck), 3A (Jetson + servo buck), 5A (main/fallback), 10A (main trunk input fuse)
  - Note: Replace included 5A fuses in WUPP block with these properly-rated fuses for per-branch protection
- Small breadboard (Pico/servo testing and prototyping)
  - https://www.digikey.com/en/products/detail/dfrobot/FIT0096/7597069
  - Type: DFRobot FIT0096 half-size breadboard (~400 tie-points)
  - Usage: Mount Pololu buck, route 5V power rail, PWM signal connections, servo wiring
  - Est. Price: $5-8
  - Notes: Enables non-destructive, reconfigurable servo control connections before final assembly
- USB micro-to-USB-A cable (Pico power + serial communication)
  - Length: 3 ft (allows flexible Pico placement near servo)
  - Usage: Connect Jetson USB-A #1 port to Pico for power delivery and serial control
  - Est. Price: $0 (on hand)
  - Notes: On-hand cable confirmed. Keep run short and well-shielded; consider ferrite clamps for EMI if servo causes signal noise.
- USB adapter (display touch/power path): female USB-C to male USB-A
  - https://www.amazon.com/biaze-Adapter-Transfer-Charging-Charger/dp/B0FF4Q5Z71/
  - Orientation required: USB-C receptacle to USB-A plug
  - Usage: Plug into Jetson USB-A #3, then connect USB-C cable from panel pass-through/display side
  - Est. Price: $5-10
  - Notes: Selected part. Choose/use as data-capable adapter (not charge-only).
- Camera USB 3 cable (Jetson USB-A to camera)
  - Length target: 2-3 ft for internal camera mount
  - Usage: Camera power + data to Jetson USB-A #2
  - Est. Price: $0 (on hand)
  - Notes: On-hand cable confirmed.
- Optional fallback cable: USB-A to USB-C data cable
  - Length target: 3 ft
  - Usage: Alternate direct path Jetson USB-A #3 to display USB-C if adapter approach is not used
  - Est. Price: $6-12
- Jumper wire assortment (breadboard connections)
  - Type: 22 AWG male-to-male jumper wires in assorted lengths
  - Est. Price: $8-12
  - Usage: Breadboard power rails, signal routing, prototyping connections
  - Notes: Also useful for servo header-to-breadboard connections with male-to-male pin housings
- Selected external display pass-through (single combined HDMI + USB-C)
  - https://www.amazon.com/xiwai-Waterproof-Dustproof-Type-C-Extension/dp/B0C8SWHHY5/
  - Usage: one front-panel module for display video (HDMI) and display touch/power (USB-C)
  - Note: preferred for Option B external display bracket to reduce panel cutouts and simplify routing
- Fallback USB bulkhead feedthrough set (if moving to separate pass-throughs)
  - https://www.amazon.com/PENGLIN-Connector-Feedthrough-Bulkhead-Industrial/dp/B0F25V78HC/
- Selected acrylic board (translucent white): Lesnlok translucent white plexiglass sheet
  - https://www.amazon.com/Lesnlok-Translucent-Plexiglass-Transmittance73-Decoration/dp/B0G4JJSFCS/
  - Integration note: with milky LED channel covers already selected, this adds additional diffusion and may require higher PWM duty or longer exposure.
- Acrylic board alternate (clear support panel): SimbaLux clear acrylic sheet
  - https://www.amazon.com/SimbaLux-Plexiglass-Transparent-Protective-Projects/dp/B084T6SXJ6/
- Selected enclosure wall sheet pack (black ABS, 12 x 16 in, 10-pack):
  - https://www.amazon.com/gp/aw/d/B0D3DHC2PV/
