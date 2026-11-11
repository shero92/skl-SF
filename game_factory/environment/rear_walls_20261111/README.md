# TASK-0156 — الجداران الخلفيان

ART-0042: جدار أيسر متدرج بنافذة مربعة شفافة. ART-0043: جدار أيمن متدرج بتجويف مقوس وباب خشبي مغلق. مصدران نهائيان مستقلان وخمس طلبات image_gen؛ ثلاث محاولات سابقة محفوظة. لا صور مركبة استُخرجت منها الأصول.

المراجع وقصاصات المقارنة في الطلبات؛ لا تُستخدم كأصول لعبة. مصدر كل ملف وبصمته ومقاسه والطلب والحالة والقيود موثقة في manifest لكل ART. ملف التسليم يتضمن request_id وfiles[path,sha256] المطابقين للطلب. الموافقة البصرية تلقائية؛ التفعيل وتصادمات الجدران ووصلها بالقوس مرحلة أخرى.

الفهرس هنا يجمع بيانات المصدر المتاحة في نسخة العمل. احتُفظت محليًا بسجل ART-0040 من PR179 كسياق تدقيق للكتالوج فقط؛ لم يُعد إنتاجه أو نسخه في هذا الالتزام. يتضمن الكتالوج محدد فرعه لحين دمج PR179. عند دمج الفرعين، يُعاد فحص الكتالوج من checkout المجمع. هذه الملفات بقيت داخل worktree وفق TASK-0162 ولم تُنسخ إلى main غير الملتزم.

## المصادر والمحاولات

| الملف | SHA-256 | الاختيار / السبب |
| --- | --- | --- |
| assets_hd/architecture/rear_left_window_wall/v001/hero_rear_left_ruined_wall_window.png | a43aa0bbad6d8246083b4e9424f25ad1b9aa3450926f107a8fe3ad3f8ac10667 | selected final |
| assets_hd/architecture/rear_left_window_wall/v001/rejected/hero_rear_left_ruined_wall_window_attempt_01.png | 8c4ec564a74a1a15d2b91518ca670448be1104dd0b288cd4f6c87828aaf80f3e | Window aperture too tall for the requested square; superseded by independently requested square-window edit. |
| assets_hd/architecture/rear_right_door_niche/v001/hero_rear_right_wall_arched_door_niche.png | e4c179693e6f56575cf0384b7e00aa00a7c8ea9905db34df323677e659a31735 | selected final |
| assets_hd/architecture/rear_right_door_niche/v001/rejected/hero_rear_right_wall_arched_door_niche_attempt_01.png | 8d238e9369ea16303862ec1ce64cf298cbcca80002e107e83deefca37f269c7e | Approximately11courses instead of requested7-8; superseded by separate coursing redraw. |
| assets_hd/architecture/rear_right_door_niche/v001/rejected/hero_rear_right_wall_arched_door_niche_attempt_02.png | b6e61bd0f6139f76434925de386ffa16f4f30f852c48f0b01b7740b8e65dc62b | Course count corrected but several blocks excessively wide; superseded by separate vertical-joint redraw. |
