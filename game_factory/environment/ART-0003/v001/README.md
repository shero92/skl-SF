# ART-0003 — رغوة قاعدة الجرف

أربع مراحل مستقلة: هدوء، تقدم، تكسر، تراجع. المصادر محفوظة كاملة في assets_hd/background/cliff_foam_loop/v001. معاينة 96×48 ثابتة وNearest Neighbor، دون قص أو تحريك أو إعادة تحجيم لكل مرحلة على حدة. مصدر كل مرحلة طلب image_gen مستقل؛ الإطارات اللاحقة إعادة رسم مرجعية وليست نسخًا أو تحريكًا للصورة.

الموافقة البصرية تلقائية وفق docs/OWNER_AUTOMATIC_ART_APPROVAL_20261111.md. الحالة delivered؛ لا تفعيل في الخرائط ولا تعديل للأصول السابقة. 4fps / 250ms لكل إطار مأخوذة من cadence المحيط الحالي؛ الدورة ثانية واحدة.

تختلف الحدود السفلية للرغوة طبيعيًا خلال الموجة؛ لا تستخدم origin أسفل الحدود لتثبيت كل إطار، بل canvas وcontact_anchor الثابتين. مقاس 96×48 مقترح مراجعة، وقياس التماس على تضاريس الجرف الفعلية ما زال من عمل التكامل. لا collider ولا ظل مستقل ولا خلفية بحر مدمجة.

إعادة القياسات: python game_factory/environment/ART-0003/v001/prepare_review.py. الالتقاط: Godot --path . --rendering-method gl_compatibility --script res://game_factory/environment/ART-0003/v001/review.gd. تجميع GIF من لقطات Godot: python game_factory/environment/ART-0003/v001/finish_review.py. تعرض اللوحة الإطارات الطبيعية ومكبرة ومثبتة إلى نفس الموضع؛ لا تدّعي مطابقة إيقاع البحر الفعلي أو جاهزية تكامل الخريطة.

## الملفات والبصمات

| الملف | SHA-256 |
| --- | --- |
| assets_hd/background/cliff_foam_loop/v001/hero_cliff_foam_01.png | 4c44b5b35087c10fe2b3ef75a0e18242b39e5306c4f3d74d97b0b2f8c6b0ffee |
| assets_hd/background/cliff_foam_loop/v001/hero_cliff_foam_02.png | 8095222701032f32a7e239b450fd1d2df6a714af02665e557f506c110ca1766f |
| assets_hd/background/cliff_foam_loop/v001/hero_cliff_foam_03.png | 7deaec5d213d88cedb904a9d9e8667a633a6e55fe7a0c4e7169a81f1cfdbb392 |
| assets_hd/background/cliff_foam_loop/v001/hero_cliff_foam_04.png | 32c11a3e11bc31908fb697fc1db609b992a5466f6339673999c2166d2ac2583c |

## الفحص الفعلي

Godot 4.7.2 / ANGLE NVIDIA RTX3070: اثنتا عشرة لقطة viewport لثلاث دورات، وGIF مجمع منها. فُحصت اللوحة الفعلية: أوضاع التقدم والتكسر والتراجع ظاهرة والموضع العام ثابت. فرق موضع القمة البيضاء بين الإطارات بكسل مصدر واحد = 0.054 بكسل عند 96×48. لا إثبات اندماج مع سطح الجرف أو إخفاء الرغوة خلف الصخور بعد؛ ذلك يحتاج معايرة داخل الغرفة. لا محاولات مرفوضة في هذه الجولة. تحذيرات مسار log/shader cache المحلي في sandbox لم تمنع الالتقاط.
