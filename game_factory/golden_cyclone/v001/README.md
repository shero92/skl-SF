# Golden Cyclone — دليل التسليم والاستخدام

Agent: codex. Task: TASK-0074. Art request: ART-0029. الإصدار v001، تحديث 2026-11-09.

جميع المسارات نسبية لجذر المشروع H:/shining force/skl-SF. الحالة needs_review؛ لا موافقة فنية من المالك ولا تفعيل في سجل الشخصيات أو القتال الإنتاجي. تطوير الكود على الفرع codex/golden-cyclone-resume داخل .worktrees/TASK-0074-resume؛ نسخ تسليم الرسوم والبيانات محفوظة كذلك في جذر المشروع بطلب المالك.

## الملفات وأسماؤها

| الاستخدام | المسار |
|---|---|
| 22 مصدر جسم مستقل، RGBA 1254×1254 | assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_001.png حتى 022.png |
| 22 مشتق لعبة، RGBA 384×384 | assets/characters/hero/battle/golden_cyclone/v001/game_frames/hero_golden_cyclone_001.png حتى 022.png |
| ستة مؤثرات منفصلة | assets/characters/hero/battle/golden_cyclone/v001/vfx/ |
| المحاولات المرفوضة المحفوظة | assets/characters/hero/battle/golden_cyclone/v001/rejected_sources/ |
| صور بيئة وسيفين وهدف معاينة موجود أصلًا، منسوخة ببصماتها | assets/characters/hero/battle/golden_cyclone/v001/preview_dependencies/ |
| معلومات كل مصدر ومرحلته وتوقيته وبصمته وطلبه | game_factory/golden_cyclone/v001/manifest.json |
| مسارات الصور، الأبعاد، الدور والبصمات لجميع ملفات التسليم | game_factory/golden_cyclone/v001/metadata/asset_inventory.json |
| قياسات اليد والأرض من المصدر | game_factory/golden_cyclone/v001/metadata/source_annotations.json |
| بيانات دقة اللعبة ونقاط السلاح ومدة كل إطار | game_factory/golden_cyclone/v001/metadata/review_assets.json |
| معرفات VFX، نقطة الأصل، المقياس والطبقة | game_factory/golden_cyclone/v001/metadata/vfx.json |
| طلب مستقل لكل إطار ولكل مؤثر | game_factory/golden_cyclone/v001/requests/ |
| Sprite Sheet مجمّع من المشتقات الفردية وليس مصدر رسم | game_factory/golden_cyclone/v001/previews/hero_golden_cyclone_sprite_sheet.png |
| GIF من التقاط Godot الفعلي | game_factory/golden_cyclone/v001/previews/hero_golden_cyclone.gif |
| التقاط بطيء بلا مؤثرات وبلا حركة كاميرا | game_factory/golden_cyclone/v001/previews/hero_golden_cyclone_slow_no_effects.gif |

المؤثرات: golden_spinning_arc_001، golden_energy_ring_001، golden_motion_trail_001، golden_impact_sparks_001، golden_final_flash_001، cyclone_ground_dust_001. كل منها PNG مستقل؛ لا مؤثر أو سيف مدمج في الجسم. تصف space نظام الإحداثيات وanchor_normalized نقطة تثبيت الصورة. أسماء الملفات ثابتة؛ لا تستخدم أسماء exec-* كمعرفات أصول.

## للوكيل التالي

ابدأ من manifest.json للمصادر وmetadata/review_assets.json للمشتقات. وحدة الدوران بالدرجات، التوقيت بالميلي ثانية، الإحداثيات بالبكسل نسبة إلى أعلى يسار canvas المعني. مصادر 1254px ونسخ 384px لها إحداثيات مختلفة؛ لا تنقل نقاط اليد بينهما دون التحويل المسجل. المشتقات تستخدم مقياسًا موحدًا 0.22 وارتكازًا أرضيًا [192,352]؛ لا ملاءمة حجم مستقلة لكل إطار. لا تعدّل المصدر لتصحيح ارتكاز المشهد.

الصورة الأصلية محفوظة في المشروع وبصمتها لا تتغير أثناء التصدير. مجلد .codex/generated_images مخرج مؤقت تفرضه الأداة وليس موقع تسليم ولا اعتمادًا تشغيليًا. ملفات المشروع تعمل دون الوصول إليه؛ لا تنسخ منه وقت تشغيل Godot.

المشهد المستقل: res://scenes/battle/golden_cyclone_preview.tscn. افتحه في نسخة العمل المذكورة أعلاه؛ تعديل كود الإنتاج ينتظر مراجعة الفرع. يدعم التشغيل والإيقاف والتصفح إطارًا بإطار والسحب وتبديل السيفين والكاميرا وVFX وسرعة 0.25x والإلغاء. الواجهة play_attack("golden_cyclone", hero, defender) تخص مشهد المراجعة؛ لا تدّعي اكتمال تكامل TASK-0087. الهدف Hero موجود لغرض التدريب؛ لم تُنشأ شخصية وحش بديلة.

أوامر إعادة الإنشاء من نسخة العمل:
- python tools/golden_cyclone_assets.py validate
- python tools/golden_cyclone_assets.py build
- python tools/golden_cyclone_assets.py request-capture
- شغّل المشهد في Godot؛ يلتقط PNGs من الـviewport ثم يغلق نفسه.
- python tools/golden_cyclone_assets.py encode-godot

مدة الحركة 1500ms تشمل توقف اصطدام 70ms عند 930ms، وحدث عرض واحد؛ لا حساب ضرر جديد. لقطات GIF الطبيعية 1700ms والبطيئة 6800ms وتشمل مهلة استعداد 200ms. الدليل في previews/godot_capture_receipt.json وpreviews/weapon_swap_verification.json وqa/verification_summary.md. اللقطات الخام قابلة لإعادة الإنشاء ومحفوظة محليًا؛ لا يلزم إدراجها كلها في Git.

يلزم اعتماد المالك للهوية وتتابع الريش والملابس والإيقاع وجودة المشتقات وحجب اليد؛ تطابق النقاط حسابيًا لا يثبت جودة الحجب أو اتصال الحركة بصريًا. لا تغيّر owner_approved أو السجل النشط تلقائيًا. ورقة Phantom Dash متعددة الوضعيات محفوظة تحت rejected_sources/phantom_dash_multi_pose_rejected.png للأرشفة فقط، ويمنع اقتطاع إطارات إنتاجية منها.

## اعتماد المالك 2026-11-10

وافق المالك على جميع أصول حزمة Golden Cyclone المسلمة وعلى الدمج. owner_approved=true في manifest؛ أوصاف needs_review السابقة توثق حالة التسليم وقت إنتاجه. الموافقة تخص الأصول المسلمة، ولا تشمل المحاولات المرفوضة أو ملفات غير مولدة. ربط هجوم الإنتاج في TASK-0087 منفصل ولم يُدّع اكتماله.
