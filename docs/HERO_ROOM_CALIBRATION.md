# Hero Room calibration — source vs. Godot v0011 (TASK-0038)

Measured 2026-10-27 by Claude Code (`Agent: claude`) under the one-time owner decision of 2026-10-27 that let Claude run this graphics/calibration task with image reads. Measurements only: no art was generated or edited, and no map, catalog or part file was changed. This is **not** visual approval.

## 1. Signed source identity
| Item | Path | Pixels | SHA-256 (measured) |
| --- | --- | --- | --- |
| Original reference | `map_factory/references/hero_room_01_original.png` | 1448x1086 RGB | `42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7`. Matches `hero_room_01_original.reference.json` |
| Godot capture v0011 | `…/AncientSeal-DevTools/current-map-qa-final/.agents/monitoring/.local/qa-evidence/GOAL-0001/hero_room_01_v0011.png` (local, not committed) | 1536x1024 RGBA | `c8558d87da0ce61b978b2801f4d8885a6742a58b61a883a8bd6335e4a0a2ebb5` |
| Map revision | `map_factory/maps/hero_room_01/versions/v0011.json` | canvas 1536x1024, grid 17x10 @64, origin (226,225) | `e293de120de43a793f1e5b95e75a81eef24f5afb1af017923a87f6cb481206b3` |
| Catalog | `map_factory/metadata/asset_index.json` | — | `6962923373eec62d16dc50116114a811732fbdeb6bd815ffc0270fffc9ad4d1c` |

Signed: Claude Code, 2026-10-27. The reference hash was verified before any measurement.

**Limits of the capture:** the v0011 capture was made from an image-free checkout. Every sprite is drawn as a labelled `(draft)` placeholder, so the capture confirms **anchor positions only**. For example, the anchors of A005 (759,346), O028 (892,543) and E023 (394,941) match the JSON. The capture does not show craftsmanship. Rendered sizes below are therefore computed as catalog native size × placement scale, with opaque (alpha > 24) bounds measured from each part PNG. Transparent padding is under 10 % for all parts used, except W015 (123 of 146 px wide), O028 (235 of 268 px) and V017 (148 of 171 px tall). A real textured source-versus-Godot capture is still required (TASK-0001 / TASK-0037).

## 2. Method and calibration transform
- I measured source bounding boxes by eye on grid overlays (50 px lines, and 25 px lines at 2x for the floor). Precision is about ±5 px. Boxes are tight to visible pixels. "Contact" means the lowest ground-touching pixel row.
- I fitted the floor box: source floor x 190–1310 and y 280–800 maps to Godot floor x 226–1314 and y 225–865. This gives the ground-plane transform **T: rx = 226 + (sx−190)·0.971, ry = 225 + (sy−280)·1.231**.
- **D1 – projection mismatch (owner decision):** source flagstone grout intersections are at x ≈ 570/671/779/979 and y ≈ 339/400/462. One source tile is therefore **≈104x62 px**, an oblique 3/4 tile with an aspect ratio of 0.60. Godot draws 64x64 square cells. At the uniform image scale of 0.971, the source floor is 1088x505 render px, but v0011 draws it 1088x640. **The render floor is 27 % too deep.** This is why ground-plane contacts must use T (sy 1.231), while upright sprites must use the uniform 0.971 scale or they would be stretched. Options: (a) keep the 64 px logical grid, reduce the walk depth to 8 rows (512 px) and use the uniform scale for everything; or (b) keep 10 rows and accept depth-stretched placements. The audit locks the rectangular logical grid. Only the row count and depth scale are open.
- Ratios: `w`/`h` = rendered opaque size ÷ (source size × 0.971). Flat floor items (rugs, inlay, stairs) use 1.231 for height. `s*` = the scale that gives a width ratio of 1.00. `d(x,y)` = placement anchor minus T(source contact). For wall-mounted items, T is only indicative. Use the host-relative values in §5.
- Classes: **reuse** = the existing asset fits as placed (|d| ≤ 32 px and ratio 0.85–1.15). **repair** = the asset fits but its scale, placement, pivot or collision data is wrong (data-only fix, no art). **new** = no acceptable registered asset, so an ART request is needed. **deferred** = out of scope, hidden by UI, or waiting on an owner decision.

## 3. Visible-component measurements
Source box = x0,y0–x1,y1 in source px. Expected contact = T(source contact).

| Component | Source box | Source size | Expected contact | Render instance: asset native (opaque) scale → display; d; ratios; s* | Class / action |
| --- | --- | --- | --- | --- | --- |
| Bed | 275,312–478,525 | 203x213 | (407,526) | `HeroBed` P024 679x570 s0.42→285x239; d(+2,+33); w1.45 h1.16; s*0.29<br>`HeroHDBedCover` P025 760x516 s0.37→281x190; d(+2,+23); w1.43; s*0.26 | **repair**. Accepted HD reused: P024 s0.29, P025 s0.26, contact y 526, then rescale the mount offset |
| Headboard shelf (books, coral, lantern) | 310,245–485,300 | 175x55 | (427,249) | `LeftBookshelf` P014 296x269 (294x269) s0.63→185x169; d(−20,+174); w1.09 h3.17 | **new** (ART-0008). P014 is a tall free-standing case (aspect 1.09 vs 3.18). Native 170x53 |
| Bedside table + shell | 215,405–290,490 | 75x85 | (286,483) | `SideTable` P007 151x243 (139x241) s0.58→80x139; d(−10,+83); w1.11 h1.69; s*0.52 | **repair**. P007 already carries the shell. s0.52, contact (286,483). Re-check height after D1 |
| Bed rug | 215,365–528,548 | 313x183 | (402,554) | `BedRug` P005 238x304 (236x303) s0.69→162x209; d(+7,+39); w0.54 h0.93 | **new** (ART-0015, bedroom output). Portrait top-down rug vs landscape oblique rug (aspect 0.78 vs 1.71). Native 304x225 (D1-a: 304x178) |
| Blue vase left of arch | 480,280–520,335 | 40x55 | (527,292) | none | **reuse**. Add O002 (85x123) s0.46 → 39x57 at (527,292) |
| Arch + paired columns | 512,20–860,325 | 348x305 | (707,280) | `ArchMain` A005 328x283 s1.03→337x291; d(+51,+65); w1.00 h0.98 | **repair**. Scale is correct. Move to (707, ≈289), the back edge of floor row 1 |
| — extra columns | — | — | — | `A007_back_objects_008` A007 s0.82; d(−78,+79)<br>`A012_back_objects_009` A012 s0.84; d(+198,+79) | **deferred / omit**. The source columns are part of A005. These duplicates are not in the source |
| — HD pillar / door at arch | — | — | — | `HeroHDPillar` A017 s0.40; d(−127,+135)<br>`HeroHDDoor` A018 s0.43; d(+65,+155) | **deferred** (owner). The source arch is open to the sea and has no shrine pillar or blue door. Keep the accepted HD files, but remove them from this composition |
| Banner right of arch | 845,130–895,270 | 50x140 | (886,212)* | `CompassBannerArchRight` D004 84x152 (82x151) s0.79→64x119; d(+133,+78); w1.33 h0.88; s*0.59 | **repair**. D004 s0.59, mounted on the right arch column (§5) |
| — duplicate HD banner | — | — | — | `HeroHDBanner` D019 491x667 s0.31→152x206; w3.14 | **deferred**. Not in the source at this spot. Accepted HD retained |
| Right wall door + lantern | 1060,170–1145,280 (lantern 1018,195–1045,245) | 85x110 | (1112,225) | `DecoratedDoorRight` A015 196x233 s0.68→133x157; d(+136,+130); w1.61 h1.48; s*0.42 | **repair**. A015 already contains the door and lantern. s0.42, base (1112,225). ART-0005 becomes a cancel candidate |
| Right shelf (candles, books, crates) | 985,280–1180,410 | 195x130 | (1092,385) | `RightBookshelf` P015 210x232 (209x230) s0.63→131x144; d(+39,+27); w0.70 h1.15 | **new** (ART-0020, south view). Aspect 0.91 vs 1.50. Native 189x126 |
| Astrolabe on shelf | 1145,255–1190,305 | 45x50 | on shelf top | `Astrolabe` O019 151x141 s0.57→85x80; d(+50,+256); w1.96 h1.66; s*0.29 | **repair**. O019 s0.29, mounted on the right shelf top. ART-0010 becomes a cancel candidate |
| Large blue planter + palm | 1170,270–1305,435 | 135x165 | (1243,415) | `V017_objects_010` V017 142x171 (141x148) s0.60→84x88; d(+109,+207); w0.65 h0.55 | **new** (ART-0011), unless the reviewer accepts an O001 + V017 composite. Native 131x160 |
| Study desk (+stool) | 1010,415–1285,575 (stool 1110,520–1170,585) | 275x160 | (1155,588) | `WritingTable` P026 760x561 s0.46→349x258; d(−31,+17); w1.31 h1.66; s*0.35 | **repair**. Accepted HD P026 already contains the stool. s0.35 |
| Study rug | 995,450–1315,580 | 320x130 | (1163,594) | `DeskRug` P005 s0.68→160x206; d(−37,+36); w0.52 h1.29 | **new** (ART-0015 primary). Native 311x160 (D1-a: 311x126) |
| Blue vase right of arch | 945,280–995,345 | 50x65 | (983,305) | `VaseByArch` O001 117x165 (107x164) s0.43→46x70; d(+78,+178); w0.95 h1.12 | **repair**. Move to (983,305) and set s0.45 |
| Lantern, back-left wall | 315,195–345,245 | 30x50 | mount | `D007_back_objects_012` D007 73x141 (70x140) s0.63→44x88; w1.51 h1.82; s*0.42 | **repair**. s0.42, re-mount (§5) |
| Lantern, left side wall | 215,310–250,385 | 35x75 | mount | `LeftWallLantern` D008 94x175 (89x160) s0.59→52x94; w1.55 h1.30; s*0.38 | **repair**. s0.38. The east-pointing bracket matches |
| Lantern, back-right (part of door) | 1018,195–1045,245 | 27x50 | mount | `D007_back_objects_013` D007 s0.63; d(+191,+251) | **deferred / omit**. Already drawn inside A015 |
| Lantern, right side wall | 1305,445–1335,500 | 30x55 | mount | `RightWallLantern` D009 116x166 s0.59→68x97; w2.35 h1.82 | **new** (ART-0023). D009's bracket points east, but the right side wall needs a west-pointing view. Mirroring is forbidden. Native 29x53 |
| Banner, left back corner | 250,250–278,345 | 28x95 | mount | none | **new** (ART-0023 side view). Native 27x92 |
| Banner, left side wall | 148,360–180,530 | 32x170 | mount | `W015_back_objects_006` W015 146x157 (123x151) s0.89→109x134; w3.52 | **new** (ART-0023). Foreshortened east-facing banner (aspect 0.19). Native 31x165 |
| Banner, lower left | 125,580–175,780 | 50x200 | mount | `BlueBannerLeft` D001 154x260 s0.59→89x152; w1.85 h0.79 | **new** (ART-0023). Native 49x194 |
| Banner, lower right | 1320,560–1375,740 | 55x180 | mount | `BlueBannerRight` D001 s0.62; w1.76<br>`W015_back_objects_007` W015 s0.89 | **new** (ART-0023, west-facing). Native 53x175 |
| Rope-and-post fence, left | 200,610–295,740 (posts 200,610–225,660 and 265,660–295,740) | 95x130 | (281,791) | none | **new** (ART-0024). Native post 29x78, run 92x126 |
| Rope-and-post fence, right | 1210,620–1300,745 (posts 1210,670–1240,745 and 1275,620–1300,690) | 90x125 | (1260,797) | none | **new** (ART-0024). Native run 87x121 |
| Ball-topped pedestal left | 555,730–600,810 | 45x80 | (602,≤865) | `EntrancePillarLeft` ST011 72x110 (71x109) s0.74→52x80; d(+39,−21); w1.20 h1.04; s*0.62 | **repair**. ST011 already has the sphere finial. s0.62. ART-0006 becomes a cancel candidate |
| Ball-topped pedestal right | 855,735–900,820 | 45x85 | (893,≤865) | `EntrancePillarRight` ST012 90x117 s0.74→66x85; w1.52 | **repair**. Replace with a second ST011 instance at s0.62. ST012 has no sphere |
| Entrance stairs (visible part) | 650,795–810,880 (UI covers ≥ 845–870) | 160x85 | (750,963) | `EntryStairUpper/Middle/Lower` ST001–ST003 s1.03–1.05→≈199x73; `LandingCenter` ST006; w1.12–1.30 h0.61–0.70 | **new** (ART-0025). Visual check: the ST001–ST006 face pixels are flat procedural fills. Native visible part 155x105. Lower steps hidden by UI: **deferred** |
| Wooden chest (front right) | 1130,715–1190,790 | 60x75 | (1167,852) | `TreasureChest` P023 649x540 s0.31→201x167; d(+32,−72); w3.45 h2.30 | **new** (ART-0021, south view). The source is a plain brown plank chest; P023 is cobalt/gold. Keep the accepted HD P023 elsewhere. Native 58x73 |
| Seashell (front) | 1040,750–1090,800 | 50x50 | (1075,865) | `Shell` O021 123x114 (121x112) s0.35→42x39; d(+244,−105); w0.87 h0.81 | **repair**. Move to (1075,865) and set s0.40 |
| Small blue vase (front) | 1095,750–1135,800 | 40x50 | (1124,865) | `V020_objects_012` V020 107x108 s0.49→52x51; w1.35 | **reuse**. Swap V020 (crop debris, cut at the left edge) for O003 85x110 at s0.46 |
| Compass floor inlay | 575,490–850,700, centre (712,595) | 275x210 | centre (733,613) | none. 3x3 procedural tiles F014–F022 at grid (7..9, 4..6) = 674–866 x 481–673 | **new** (ART-0022). The source is a 45°-rotated oblique rhombus. The squares and O020 (top-down circle) do not match. Native 267x259 (D1-a: 267x204) |
| Floor flagstones | tile ≈104x62 | — | — | F001/F002 162x161 crops on 64x64 cells | **repair / D1**. Owner decides on projection depth before any floor art |
| Back walls, left run (bed alcove + side wall) | 150,145–500,560 | — | base y≈300 → 250 | W021 s0.38 (258x320, base 445), W001, W003, `RearLeftFlowerWall` W012 | **repair** (placement and seams, §6). Accepted HD W021 is the corner face. Per-piece ratios are not comparable because pieces overlap by 33–109 px |
| Back walls, right run (door wall + side wall) | 965,85–1340,560 | — | base y≈410 → 385 | W022 s0.38 (base 446), W002, W014, `RearRightFlowerWall` W013 | **repair** (§6). Continuous side-wall runs: **new** (ART-0004). The existing delivery manifest says `builder: wall_run`, i.e. procedural, which AGENTS.md §4 says can never count as accepted art; this needs an independent reviewer |
| Antlered treant figure | 820,290–955,495 | 135x205 | (903,489) | `AntleredFlowerShrine` O028 268x276 (235x260) s0.73→171x189; d(−11,+53); w1.31 | **deferred**. In the source this is an NPC character (out of scope, AGENTS.md §1). O028 is a procedural environment substitute. Owner decides whether to keep or omit it |
| Hero, two fairies, turtle | — | — | — | none | **deferred**. Characters are out of scope |
| UI title (24,18–410,95) and dialogue/portrait (48,845–1400,1060) | — | — | — | none | **deferred**. UI is out of scope. It hides source rows ≥ 845, so the front wall, lower stairs, cliff foundation (E023/E024) and lower vines cannot be measured |
| Diagonal sun shafts, distant sea stacks, vine clusters | — | — | — | E015–E017, V001–V024 | **deferred measurement**. Not measured in this pass. Sun shafts stay with ART-0013. Do not invent numbers |

\* Wall-mounted: T is indicative only. Use §5.

## 4. Ground and collision contacts
These compare the render collision rectangle with the source ground footprint passed through T. Coverage = the share of the expected footprint that the render rectangle covers.

| Instance | Render rect | Expected (T) | Coverage | Action |
| --- | --- | --- | --- | --- |
| HeroBed | 318,500–502,558 | 309,287–506,527 | 10 % | repair: 197x240 (D1-a: 197x189) |
| SideTable | 244,529–308,565 | 250,440–323,484 | 0 % | repair: 73x44 |
| LeftBookshelf | 338,378–476,424 | 343,231–512,250 | 0 % | moves with the headboard shelf (ART-0008). Wall-backed: no separate collider needed |
| RightBookshelf | 1073,370–1191,412 | 998,336–1187,385 | 18 % | repair: 189x49 |
| WritingTable | 1022,552–1226,608 | 1022,459–1289,588 | 22 % | repair: 267x129 |
| TreasureChest | 1163,745–1237,785 | 1139,816–1197,853 | 0 % | repair with ART-0021: 58x37 |
| AntleredFlowerShrine | 852,498–932,544 | 852,459–959,490 | 0 % | deferred (owner) |
| Deep corners W020 x2, foundations E023/E024 | enabled | not measurable (UI occludes or no source equivalent) | — | deferred |

Of 38 architecture placements, only 2 have collision. Navigation region `inner_terrace_safe_walk` [1,2,15,7] = 290–1250 x 353–801. Under T, the source walkable floor runs from y≈287 (alcoves) to ≈865 (stair top), so the region should grow after D1. Missing colliders: pedestals (ST011 base ≈ 30x16 each), rope posts (≈20x12 each), vases O001/O002 (≈36x18).

## 5. Mounts (v0011 `mount_on`)
9 of 15 mounted anchors fall **outside** their host's bounding box. These are measured defects.

| Child | Host | Child anchor | Host bbox | Result | Source host-relative position (src px → render px) |
| --- | --- | --- | --- | --- | --- |
| D007_back_objects_012 | W001_back_objects_002 | 325,426 | 190,171–365,405 | OUTSIDE, below the wall base | lantern bottom 55 → 53 above the back-wall base (src 300) |
| D007_back_objects_013 | W014_back_objects_005 | 1235,433 | 1241,186–1407,414 | OUTSIDE | omit (inside A015) |
| CompassBannerArchRight | A012_back_objects_009 | 1020,291 | 863,132–950,360 | OUTSIDE | re-host on A005. Banner top 195 → 189 above the arch base (src 325), x = column right +10 |
| LeftWallLantern | W001_back_objects_002 | 256,463 | 190,171–365,405 | OUTSIDE | side wall. Bottom 175 → 170 above the bed-rug floor line (src 560) |
| RightWallLantern | W014_back_objects_005 | 1332,481 | 1241,186–1407,414 | OUTSIDE | ART-0023 west view. Bottom ≈60 → 58 above the right floor line (src 560) |
| ArchRightFlowers | W002_back_objects_004 | 1054,320 | 1072,173–1225,349 | OUTSIDE | re-host on A005 |
| UpperLeftClimbingIvy | W001_back_objects_002 | 225,434 | 190,171–365,405 | OUTSIDE | deferred (vine pass) |
| UpperRightClimbingIvy | W014_back_objects_005 | 1305,440 | 1241,186–1407,414 | OUTSIDE | deferred (vine pass) |
| FlowerClusterArch, HeroHDBedCover, FrontIvyLeft/Right, ArchLeftFlowers, BlueBannerLeft/Right | — | — | — | inside | HeroHDBedCover offset must rescale with P024. Banners move to ART-0023 |

## 6. Seams (adjacent pieces in each run; dx = gap(+)/overlap(−) in px, base_dy = contact-y jump)
| Run | Pairs |
| --- | --- |
| Back left | W001→W021 −109/+40; W021→W003 −108/−86; W003→W012 −102/+13; W012→A017 −33/+44; A017→A007 −58/−56; A007→A005 −81/−14 |
| Back right | A005→A012 −64/+14; A012→W013 **+58 gap**/+13; W013→W022 −87/+73; W022→W002 −222/−97; W002→A015 −42/+6; A015→W014 −74/+59 |
| Front | W012→ST013 −18/+96; ST013→W012 −90/−33; W012→ST013 −76/+40; ST013→W010 −136/−20; W010→ST011 −13/−5; ST011→ST001 +8/+39; ST001→ST012 −26/−39; ST012→W011 +4/+2; W011→W013 −20/−12; W013→W013 **+84 gap**/−60 |
| Foundation | E023→ST003 **+131 gap**/+1; ST003→E024 **+118 gap**/−1 |

None of the runs is butt-jointed. Overlaps hide seams instead of matching interfaces, and base jumps of up to 97 px break a single ground line. Source walls are continuous runs whose bases follow the floor edge. Measured interfaces belong in TASK-0039 (geometry contracts) and TASK-0040 (sorting/mounts).

## 7. Request mapping
- **New requests written:** ART-0022 compass inlay; ART-0023 side-wall banner and west-pointing lantern views; ART-0024 rope-post fence; ART-0025 entrance stairs. All are `blocked_reference` until the owner reviews the calibrated specs.
- **Existing requests calibrated** (a section was appended): ART-0004, 0008, 0011, 0015 (bedroom output added), 0020, 0021 need art. ART-0001, 0005, 0006, 0007, 0010, 0019 become cancel/defer candidates, because accepted HD or existing parts fit after a data repair.
- Not calibrated this pass: ART-0002/0003 (water and cloud motion), 0009, 0012, 0013, 0014, 0016–0018 (shadows and edges).

## 8. Owner decisions
D1 floor depth / projection. Fate of A017/A018/D019/A007/A012 in this room (omit, never delete). Treant substitute O028. Accepting the O001+V017 planter composite. Status of ART-0004/0014 procedural deliveries.
