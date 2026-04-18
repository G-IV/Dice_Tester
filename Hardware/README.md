# Hardware Index

Last updated: 2026-04-18

## Current Recommended Build
- Option: B+ (Orin NX 16 GB-class compute)
- Status: **SBC purchase confirmed** – Waveshare Jetson Orin NX 16GB Dev Kit (SKU 24222) at $1,175.99.
- Control split: SBC for vision/UI/storage, MCU for deterministic 333 Hz PWM.
- Storage: 256 GB NVMe baseline (included with kit).
- Budget reality: ~$1,650–$1,700 total system cost with new peripherals; ~$1,550–$1,600 with reused input devices.

## Quick Links
- [hardware-plan.md](hardware-plan.md)
- [hardware-bom-wiring.md](hardware-bom-wiring.md)
- [shopping-shortlist.md](shopping-shortlist.md)
- [enclosure-footprint-estimate.md](enclosure-footprint-estimate.md)

## Next Actions
1. Validate exact Orin NX 16 GB kit SKU and JetPack support.
2. Confirm camera manual-control support in Linux UVC path.
3. Confirm servo logic threshold and power draw for final signal stage and fuse sizing.
4. Build temporary optical rig to validate 4.0 mm lens working distance and field coverage.
