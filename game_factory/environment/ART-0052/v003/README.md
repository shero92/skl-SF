# ART-0052 — Hidden Island, الخانات والصور الأصلية

Agent: codex. Tool: built-in image_gen. Model/tokens/cost unknown.

ست صور مستقلة1536×1024عرضها1:1؛ sourceRGBمحفوظ دون تعديل، وتسليم/runtimeRGBAمعalpha255وتطابقRGBبايتًا ببايت. الموافقة البصرية تلقائية، ومراجعة تكوين الخريطة لا تزال مستقلة.

| المشهد | master | SHA-256 master | SHA-256 RGBA runtime/delivery |
| --- | --- | --- | --- |
| hidden_island_home_descent | `assets_hd/background/hidden_island_grid_painted/v001/hidden_island_home_descent.png` | `4dbf2e2db86556001d1d0e2b087446483fac40ab4a4df42e9dff13389047c4c5` | `76cbf330b8993364f30a556f6e0c9e65235e5b9391278586ef1edf352770e951` |
| hidden_island_mossveil_edge | `assets_hd/background/hidden_island_grid_painted/v001/hidden_island_mossveil_edge.png` | `7a7c7ae71af73e19abc45590a870b0a9885bd35d1f958829e3500200512daa4b` | `f5a5a32f88f7ea9af27327c9d1752c9b749c52308342dc45c37e190782ad2f47` |
| hidden_island_mossveil_roots | `assets_hd/background/hidden_island_grid_painted/v001/hidden_island_mossveil_roots.png` | `416f25e99e40cbafc1c6f6f3d4ebc218b7eb46d434155ea916ce6c0267789f14` | `79f9ef17fdcf5146c8af1522945df0031a8ed9f019fd5d9dd70e85f394a40d8b` |
| hidden_island_stormwatch_ascent | `assets_hd/background/hidden_island_grid_painted/v001/hidden_island_stormwatch_ascent.png` | `e371887c2d4e3c472a8122490cb006b6296cce93ae3c7b6c361b680497f70ece` | `4a866006b360fc6dca34e796282d3e906c70f23bd194a91a0caf6564e913eb67` |
| hidden_island_stormwatch_overlook | `assets_hd/background/hidden_island_grid_painted/v001/hidden_island_stormwatch_overlook.png` | `2ebb18ee43e4dc8210f63ea6b783d0a966356f10964fe354debc4f7e6c4e2125` | `fff6242fc582a2dfa4240a222ec517c9bbf3d1e5ec2ab1af955fefe19c3a36ed` |
| hidden_island_bone_tide_shore | `assets_hd/background/hidden_island_grid_painted/v001/hidden_island_bone_tide_shore.png` | `9aebc761cbc2f2c8e6ded37d8facc0410cb126fb51d0ca78af9a156f8d4962d4` | `f3359b9ca1a5395c2b42e4c4f93e00b0ea5bda7a475c516c49a8cc8aeb09ef33` |

البيانات والتوقيت والبوابات والمشي: map_factory/painted_worlds/hidden_island/v001/world.json. تصديرRGBإلىRGBAلا يغير اللون أو الحجم، ولا يضاعف الإطارات. أصل اللوحة الكامل عند0,0فيruntime، وحقلoriginفيmasterيعني منتصف أسفل اللوحة، وليس قدم شخصية.

كل أوامر التوليد في requests/، واللقطات الفعلية godot_*.pngمعcapture_receipt.json. لا تعتمد علىC:/Users/.../.codex/generated_images. دليل القصة والتشغيل والتقييد: docs/PAINTED_COAST.md. النسخةالفعلية H:/shining force/skl-SF/.worktrees/seabreak-painted-world؛ الملفات تظهر في نسخة المالك بعد دمج الفرع.

v001/v002يحفظان8محاولات غير مختارة للقصة أو جغرافيا الدرج أو منظور الخانات. إجمالي الاستدعاءات14. لا تستعمل المحاولات غير المختارة فيworld.json. فهرس الصور161سجلًا، يربط الصور الست بالعالمhidden_island_openingعبرمسارruntime.

هذه الخلفيات مكتملة بقرار المالك؛ ليستقطعpropsللاستخراج ولاasset_idsلمصنعالأجزاء. المصدر4xللقطع لا يُدَّعى لهذه الصور الأصلية، ولا تكبير لإيهام دقة أعلى. nativeالمصدر موثق كما أنتجته الأداة.
