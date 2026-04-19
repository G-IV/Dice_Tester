# First-Pass Enclosure Footprint Estimate

Date: 2026-04-18
Purpose: Size the capture chamber and overall enclosure based on lens focal length and required working distance.

## Inputs and Assumptions
- Target landing area at capture plane:
  - Circular landing zone diameter: 3.5 in (88.9 mm)
  - Goal: fit the full circle inside frame while minimizing lens-to-surface distance
- Sensor assumption for AR0234:
  - Effective sensor width: 5.76 mm
  - Effective sensor height: 3.60 mm
- Candidate M12 lens focal lengths:
  - 2.1 mm (compact-height option)
  - 2.8 mm (balanced-build option)
  - 3.2 mm (balanced to lower-distortion option)
  - 4.0 mm (taller but cleaner geometry)
- Added depth overhead between lens front and enclosure front/back structures:
  - Camera body + mount stack: 35 mm
  - Lighting and diffuser clearance near view path: 40 mm
  - Mechanical margin for service and cable bend radius: 30 mm
  - Total fixed overhead: 105 mm

## Working Distance Estimate Method
Working distance approximation:
- WD = (Object Size x Focal Length) / Sensor Dimension

For a circular landing target, vertical coverage is the limiting dimension because the sensor is wider than it is tall.

Using object height 88.9 mm and sensor height 3.60 mm:
- 2.1 mm lens: WD about 52 mm
- 2.8 mm lens: WD about 69 mm
- 3.2 mm lens: WD about 79 mm
- 4.0 mm lens: WD about 99 mm

Interpretation:
- Your minimum allowed distance is 2.0 in (50.8 mm).
- A 2.1 mm lens lands almost exactly on that minimum distance.
- A 2.8 mm lens lands around 2.7 in and is a strong balanced choice.
- A 3.2 mm lens lands around 3.1 in and is also a strong balanced choice with slightly lower distortion.
- A 4.0 mm lens lands around 3.9 in and is the taller, cleaner-geometry option.

## Capture Chamber Depth Estimate
Capture chamber depth (camera to capture plane plus fixed overhead):
- 2.1 mm lens: 52 + 105 = about 157 mm
- 2.8 mm lens: 69 + 105 = about 174 mm
- 3.2 mm lens: 79 + 105 = about 184 mm
- 4.0 mm lens: 99 + 105 = about 204 mm

Recommended design target:
- Build around a 2.8-3.2 mm M12 lens first.
- Practical capture chamber depth target: 180 to 210 mm before adding extra margin for light baffling or service space.

## Capture Chamber Width and Height Estimate
Use framing area plus wall, lighting, and tolerance margins:
- Width: 89 mm target area + 2 x 60 mm side margin = about 209 mm
- Height: 89 mm target area + top/bottom margin about 80 mm = about 169 mm

Recommended internal capture chamber envelope:
- Width: 220 to 280 mm
- Height: 180 to 240 mm
- Depth: 160 to 220 mm

## Full Enclosure First-Pass Estimate
Add compute and wiring zone adjacent or below chamber:
- SBC + PSU + MCU + fuse/distribution zone: about 180 mm x 220 mm footprint
- Cable/fan service margin: about 60 mm extra in one axis

Two practical layout options:

1. Sidecar electronics bay (same height)
- Capture chamber internal: 340 W x 290 H x 270 D mm
- Electronics bay internal: 200 W x 290 H x 270 D mm
- Combined internal envelope: about 540 W x 290 H x 270 D mm
- External with panel thickness and feet: about 590 W x 340 H x 320 D mm

2. Bottom electronics bay (stacked)
- Capture chamber internal: 340 W x 290 H x 270 D mm
- Bottom bay internal: 340 W x 140 H x 270 D mm
- Combined internal envelope: about 340 W x 430 H x 270 D mm
- External with panel thickness and feet: about 390 W x 480 H x 320 D mm

## Lens Choice Guidance
- 2.1 mm:
  - Pros: best fit for absolute minimum build height.
  - Cons: widest distortion profile and tighter lens-selection constraints.
- 2.8 mm:
  - Pros: strong balance of compactness, lens availability, and manageable distortion.
  - Cons: slightly taller enclosure than the 2.1 mm option.
- 3.2 mm:
  - Pros: balanced choice with slightly cleaner geometry than 2.8 mm.
  - Cons: modestly taller still.
- 4.0 mm:
  - Pros: cleanest geometry of these options.
  - Cons: pushes enclosure height closer to your upper acceptable range.

Recommended first build lens:
- Start with a 2.8 mm or 3.2 mm manual-focus M12 lens.
- Keep a 2.1 mm lens as the fallback if enclosure height becomes the dominant constraint.
- Keep a 4.0 mm lens as the cleaner-geometry option if you accept a taller build.

## Field of View Target
- To cover an 88.9 mm circular target from 2 to 4 inches away, you want approximately:
  - At 2.1 mm and about 2.0 inches: vertical FOV about 82 to 85 degrees
  - At 2.8 mm and about 2.7 inches: vertical FOV about 65 to 70 degrees
  - At 3.2 mm and about 3.1 inches: vertical FOV about 58 to 62 degrees
  - At 4.0 mm and about 3.9 inches: vertical FOV about 48 to 52 degrees
- In practical shopping terms, prioritize a 2.8-3.2 mm M12 manual-focus lens first, then verify sensor compatibility and close-focus behavior.

## Thermal and Lighting Placement Notes
- Keep LED emitters and drivers away from camera sensor thermal plume.
- Place one exhaust fan near top rear of chamber.
- Add filtered intake low and opposite side to encourage cross-flow.
- Keep dimmer and PSU modules in electronics bay, not in optical path volume.

## Validation Steps Before Cutting Panels
1. Build a temporary optical rig on rails.
2. Verify full-frame coverage at selected lens and working distance.
3. Rotate polarizers for minimum glare and lock camera settings.
4. Run 30-minute thermal test with lights and inference active.
5. Adjust final chamber depth by plus/minus 20 mm based on measured focus margin.

## Fusion360 Mirror Placement Recipe (4 inch Landing Area)

This section is the working recipe for the folded-path build.

### Coordinate Setup
- Define a vertical section sketch through the camera optical axis.
- Set the dice plane as horizontal at Z = 0.
- Set mirror plane at 45 degrees to the incoming and outgoing rays.
- Use these variables in Fusion360 parameters:
  - `H` = vertical rise from dice plane to mirror center (inches)
  - `X` = horizontal run from mirror center to lens entrance pupil (inches)
  - `L` = folded optical path length (inches)

At nominal 45 degrees reflection, the incoming and outgoing path lengths are:
- Mirror-to-scene path approximately `H`
- Lens-to-mirror path approximately `X`
- Total folded path: `L = H + X`

### Lens Sizing Targets For 4 inch Coverage (IMX296 width)
- Sensor width assumption for IMX296 active area: about 5.02 mm.
- Coverage model: `scene_width = sensor_width * L / focal_length`.

Solve for path length to fill 4.0 inches horizontally:
- 5 mm lens: `L` about 3.98 inches
- 6 mm lens: `L` about 4.78 inches

Recommendation:
- Start with 6 mm as primary.
- Keep 5 mm as fallback if you need wider framing margin.
- Avoid 4 mm unless you intentionally want extra-wide framing and plan to crop.

### Solved Dimension Sets (Ready To Enter)

Use one of these presets for initial CAD and prototype alignment:

Preset A (6 mm, near full-frame 4 inch target)
- `H = 2.4 in`
- `X = 2.4 in`
- `L = 4.8 in`
- Expected horizontal coverage about 4.0 in

Preset B (6 mm, extra framing margin)
- `H = 2.6 in`
- `X = 2.6 in`
- `L = 5.2 in`
- Expected horizontal coverage about 4.35 in

Preset C (5 mm, near full-frame 4 inch target)
- `H = 2.0 in`
- `X = 2.0 in`
- `L = 4.0 in`
- Expected horizontal coverage about 4.0 in

Preset D (5 mm, larger margin)
- `H = 2.4 in`
- `X = 2.4 in`
- `L = 4.8 in`
- Expected horizontal coverage about 4.8 in

### Guardrails To Avoid "Too Short" Focal Length Choice
- If your achievable `L` is usually 4.6 to 5.4 inches, 6 mm is the safer starting lens.
- If your achievable `L` is usually 3.8 to 4.5 inches, 5 mm is more forgiving.
- 4 mm tends to over-widen the scene at these distances and lowers pixel density on the die faces.

### Build/Calibration Procedure
1. Model mirror bracket with ±3 degrees angular adjustment around 45 degrees.
2. Model camera rail with at least ±0.5 inch linear adjustment for `X`.
3. Start at Preset A (`H = X = 2.4 in`) with 6 mm lens.
4. Capture frame and measure visible width of the landing plane.
5. If scene is too tight, increase `L` slightly by sliding camera away from mirror.
6. If scene is too wide, decrease `L` slightly by sliding camera toward mirror.
7. Lock mirror angle and camera rail, then re-tune polarizer orientation.

### Fusion360 Parameters Table (Copy/Paste Setup)

Create these user parameters in Fusion360:

| Name | Unit | Expression / Default | Notes |
| --- | --- | --- | --- |
| landing_diameter | in | 4.0 in | Target dice landing area |
| focal_length | mm | 6 mm | Primary lens setting |
| sensor_width | mm | 5.02 mm | IMX296 active width assumption |
| mirror_angle | deg | 45 deg | Nominal fold angle |
| H | in | 2.4 in | Mirror center above dice plane |
| X | in | 2.4 in | Lens pupil to mirror center run |
| L | in | H + X | Folded optical path (45 degree nominal) |
| scene_width | in | (sensor_width / focal_length) * L | Predicted horizontal coverage |
| framing_margin | in | scene_width - landing_diameter | Positive means extra border |
| rail_adjust | in | 0.5 in | Recommended camera rail travel each direction |
| mirror_trim | deg | 3 deg | Recommended mirror adjustability each direction |

Primary defaults (6 mm first pass):
- focal_length = 6 mm
- H = 2.4 in
- X = 2.4 in
- L = 4.8 in
- scene_width expected about 4.0 in

Fallback defaults (5 mm lens):
- focal_length = 5 mm
- H = 2.0 in
- X = 2.0 in
- L = 4.0 in
- scene_width expected about 4.0 in

Quick tuning rule in CAD and prototype:
- Need wider view: increase L by increasing X and/or H.
- Need tighter view: decrease L by decreasing X and/or H.

### Dimensioned Sketch Legend (Fusion360 First Sketch)

Use a single side-view sketch (XZ-style section) and map geometry like this:

Reference points:
- `P0` = dice-plane origin (0, 0)
- `P1` = mirror center
- `P2` = lens entrance pupil center

Reference lines:
- `dice_plane`: horizontal construction line through `P0`
- `incoming_ray`: construction line from `P0` to `P1`
- `outgoing_ray`: construction line from `P1` to `P2`
- `mirror_plane`: construction line through `P1`, constrained to `mirror_angle`

Dimension mapping:
- `H` = vertical distance from `dice_plane` to `P1`
- `X` = horizontal distance from `P1` to `P2`
- `L` = path budget parameter (`H + X`), tracked in parameters table
- `mirror_angle` = angle between `mirror_plane` and `incoming_ray` bisector equivalent setup (nominal 45 deg fold)

How to constrain the first sketch:
1. Draw `dice_plane` as horizontal construction line through `P0`.
2. Place `P1` above `P0`; dimension vertical from `dice_plane` to `P1` as `H`.
3. Draw `incoming_ray` from `P0` to `P1`.
4. Draw `mirror_plane` through `P1`; set angle to `mirror_angle`.
5. Place `P2` to the right of `P1`; dimension horizontal `P1` to `P2` as `X`.
6. Draw `outgoing_ray` from `P1` to `P2`.
7. Add lens body placeholder centered on `P2` and mount it to a rail slot driven by `rail_adjust`.

Suggested named dimensions in sketch:
- `d_H` linked to `H`
- `d_X` linked to `X`
- `a_mirror` linked to `mirror_angle`

Sanity checks after sketching:
- `incoming_ray` and `outgoing_ray` intersect only at `P1`.
- Increasing `X` widens scene coverage (via larger `L`).
- Decreasing `X` tightens scene coverage (via smaller `L`).
- Mirror bracket has enough clearance for `mirror_trim` adjustment.

### 3D Feature Mini-Legend (Fusion360 Starter Dimensions)

Use these as first-pass values for a printable or machined prototype. Keep all of them as editable user parameters.

#### A) Mirror Bracket

Recommended first-surface mirror blank:
- `mirror_w = 80 mm`
- `mirror_h = 60 mm`
- `mirror_t = 2 mm`

Bracket starter parameters:
- `bracket_t = 4 mm` (plate thickness)
- `mirror_lip = 2.5 mm` (retention edge on two sides)
- `mirror_clear = 0.4 mm` (clearance around mirror pocket)
- `pivot_d = 4.3 mm` (for M4 pivot bolt)
- `pivot_offset = 20 mm` (pivot center from bracket base edge)
- `angle_arc_r = 22 mm` (slot radius around pivot)
- `angle_arc_span = 14 deg` (supports +/- 7 deg trim)

Build notes:
- Add compliant pads or thin tape under mirror support surfaces.
- Keep clamp pressure low and uniform to avoid mirror warp.

#### B) Camera Rail + Carriage

Rail starter parameters:
- `rail_slot_w = 6.5 mm` (M6 clearance slot)
- `rail_slot_len = 30 mm` (supports about +/-15 mm slide)
- `rail_edge_margin = 8 mm`
- `carriage_t = 5 mm`
- `camera_hole_pattern = 28 mm` (typical board spacing; verify camera PCB)
- `camera_hole_d = 3.2 mm` (M3 clearance)

Build notes:
- Place rail direction colinear with `X` adjustment direction.
- Use two fasteners on the carriage to prevent yaw during tightening.

#### C) Base Plate + Hole Pattern

Base starter parameters:
- `base_t = 6 mm`
- `base_w = 160 mm`
- `base_d = 120 mm`

Hole pattern starter:
- `mount_hole_d = 4.3 mm` (M4 clearance)
- `mount_edge_margin = 10 mm`
- `mount_pitch_x = 120 mm`
- `mount_pitch_y = 80 mm`

Suggested layout:
- Keep mirror bracket and camera rail on same base datum plane.
- Add two 3 mm dowel/reference holes for repeatable disassembly alignment.

#### D) Fastener Starter Kit
- Mirror pivot: M4 x 16 mm bolt + washer + nyloc nut
- Mirror clamp screws: M3 x 10 mm (if clamped frame design)
- Camera carriage: M3 x 8/10 mm into inserts or nuts
- Base mounting: M4 x 10/12 mm

#### E) Tolerance and Print Guidance
- Printed slot clearance: +0.2 to +0.3 mm over nominal bolt diameter
- Mirror pocket clearance: +0.3 to +0.5 mm on width/height
- Flatness priority surfaces:
  - mirror support ledge
  - camera carriage face
  - base datum face

#### F) Quick Assembly Order
1. Fix base to enclosure datum.
2. Install mirror bracket with pivot and angle slot fastener lightly tightened.
3. Install camera carriage on rail and set nominal `X`.
4. Set mirror near 45 deg, then frame target and lock rail position.
5. Fine-trim mirror angle for center/framing and lock bracket.
6. Re-check `scene_width` against parameter prediction and adjust if required.
