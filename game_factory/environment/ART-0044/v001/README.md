# ART-0044 — مرشحات جدار جانبي منحني

الحالة requested / needs_regeneration، وعدد الأصول الإنتاجية المؤهلة صفر. الموافقة البصرية التلقائية مسجلة، ولا تلغي إخفاق شرط دقة4x. لا يوجد أصل إنتاجي في requested_output_path ولا تفعيل في الخرائط.

| المرشح | الأبعاد الفعلية | الحد الأدنى المطلوب | كثافة المصدر | SHA-256 |
| --- | --- | --- | --- | --- |
| hero_west_curved_side_wall_attempt_01 | [877, 1794] | [920, 1880] | [3.8130434782608695, 3.8170212765957445] | 8ba1f9ffe11509a62ab89cb16abb8db71a9960220f5179a54b23d73334d0ef19 |
| hero_west_curved_side_wall_attempt_02 | [878, 1792] | [920, 1880] | [3.8173913043478263, 3.8127659574468087] | 69a3e8d903e7371f666ff965a6d19e35de6d87517ebb2916a7581251b20e29c6 |

الأداة built-in image_gen؛ النموذج والكلفة غير مقاسين. الغربي والشرقي رسمان مستقلان، بضوء أعلى اليسار؛ لا تكبير أو عكس أو تدوير أو قص من Sheet. القصاصات المرجعية للتكوين والمادة فقط.

طُلب مقاس أكبر صراحة، لكن المخرجات الفعلية بقيت دون الحد. maximum_native_canvas_at4x معلومة حسابية فقط وليست اعتمادًا لتصغير المقاس المطلوب. تحسن هامش الأمان العلوي للغربي في المحاولة الثانية. لا تُعد أي صورة ready.

Godot: godot_candidate_review.png لقطة viewport فعلية بالحجم المطلوب مع تحذير إخفاق4x. نجاح حفظ الأدلة والاختبارات لا يعني اجتياز شرط الرسم. الوصلات والتصادم والمواضع داخل الغرفة غير مختبرة.

إعادة القياس: python game_factory/environment/curved_side_walls_20261111/prepare_review.py
الالتقاط: Godot --path . --rendering-method gl_compatibility --script res://game_factory/environment/curved_side_walls_20261111/review.gd
التحقق: python game_factory/environment/curved_side_walls_20261111/verify_candidates.py

الملفات في H:/shining force/skl-SF/.worktrees/art-curved-side-walls، الفرع codex/art-0044-0045-side-walls. لم يُكتب إلى مجلد main للمالك. يلزم مصدر حقيقي بالدقة الدنيا المحددة لإكمال المهمة؛ لا إعادة تصنيف المرشح الحالي كأصل مؤهل.
