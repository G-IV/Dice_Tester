"""
Lens working-distance & mirror–tower clearance calculator
for the Die Tester capture chamber.

Lens:   60°(D) × 50°(H) × 38°(V)
Target: 3.5" (88.9 mm) diameter die landing circle

Geometry: folded optical path via 45° first-surface mirror.
  Total optical path = horizontal leg (camera → mirror)
                     + vertical leg   (mirror  → die)

Two independent constraints drive the minimum path:

  1. FOV constraint (optical):
       WD_min = (D/2) / tan(FOV_V/2)
       The vertical FOV (38°) is the limiting dimension.

  2. Collision constraint (physical):
       The dice-tower cylinder must not collide with the top edge of the mirror.
       min_vert_leg = mirror_top_dist / sqrt(2)
       where mirror_top_dist is the Euclidean distance from origin to the
       topmost point of the mirror.

The minimum total WD is driven by the FOV constraint (129.09 mm).
The split between legs is driven by the collision constraint:
  vert_leg_min = mirror_top_dist / sqrt(2)   (collision floor)
  horiz_leg    = WD_total - vert_leg
"""

import math


# ── Lens & target parameters ────────────────────────────────────────────────

FOV_H_DEG = 50.0        # horizontal field of view (°)

FOV_V_DEG = 38.0        # vertical field of view   (°)
FOV_D_DEG = 60.0        # diagonal field of view   (°)

TARGET_DIA_IN = 3.5                     # die landing zone diameter (inches)
TARGET_DIA_MM = TARGET_DIA_IN * 25.4   # → 88.9 mm


# ── Helpers ──────────────────────────────────────────────────────────────────

def wd_for_fill(obj_size, fov_deg, fill=1.0):
    """Return WD so that obj_size fills `fill` fraction of the frame
    dimension corresponding to fov_deg."""
    return obj_size / (2 * math.tan(math.radians(fov_deg / 2)) * fill)


def frame_dims(wd, fov_h=FOV_H_DEG, fov_v=FOV_V_DEG):
    """Return (frame_width, frame_height) at a given working distance."""
    w = 2 * wd * math.tan(math.radians(fov_h / 2))
    h = 2 * wd * math.tan(math.radians(fov_v / 2))
    return w, h


# ── Minimum working distance ─────────────────────────────────────────────────

WD_MIN_IN = wd_for_fill(TARGET_DIA_IN, FOV_V_DEG, fill=1.0)
WD_MIN_MM = WD_MIN_IN * 25.4

fw0, fh0 = frame_dims(WD_MIN_IN)

print("=" * 64)
print("  Die Tester · Lens Working-Distance Calculator")
print("=" * 64)
print(f"  Lens FOV : {FOV_H_DEG}° (H) × {FOV_V_DEG}° (V)  [{FOV_D_DEG}° diag]")
print(f"  Target   : ⌀ {TARGET_DIA_IN}\" ({TARGET_DIA_MM:.1f} mm) circle")
print()
print("  MINIMUM WORKING DISTANCE  (circle exactly fills V dimension)")
print(f"    WD_min  = {WD_MIN_IN:.4f}\"  =  {WD_MIN_MM:.2f} mm")
print(f"    Frame   = {fw0:.4f}\" W × {fh0:.4f}\" H")
print(f"    Fill    = {TARGET_DIA_IN/fw0*100:.1f}% W,  100.0% V")
print()


# ── Fill-ratio table ──────────────────────────────────────────────────────────
# No hard optical maximum — the maximum is a design choice.
# This table shows how WD grows as you allow the circle to fill a smaller
# fraction of the vertical frame dimension.

print("  FILL-RATIO TABLE  (V fill % → required WD)")
print(f"  {'V fill':>7}  {'WD (in)':>9}  {'WD (mm)':>9}  "
      f"{'Frame W (in)':>13}  {'Frame H (in)':>13}  {'H fill':>7}")
print("  " + "-" * 64)
for fill_v in [1.00, 0.90, 0.80, 0.75, 0.70, 0.60, 0.50]:
    wd = wd_for_fill(TARGET_DIA_IN, FOV_V_DEG, fill_v)
    fw, fh = frame_dims(wd)
    print(f"  {fill_v*100:>6.0f}%  {wd:>9.4f}  {wd*25.4:>9.2f}  "
          f"{fw:>13.4f}  {fh:>13.4f}  {TARGET_DIA_IN/fw*100:>6.1f}%")
print()


# ── Folded-path splits ────────────────────────────────────────────────────────
# For a 45° mirror:  horiz_leg + vert_leg = WD_total
# Either leg can be the longer one; pick based on enclosure geometry.

# ── Section 2: Mirror–tower collision geometry ───────────────────────────────

MIRROR_TOP_DIST_MM = 40.659   # Euclidean distance from origin to topmost mirror point
MIRROR_ANGLE_DEG   = 45.0

TOWER_DIA_IN  = 5.0
TOWER_DIA_MM  = TOWER_DIA_IN * 25.4
TOWER_RAD_MM  = TOWER_DIA_MM / 2
TOWER_H_IN    = 6.0
TOWER_H_MM    = TOWER_H_IN * 25.4

# Topmost mirror point coordinates (at 45°, symmetric)
mirror_top_x = MIRROR_TOP_DIST_MM * math.cos(math.radians(MIRROR_ANGLE_DEG))
mirror_top_y = MIRROR_TOP_DIST_MM * math.sin(math.radians(MIRROR_ANGLE_DEG))

# Mirror top is within cylinder footprint when mirror_top_x < tower_radius.
# In that case, the Y coordinate of the topmost mirror point is the hard floor
# for the tower bottom (vert leg).
inside_footprint = mirror_top_x < TOWER_RAD_MM
z_critical_mm = math.sqrt(TOWER_RAD_MM**2 - mirror_top_x**2) if inside_footprint else 0.0

VERT_LEG_MIN_MM = mirror_top_y          # collision floor
HORIZ_LEG_AT_MIN_MM = WD_MIN_MM - VERT_LEG_MIN_MM

print("─" * 64)
print("  MIRROR–TOWER CLEARANCE")
print("─" * 64)
print(f"  Mirror half-extent along surface  = {MIRROR_TOP_DIST_MM} mm")
print(f"  Topmost mirror point  X = {mirror_top_x:.4f} mm,  Y = {mirror_top_y:.4f} mm")
print()
print(f"  Tower cylinder  ⌀ {TOWER_DIA_IN}\" ({TOWER_DIA_MM:.1f} mm),  "
      f"h {TOWER_H_IN}\" ({TOWER_H_MM:.1f} mm)")
print()
print(f"  Mirror top X ({mirror_top_x:.2f} mm) < tower radius ({TOWER_RAD_MM:.1f} mm)?  "
      f"{'YES — inside footprint' if inside_footprint else 'NO — always clear'}")
if inside_footprint:
    print(f"  Mirror top edge is inside footprint for |z| < {z_critical_mm:.2f} mm")
print()
print(f"  MINIMUM VERTICAL LEG  (mirror centre → tower bottom)")
print(f"    vert_leg_min  =  {VERT_LEG_MIN_MM:.4f} mm  =  {VERT_LEG_MIN_MM/25.4:.4f} in")
print(f"    = mirror_top_dist / sqrt(2)  =  {MIRROR_TOP_DIST_MM} / {math.sqrt(2):.6f}")
print()
print(f"  MINIMUM-TOTAL-WD FOLDED-PATH BREAKDOWN")
print(f"    WD_total (optical floor)  =  {WD_MIN_MM:.4f} mm")
print(f"    Vert leg  (collision floor) =  {VERT_LEG_MIN_MM:.4f} mm  ({VERT_LEG_MIN_MM/25.4:.4f} in)")
print(f"    Horiz leg                  =  {HORIZ_LEG_AT_MIN_MM:.4f} mm  ({HORIZ_LEG_AT_MIN_MM/25.4:.4f} in)")
print()


# ── Fusion 360 user parameters ────────────────────────────────────────────────

print("─" * 64)
print("  FUSION 360 USER PARAMETERS  (copy-paste into Parameters dialog)")
print("─" * 64)
print(f"  lens_fov_h_deg          = {FOV_H_DEG}")
print(f"  lens_fov_v_deg          = {FOV_V_DEG}")
print(f"  target_dia_mm           = {TARGET_DIA_MM:.2f}")
print(f"  mirror_top_dist_mm      = {MIRROR_TOP_DIST_MM}   ← half-extent of mirror surface")
print(f"  tower_dia_mm            = {TOWER_DIA_MM}")
print(f"  tower_height_mm         = {TOWER_H_MM:.1f}")
print()
print("  Derived (enter as expressions):")
print(f"  vert_leg_min_mm         = mirror_top_dist_mm / sqrt(2)          "
      f"→ {VERT_LEG_MIN_MM:.4f} mm")
print(f"  wd_min_mm               = (target_dia_mm/2) / tan(lens_fov_v_deg/2 deg)  "
      f"→ {WD_MIN_MM:.4f} mm")
print(f"  horiz_leg_min_mm        = wd_min_mm - vert_leg_min_mm           "
      f"→ {HORIZ_LEG_AT_MIN_MM:.4f} mm")
print(f"  frame_w_mm              = 2 * wd_min_mm * tan(lens_fov_h_deg/2 deg)")
print(f"  frame_h_mm              = 2 * wd_min_mm * tan(lens_fov_v_deg/2 deg)")
