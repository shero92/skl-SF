# ART-0045 — مرشحات جدار جانبي منحني

الحالة requested / needs_regeneration، وعدد الأصول الإنتاجية المؤهلة صفر. الموافقة البصرية التلقائية مسجلة، ولا تلغي إخفاق شرط دقة4x. لا يوجد أصل إنتاجي في requested_output_path ولا تفعيل في الخرائط.

| المرشح | الأبعاد الفعلية | الحد الأدنى المطلوب | كثافة المصدر | SHA-256 |
| --- | --- | --- | --- | --- |
| hero_east_curved_side_wall_attempt_01 | [829, 1898] | [944, 2160] | [3.51271186440678, 3.5148148148148146] | 36aad081a47245286b761f297ee2281f58e7f4da2c818c0c7b1a38f0c48cadd1 |

الأداة built-in image_gen؛ النموذج والكلفة غير مقاسين. الغربي والشرقي رسمان مستقلان، بضوء أعلى اليسار؛ لا تكبير أو عكس أو تدوير أو قص من Sheet. القصاصات المرجعية للتكوين والمادة فقط.

طُلب مقاس أكبر صراحة، لكن المخرجات الفعلية بقيت دون الحد. maximum_native_canvas_at4x معلومة حسابية فقط وليست اعتمادًا لتصغير المقاس المطلوب. تحسن هامش الأمان العلوي للغربي في المحاولة الثانية. لا تُعد أي صورة ready.

Godot: godot_candidate_review.png لقطة viewport فعلية بالحجم المطلوب مع تحذير إخفاق4x. نجاح حفظ الأدلة والاختبارات لا يعني اجتياز شرط الرسم. الوصلات والتصادم والمواضع داخل الغرفة غير مختبرة.

إعادة القياس: python game_factory/environment/curved_side_walls_20261111/prepare_review.py
الالتقاط: Godot --path . --rendering-method gl_compatibility --script res://game_factory/environment/curved_side_walls_20261111/review.gd
التحقق: python game_factory/environment/curved_side_walls_20261111/verify_candidates.py

الملفات في H:/shining force/skl-SF/.worktrees/art-curved-side-walls، الفرع codex/art-0044-0045-side-walls. لم يُكتب إلى مجلد main للمالك. يلزم مصدر حقيقي بالدقة الدنيا المحددة لإكمال المهمة؛ لا إعادة تصنيف المرشح الحالي كأصل مؤهل.
