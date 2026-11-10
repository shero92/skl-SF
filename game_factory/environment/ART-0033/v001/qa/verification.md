# فحص ART-0033 — 2026-11-10

- 8 PNG مستقلة وبصمات فريدة، RGBA وشفافية حقيقية وحدود alpha128 داخل canvas بلا قص.
- 8 مشتقات Nearest Neighbor منفصلة؛ بصمات المصادر الأصلية لم تتغير.
- لقطة Godot 4.7.2 فعلية 1024×1024 عبر ANGLE/NVIDIA RTX3070؛ receipt يثبت بصمة manifest والصورة والعدد 8.
- فُحصت اللوحة بصريًا: الحافة الضحلة وواجهات الجرف العميقة متميزة، الركام منفصل، والزبد لا يحتوي صخورًا أو مستطيل محيط. لا خلفية ملونة ظاهرة عند التركيب على خلفية محايدة.
- python -u tools/run_tests.py --changed --base origin/main --timeout 120: 73/73 passed، ومنها Godot import وmap smoke.
- تحذيرات editor_data وuser://log وshader cache في sandbox لم تمنع الالتقاط أو الفحوص. لم تعدّل إعدادات الصلاحيات أو العرض لمعالجة الرسوم.
- معايرة ارتفاعات واجهات الجرف، تطابق النهايات، footprint، runtime_scale وconnection_sockets داخل الغرفة لم تنفذ؛ القيم المقترحة معلّمة، والمجهول null. لا collision أو seam tiling مثبت ولا اعتماد فني تلقائي.
- لا تعديل للأصول المعتمدة أو الخريطة أو سجل الإنتاج. الصور الجديدة needs_review. Agent: codex، builtin_image_gen؛ نموذج الصورة غير مكشوف والاستهلاك والتكلفة غير المقاسين unknown.
