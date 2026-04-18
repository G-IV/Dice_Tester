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
