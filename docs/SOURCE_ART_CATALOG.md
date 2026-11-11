# دليل الصور المولدة وبيانات القطع

الفهرس القابل للبحث: `map_factory/metadata/source_art_index.json`. ابحث بواسطة ART أو اسم القطعة أو الفئة؛ كل سجل يحتوي بيانات المصدر الأصلية وقياسات PNG وبصمته ومسار manifest وREADME وحالة النشر والموافقة.

الأصول محفوظة مباشرة تحت `H:/shining force/skl-SF/assets_hd/<category>/<group>/vNNN/`. بياناتها ومعايناتها تحت `game_factory/environment/ART-####/vNNN/`. لا يعتمد التسليم على cache أداة التوليد. ملفات الشخصية السابقة محفوظة في مساراتها الأصلية المحمية ولا تُنقل.

الموافقة البصرية تلقائية وفق `docs/OWNER_AUTOMATIC_ART_APPROVAL_20261111.md`. المحاولات rejected محفوظة للتتبع ولا تدخل الخريطة. وجود سجل لا يثبت التكامل؛ تُراجع المقاسات والارتكاز والتثبيت والقيود في manifest. القيم الناقصة تبقى مجهولة، ولا تُختلق collision أو اتجاه أو قياسات.

سجل الخرائط الحالية مرفق في JSON؛ exact_path_map_references يرصد فقط التطابق الحرفي لمسار المصدر/المعاينة في latest.json، ولا يستنتج أن الصور غير المطابقة مستخدمة. لا يغيّر الفهرس خرائط أو يعين أصولًا نشطة.

الصور المنسوخة محليًا قد تكون في PR لم يدمج بعد؛ publication يوضح الفرع والرابط. تتحقق حالة الدمج من Git عند الاستخدام. لا تستبدل الصور بأسماء متشابهة ولا تفعّل البدائل تلقائيًا.

بعد كل تسليم: شغّل `python tools/source_art_catalog.py --root . --write` في مجلد المشروع الجامع، ثم `python tools/source_art_catalog.py --root . --check`. تحفظ الأداة فقط هذا الفهرس ودليله؛ لا تعدّل PNG أو manifests تاريخية. فهارس INDEX.md الآلية تُحدّث على main وفق سير المشروع.

العدد: 109 مصادر مختارة و34 محاولات مرفوضة في 30 manifests.

| ART | القطعة | الفئة | الاختيار | المصدر |
| --- | --- | --- | --- | --- |
| ART-0002 | hero_cloud_01 | background | selected | [hero_cloud_01.png](../assets_hd/background/drifting_clouds/v001/hero_cloud_01.png) |
| ART-0002 | hero_cloud_02 | background | selected | [hero_cloud_02.png](../assets_hd/background/drifting_clouds/v001/hero_cloud_02.png) |
| ART-0002 | hero_cloud_03 | background | selected | [hero_cloud_03.png](../assets_hd/background/drifting_clouds/v001/hero_cloud_03.png) |
| ART-0003 | hero_cliff_foam_01 | background | selected | [hero_cliff_foam_01.png](../assets_hd/background/cliff_foam_loop/v001/hero_cliff_foam_01.png) |
| ART-0003 | hero_cliff_foam_02 | background | selected | [hero_cliff_foam_02.png](../assets_hd/background/cliff_foam_loop/v001/hero_cliff_foam_02.png) |
| ART-0003 | hero_cliff_foam_03 | background | selected | [hero_cliff_foam_03.png](../assets_hd/background/cliff_foam_loop/v001/hero_cliff_foam_03.png) |
| ART-0003 | hero_cliff_foam_04 | background | selected | [hero_cliff_foam_04.png](../assets_hd/background/cliff_foam_loop/v001/hero_cliff_foam_04.png) |
| ART-0005 | hero_compass_wood_door_south | architecture | selected | [hero_compass_wood_door_south.png](../assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_south.png) |
| ART-0005 | hero_compass_wood_door_north | architecture | selected | [hero_compass_wood_door_north.png](../assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_north.png) |
| ART-0005 | hero_compass_wood_door_east | architecture | selected | [hero_compass_wood_door_east.png](../assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_east.png) |
| ART-0005 | hero_compass_wood_door_west | architecture | selected | [hero_compass_wood_door_west.png](../assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_west.png) |
| ART-0006 | hero_stone_sphere_finial | architecture | selected | [hero_stone_sphere_finial.png](../assets_hd/architecture/sphere_stair_post/v001/hero_stone_sphere_finial.png) |
| ART-0006 | hero_stone_sphere_finial_attempt_01 | architecture | rejected | [hero_stone_sphere_finial_attempt_01.png](../assets_hd/architecture/sphere_stair_post/v001/rejected/hero_stone_sphere_finial_attempt_01.png) |
| ART-0006 | hero_stone_sphere_finial_attempt_02 | architecture | rejected | [hero_stone_sphere_finial_attempt_02.png](../assets_hd/architecture/sphere_stair_post/v001/rejected/hero_stone_sphere_finial_attempt_02.png) |
| ART-0008 | hero_headboard_shelf_south | furniture | selected | [hero_headboard_shelf_south.png](../assets_hd/furniture/headboard_shelf/v001/hero_headboard_shelf_south.png) |
| ART-0008 | hero_headboard_shelf_south_attempt_01 | furniture | rejected | [hero_headboard_shelf_south_attempt_01.png](../assets_hd/furniture/headboard_shelf/v001/rejected/hero_headboard_shelf_south_attempt_01.png) |
| ART-0011 | hero_blue_white_planter | plants | selected | [hero_blue_white_planter.png](../assets_hd/plants/blue_white_planter/v001/hero_blue_white_planter.png) |
| ART-0011 | hero_blue_white_planter_attempt_01 | plants | rejected | [hero_blue_white_planter_attempt_01.png](../assets_hd/plants/blue_white_planter/v001/rejected/hero_blue_white_planter_attempt_01.png) |
| ART-0015 | hero_study_blue_rug | decor | selected | [hero_study_blue_rug.png](../assets_hd/decor/hero_room_rugs/v001/hero_study_blue_rug.png) |
| ART-0015 | hero_bedroom_blue_rug | decor | selected | [hero_bedroom_blue_rug.png](../assets_hd/decor/hero_room_rugs/v001/hero_bedroom_blue_rug.png) |
| ART-0015 | hero_study_blue_rug_attempt_01 | decor | rejected | [hero_study_blue_rug_attempt_01.png](../assets_hd/decor/hero_room_rugs/v001/rejected/hero_study_blue_rug_attempt_01.png) |
| ART-0015 | hero_bedroom_blue_rug_attempt_01 | decor | rejected | [hero_bedroom_blue_rug_attempt_01.png](../assets_hd/decor/hero_room_rugs/v001/rejected/hero_bedroom_blue_rug_attempt_01.png) |
| ART-0015 | hero_study_blue_rug_attempt_02 | decor | rejected | [hero_study_blue_rug_attempt_02.png](../assets_hd/decor/hero_room_rugs/v001/rejected/hero_study_blue_rug_attempt_02.png) |
| ART-0015 | hero_bedroom_blue_rug_attempt_02 | decor | rejected | [hero_bedroom_blue_rug_attempt_02.png](../assets_hd/decor/hero_room_rugs/v001/rejected/hero_bedroom_blue_rug_attempt_02.png) |
| ART-0019 | hero_study_table_south | furniture | selected | [hero_study_table_south.png](../assets_hd/furniture/study_table_views/v001/hero_study_table_south.png) |
| ART-0019 | hero_study_table_north | furniture | selected | [hero_study_table_north.png](../assets_hd/furniture/study_table_views/v001/hero_study_table_north.png) |
| ART-0019 | hero_study_table_east | furniture | selected | [hero_study_table_east.png](../assets_hd/furniture/study_table_views/v001/hero_study_table_east.png) |
| ART-0019 | hero_study_table_west | furniture | selected | [hero_study_table_west.png](../assets_hd/furniture/study_table_views/v001/hero_study_table_west.png) |
| ART-0019 | hero_study_table_south_attempt_01 | furniture | rejected | [hero_study_table_south_attempt_01.png](../assets_hd/furniture/study_table_views/v001/rejected/hero_study_table_south_attempt_01.png) |
| ART-0020 | hero_study_bookshelf_south | furniture | selected | [hero_study_bookshelf_south.png](../assets_hd/furniture/study_bookshelf_views/v001/hero_study_bookshelf_south.png) |
| ART-0020 | hero_study_bookshelf_north | furniture | selected | [hero_study_bookshelf_north.png](../assets_hd/furniture/study_bookshelf_views/v001/hero_study_bookshelf_north.png) |
| ART-0020 | hero_study_bookshelf_north_attempt_01 | furniture | rejected | [hero_study_bookshelf_north_attempt_01.png](../assets_hd/furniture/study_bookshelf_views/v001/rejected/hero_study_bookshelf_north_attempt_01.png) |
| ART-0021 | hero_study_chest_south | furniture | selected | [hero_study_chest_south.png](../assets_hd/furniture/study_chest_views/v001/hero_study_chest_south.png) |
| ART-0021 | hero_study_chest_north | furniture | selected | [hero_study_chest_north.png](../assets_hd/furniture/study_chest_views/v001/hero_study_chest_north.png) |
| ART-0021 | hero_study_chest_east | furniture | selected | [hero_study_chest_east.png](../assets_hd/furniture/study_chest_views/v001/hero_study_chest_east.png) |
| ART-0021 | hero_study_chest_west | furniture | selected | [hero_study_chest_west.png](../assets_hd/furniture/study_chest_views/v001/hero_study_chest_west.png) |
| ART-0021 | hero_study_chest_west_attempt_01 | furniture | rejected | [hero_study_chest_west_attempt_01.png](../assets_hd/furniture/study_chest_views/v001/rejected/hero_study_chest_west_attempt_01.png) |
| ART-0022 | hero_compass_floor_inlay | decor | selected | [hero_compass_floor_inlay.png](../assets_hd/decor/compass_inlay/v001/hero_compass_floor_inlay.png) |
| ART-0023 | hero_side_banner_east_facing_short | decor | selected | [hero_side_banner_east_facing_short.png](../assets_hd/decor/side_banners/v001/hero_side_banner_east_facing_short.png) |
| ART-0023 | hero_side_banner_east_facing_long | decor | selected | [hero_side_banner_east_facing_long.png](../assets_hd/decor/side_banners/v001/hero_side_banner_east_facing_long.png) |
| ART-0023 | hero_side_banner_west_facing_long | decor | selected | [hero_side_banner_west_facing_long.png](../assets_hd/decor/side_banners/v001/hero_side_banner_west_facing_long.png) |
| ART-0023 | hero_wall_lantern_west | lighting | selected | [hero_wall_lantern_west.png](../assets_hd/lighting/west_wall_lantern/v001/hero_wall_lantern_west.png) |
| ART-0023 | hero_side_banner_east_facing_long_attempt_01 | decor | rejected | [hero_side_banner_east_facing_long_attempt_01.png](../assets_hd/decor/side_banners/v001/rejected/hero_side_banner_east_facing_long_attempt_01.png) |
| ART-0023 | hero_side_banner_east_facing_short_attempt_01 | decor | rejected | [hero_side_banner_east_facing_short_attempt_01.png](../assets_hd/decor/side_banners/v001/rejected/hero_side_banner_east_facing_short_attempt_01.png) |
| ART-0024 | hero_rope_post | decor | selected | [hero_rope_post.png](../assets_hd/decor/rope_post_fence/v001/hero_rope_post.png) |
| ART-0024 | hero_rope_swag_west_rail | decor | selected | [hero_rope_swag_west_rail.png](../assets_hd/decor/rope_post_fence/v001/hero_rope_swag_west_rail.png) |
| ART-0024 | hero_rope_swag_east_rail | decor | selected | [hero_rope_swag_east_rail.png](../assets_hd/decor/rope_post_fence/v001/hero_rope_swag_east_rail.png) |
| ART-0025 | hero_entrance_stairs_south | architecture | selected | [hero_entrance_stairs_south.png](../assets_hd/architecture/entrance_stairs/v001/hero_entrance_stairs_south.png) |
| ART-0032 | wall_straight_long_a | architecture | selected | [wall_straight_long_a.png](../assets_hd/architecture/connected_ruin_walls/v001/wall_straight_long_a.png) |
| ART-0032 | wall_straight_long_b | architecture | selected | [wall_straight_long_b.png](../assets_hd/architecture/connected_ruin_walls/v001/wall_straight_long_b.png) |
| ART-0032 | wall_corner_outer_left | architecture | selected | [wall_corner_outer_left.png](../assets_hd/architecture/connected_ruin_walls/v001/wall_corner_outer_left.png) |
| ART-0032 | wall_corner_outer_right | architecture | selected | [wall_corner_outer_right.png](../assets_hd/architecture/connected_ruin_walls/v001/wall_corner_outer_right.png) |
| ART-0032 | wall_corner_inner_left | architecture | selected | [wall_corner_inner_left.png](../assets_hd/architecture/connected_ruin_walls/v001/wall_corner_inner_left.png) |
| ART-0032 | wall_corner_inner_right | architecture | selected | [wall_corner_inner_right.png](../assets_hd/architecture/connected_ruin_walls/v001/wall_corner_inner_right.png) |
| ART-0032 | wall_side_left_run | architecture | selected | [wall_side_left_run.png](../assets_hd/architecture/connected_ruin_walls/v001/wall_side_left_run.png) |
| ART-0032 | wall_side_right_run | architecture | selected | [wall_side_right_run.png](../assets_hd/architecture/connected_ruin_walls/v001/wall_side_right_run.png) |
| ART-0032 | parapet_cap_run | architecture | selected | [parapet_cap_run.png](../assets_hd/architecture/connected_ruin_walls/v001/parapet_cap_run.png) |
| ART-0032 | wall_corner_outer_left_attempt_01 | architecture | rejected | [wall_corner_outer_left_attempt_01.png](../assets_hd/architecture/connected_ruin_walls/v001/rejected/wall_corner_outer_left_attempt_01.png) |
| ART-0032 | wall_corner_outer_right_attempt_01 | architecture | rejected | [wall_corner_outer_right_attempt_01.png](../assets_hd/architecture/connected_ruin_walls/v001/rejected/wall_corner_outer_right_attempt_01.png) |
| ART-0032 | wall_side_left_run_attempt_01 | architecture | rejected | [wall_side_left_run_attempt_01.png](../assets_hd/architecture/connected_ruin_walls/v001/rejected/wall_side_left_run_attempt_01.png) |
| ART-0032 | wall_side_right_run_attempt_01 | architecture | rejected | [wall_side_right_run_attempt_01.png](../assets_hd/architecture/connected_ruin_walls/v001/rejected/wall_side_right_run_attempt_01.png) |
| ART-0033 | terrace_edge_straight | background | selected | [terrace_edge_straight.png](../assets_hd/background/terrace_cliff/v001/terrace_edge_straight.png) |
| ART-0033 | terrace_edge_corner_left | background | selected | [terrace_edge_corner_left.png](../assets_hd/background/terrace_cliff/v001/terrace_edge_corner_left.png) |
| ART-0033 | terrace_edge_corner_right | background | selected | [terrace_edge_corner_right.png](../assets_hd/background/terrace_cliff/v001/terrace_edge_corner_right.png) |
| ART-0033 | cliff_face_front_a | background | selected | [cliff_face_front_a.png](../assets_hd/background/terrace_cliff/v001/cliff_face_front_a.png) |
| ART-0033 | cliff_face_front_b | background | selected | [cliff_face_front_b.png](../assets_hd/background/terrace_cliff/v001/cliff_face_front_b.png) |
| ART-0033 | cliff_face_front_c | background | selected | [cliff_face_front_c.png](../assets_hd/background/terrace_cliff/v001/cliff_face_front_c.png) |
| ART-0033 | cliff_rubble_cluster | background | selected | [cliff_rubble_cluster.png](../assets_hd/background/terrace_cliff/v001/cliff_rubble_cluster.png) |
| ART-0033 | foam_at_cliff_base | background | selected | [foam_at_cliff_base.png](../assets_hd/background/terrace_cliff/v001/foam_at_cliff_base.png) |
| ART-0034 | sea_stack_tall_a | background | selected | [sea_stack_tall_a.png](../assets_hd/background/sea_coast/v001/sea_stack_tall_a.png) |
| ART-0034 | sea_stack_tall_b | background | selected | [sea_stack_tall_b.png](../assets_hd/background/sea_coast/v001/sea_stack_tall_b.png) |
| ART-0034 | sea_stack_tall_c | background | selected | [sea_stack_tall_c.png](../assets_hd/background/sea_coast/v001/sea_stack_tall_c.png) |
| ART-0034 | rock_arch_far_left | background | selected | [rock_arch_far_left.png](../assets_hd/background/sea_coast/v001/rock_arch_far_left.png) |
| ART-0034 | rock_arch_far_right | background | selected | [rock_arch_far_right.png](../assets_hd/background/sea_coast/v001/rock_arch_far_right.png) |
| ART-0034 | horizon_haze_strip | background | selected | [horizon_haze_strip.png](../assets_hd/background/sea_coast/v001/horizon_haze_strip.png) |
| ART-0034 | foam_patch_a | background | selected | [foam_patch_a.png](../assets_hd/background/sea_coast/v001/foam_patch_a.png) |
| ART-0034 | foam_patch_b | background | selected | [foam_patch_b.png](../assets_hd/background/sea_coast/v001/foam_patch_b.png) |
| ART-0034 | sea_stack_tall_b_attempt_01 | background | rejected | [sea_stack_tall_b_attempt_01.png](../assets_hd/background/sea_coast/v001/rejected/sea_stack_tall_b_attempt_01.png) |
| ART-0035 | planter_stone_flowers_large | plants | selected | [planter_stone_flowers_large.png](../assets_hd/plants/coastal_garden/v001/planter_stone_flowers_large.png) |
| ART-0035 | planter_stone_flowers_medium | plants | selected | [planter_stone_flowers_medium.png](../assets_hd/plants/coastal_garden/v001/planter_stone_flowers_medium.png) |
| ART-0035 | palm_clump_front_left | plants | selected | [palm_clump_front_left.png](../assets_hd/plants/coastal_garden/v001/palm_clump_front_left.png) |
| ART-0035 | palm_clump_front_right | plants | selected | [palm_clump_front_right.png](../assets_hd/plants/coastal_garden/v001/palm_clump_front_right.png) |
| ART-0035 | flower_mound_white | plants | selected | [flower_mound_white.png](../assets_hd/plants/coastal_garden/v001/flower_mound_white.png) |
| ART-0035 | flower_mound_blue | plants | selected | [flower_mound_blue.png](../assets_hd/plants/coastal_garden/v001/flower_mound_blue.png) |
| ART-0035 | ivy_tuft_wall_a | plants | selected | [ivy_tuft_wall_a.png](../assets_hd/plants/coastal_garden/v001/ivy_tuft_wall_a.png) |
| ART-0035 | ivy_tuft_wall_b | plants | selected | [ivy_tuft_wall_b.png](../assets_hd/plants/coastal_garden/v001/ivy_tuft_wall_b.png) |
| ART-0035 | hanging_vine_long | plants | selected | [hanging_vine_long.png](../assets_hd/plants/coastal_garden/v001/hanging_vine_long.png) |
| ART-0037 | sea_light_lattice_tile_attempt_01 | background | rejected | [sea_light_lattice_tile_attempt_01.png](../assets_hd/background/sea_light_lattice/v001/rejected/sea_light_lattice_tile_attempt_01.png) |
| ART-0037 | sea_light_lattice_tile_attempt_02 | background | rejected | [sea_light_lattice_tile_attempt_02.png](../assets_hd/background/sea_light_lattice/v001/rejected/sea_light_lattice_tile_attempt_02.png) |
| ART-0038 | wall_straight_window_opening | architecture | selected | [wall_straight_window_opening.png](../assets_hd/architecture/window_wall/v001/wall_straight_window_opening.png) |
| ART-0038 | wall_straight_window_opening_attempt_01 | architecture | rejected | [wall_straight_window_opening_attempt_01.png](../assets_hd/architecture/window_wall/v001/rejected/wall_straight_window_opening_attempt_01.png) |
| ART-0038 | wall_straight_window_opening | architecture | selected | [wall_straight_window_opening.png](../assets_hd/architecture/window_wall/v002/wall_straight_window_opening.png) |
| ART-0038 | wall_straight_window_opening_attempt_03 | architecture | rejected | [wall_straight_window_opening_attempt_03.png](../assets_hd/architecture/window_wall/v002/rejected/wall_straight_window_opening_attempt_03.png) |
| ART-0039 | study_wooden_stool | furniture | selected | [study_wooden_stool.png](../assets_hd/furniture/study_stool/v001/study_wooden_stool.png) |
| ART-0040 | hero_wall_lantern_east | lighting | selected | [hero_wall_lantern_east.png](../assets_hd/lighting/east_wall_lantern/v001/hero_wall_lantern_east.png) |
| ART-0040 | hero_wall_lantern_east_attempt_01 | lighting | rejected | [hero_wall_lantern_east_attempt_01.png](../assets_hd/lighting/east_wall_lantern/v001/rejected/hero_wall_lantern_east_attempt_01.png) |
| ART-0041 | field_grass_a | floor | selected | [field_grass_a.png](../assets_hd/floor/skirmish_field/v001/field_grass_a.png) |
| ART-0041 | field_grass_b | floor | selected | [field_grass_b.png](../assets_hd/floor/skirmish_field/v001/field_grass_b.png) |
| ART-0041 | field_rock_block | props | selected | [field_rock_block.png](../assets_hd/props/skirmish_rock/v001/field_rock_block.png) |
| ART-0041 | marker_move | decor | selected | [marker_move.png](../assets_hd/decor/skirmish_markers/v001/marker_move.png) |
| ART-0041 | marker_target | decor | selected | [marker_target.png](../assets_hd/decor/skirmish_markers/v001/marker_target.png) |
| ART-0041 | marker_active | decor | selected | [marker_active.png](../assets_hd/decor/skirmish_markers/v001/marker_active.png) |
| ART-0041 | marker_active_attempt_01 | decor | rejected | [marker_active_attempt_01.png](../assets_hd/decor/skirmish_markers/v001/rejected/marker_active_attempt_01.png) |
| ART-0042 | hero_rear_left_ruined_wall_window | architecture | selected | [hero_rear_left_ruined_wall_window.png](../assets_hd/architecture/rear_left_window_wall/v001/hero_rear_left_ruined_wall_window.png) |
| ART-0042 | hero_rear_left_ruined_wall_window_attempt_01 | architecture | rejected | [hero_rear_left_ruined_wall_window_attempt_01.png](../assets_hd/architecture/rear_left_window_wall/v001/rejected/hero_rear_left_ruined_wall_window_attempt_01.png) |
| ART-0043 | hero_rear_right_wall_arched_door_niche | architecture | selected | [hero_rear_right_wall_arched_door_niche.png](../assets_hd/architecture/rear_right_door_niche/v001/hero_rear_right_wall_arched_door_niche.png) |
| ART-0043 | hero_rear_right_wall_arched_door_niche_attempt_01 | architecture | rejected | [hero_rear_right_wall_arched_door_niche_attempt_01.png](../assets_hd/architecture/rear_right_door_niche/v001/rejected/hero_rear_right_wall_arched_door_niche_attempt_01.png) |
| ART-0043 | hero_rear_right_wall_arched_door_niche_attempt_02 | architecture | rejected | [hero_rear_right_wall_arched_door_niche_attempt_02.png](../assets_hd/architecture/rear_right_door_niche/v001/rejected/hero_rear_right_wall_arched_door_niche_attempt_02.png) |
| ART-0044 | hero_west_curved_side_wall_attempt_01 | architecture | rejected | [hero_west_curved_side_wall_attempt_01.png](../assets_hd/architecture/curved_west_side_wall/v001/rejected/hero_west_curved_side_wall_attempt_01.png) |
| ART-0044 | hero_west_curved_side_wall_attempt_02 | architecture | rejected | [hero_west_curved_side_wall_attempt_02.png](../assets_hd/architecture/curved_west_side_wall/v001/rejected/hero_west_curved_side_wall_attempt_02.png) |
| ART-0045 | hero_east_curved_side_wall_attempt_01 | architecture | rejected | [hero_east_curved_side_wall_attempt_01.png](../assets_hd/architecture/curved_east_side_wall/v001/rejected/hero_east_curved_side_wall_attempt_01.png) |
| ART-0029 | hero_golden_cyclone_001 | character | selected | [hero_golden_cyclone_001.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_001.png) |
| ART-0029 | hero_golden_cyclone_002 | character | selected | [hero_golden_cyclone_002.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_002.png) |
| ART-0029 | hero_golden_cyclone_003 | character | selected | [hero_golden_cyclone_003.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_003.png) |
| ART-0029 | hero_golden_cyclone_004 | character | selected | [hero_golden_cyclone_004.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_004.png) |
| ART-0029 | hero_golden_cyclone_005 | character | selected | [hero_golden_cyclone_005.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_005.png) |
| ART-0029 | hero_golden_cyclone_006 | character | selected | [hero_golden_cyclone_006.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_006.png) |
| ART-0029 | hero_golden_cyclone_007 | character | selected | [hero_golden_cyclone_007.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_007.png) |
| ART-0029 | hero_golden_cyclone_008 | character | selected | [hero_golden_cyclone_008.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_008.png) |
| ART-0029 | hero_golden_cyclone_009 | character | selected | [hero_golden_cyclone_009.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_009.png) |
| ART-0029 | hero_golden_cyclone_010 | character | selected | [hero_golden_cyclone_010.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_010.png) |
| ART-0029 | hero_golden_cyclone_011 | character | selected | [hero_golden_cyclone_011.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_011.png) |
| ART-0029 | hero_golden_cyclone_012 | character | selected | [hero_golden_cyclone_012.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_012.png) |
| ART-0029 | hero_golden_cyclone_013 | character | selected | [hero_golden_cyclone_013.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_013.png) |
| ART-0029 | hero_golden_cyclone_014 | character | selected | [hero_golden_cyclone_014.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_014.png) |
| ART-0029 | hero_golden_cyclone_015 | character | selected | [hero_golden_cyclone_015.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_015.png) |
| ART-0029 | hero_golden_cyclone_016 | character | selected | [hero_golden_cyclone_016.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_016.png) |
| ART-0029 | hero_golden_cyclone_017 | character | selected | [hero_golden_cyclone_017.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_017.png) |
| ART-0029 | hero_golden_cyclone_018 | character | selected | [hero_golden_cyclone_018.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_018.png) |
| ART-0029 | hero_golden_cyclone_019 | character | selected | [hero_golden_cyclone_019.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_019.png) |
| ART-0029 | hero_golden_cyclone_020 | character | selected | [hero_golden_cyclone_020.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_020.png) |
| ART-0029 | hero_golden_cyclone_021 | character | selected | [hero_golden_cyclone_021.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_021.png) |
| ART-0029 | hero_golden_cyclone_022 | character | selected | [hero_golden_cyclone_022.png](../assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_022.png) |
| ART-0029 | hero_golden_cyclone_005_attempt_01 | character | rejected | [hero_golden_cyclone_005_attempt_01.png](../assets/characters/hero/battle/golden_cyclone/v001/rejected_sources/hero_golden_cyclone_005_attempt_01.png) |
| ART-0029 | hero_golden_cyclone_015_attempt_01 | character | rejected | [hero_golden_cyclone_015_attempt_01.png](../assets/characters/hero/battle/golden_cyclone/v001/rejected_sources/hero_golden_cyclone_015_attempt_01.png) |
| ART-0029 | hero_golden_cyclone_022_attempt_01 | character | rejected | [hero_golden_cyclone_022_attempt_01.png](../assets/characters/hero/battle/golden_cyclone/v001/rejected_sources/hero_golden_cyclone_022_attempt_01.png) |
| ART-0029 | phantom_dash_multi_pose_rejected | character | rejected | [phantom_dash_multi_pose_rejected.png](../assets/characters/hero/battle/golden_cyclone/v001/rejected_sources/phantom_dash_multi_pose_rejected.png) |
| ART-0029 | golden_spinning_arc_001 | character | selected | [golden_spinning_arc_001.png](../assets/characters/hero/battle/golden_cyclone/v001/vfx/golden_spinning_arc_001.png) |
| ART-0029 | golden_energy_ring_001 | character | selected | [golden_energy_ring_001.png](../assets/characters/hero/battle/golden_cyclone/v001/vfx/golden_energy_ring_001.png) |
| ART-0029 | golden_motion_trail_001 | character | selected | [golden_motion_trail_001.png](../assets/characters/hero/battle/golden_cyclone/v001/vfx/golden_motion_trail_001.png) |
| ART-0029 | golden_impact_sparks_001 | character | selected | [golden_impact_sparks_001.png](../assets/characters/hero/battle/golden_cyclone/v001/vfx/golden_impact_sparks_001.png) |
| ART-0029 | golden_final_flash_001 | character | selected | [golden_final_flash_001.png](../assets/characters/hero/battle/golden_cyclone/v001/vfx/golden_final_flash_001.png) |
| ART-0029 | cyclone_ground_dust_001 | character | selected | [cyclone_ground_dust_001.png](../assets/characters/hero/battle/golden_cyclone/v001/vfx/cyclone_ground_dust_001.png) |
