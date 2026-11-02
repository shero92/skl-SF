---
id: TASK-0073
status: blocked
owner: aider
agent: aider
priority: high
branch: codex/aider-hero-attack-runtime
depends_on: none
issue: none
art_request: ART-0026
touches: scenes/hero_attack_preview.gd,scenes/hero_attack_preview.tscn,scenes/hero_attack_timeline.gd,tools/hero_attack_assets.py,tools/tests/test_hero_attack_assets.py,tools/verify_hero_attack.gd,docs/HERO_ATTACK_RUNTIME.md,.agents/tasks/TASK-0073_hero_attack_runtime.md
test: python tools/run_tests.py --changed
done_when: مشغّل معاينة مستقل واختبارات زمن وأداة استخراج وفحص sheet؛ الأصول الناقصة تمنع الادعاء بجاهزية الحركة النهائية.
---
# تكامل معاينة هجوم Hero — تنفيذ Aider فقط

## التفويض

طلب المالك تنفيذ خطة Hero في هذه المحادثة يسمح بهذا النطاق داخل مشهد مستقل، ويستثنيه من قيد environment-only القديم في AGENTS.md عند commit الأساس. القرار الأحدث يمنع Codex من كتابة الكود ويسند هذه المهمة إلى Aider. لا تعديل AGENTS.md ولا إعدادات الأتمتة ولا الصور الحالية. لا Claude ولا تغيير النموذج: openai/gpt-4o وgpt-4o-mini.

## المطلوب الآن

1. اقرأ وثيقة docs/HERO_ATTACK_STYLE.md المقدمة كمرجع قراءة من worktree TASK-0072، والمكونات scenes/game_factory_demo.gd وscenes/modular_battle_character.gd وscenes/game_factory_actor.gd.
2. أنشئ مشهد معاينة مستقل وtimeline قابلة للاختبار. استخدم ModularBattleCharacter الحالي، ولا تعدله. واجهة play_attack(attack_id, attacker, defender). اعرض phantom_dash فقط عند وجود أصول rear ملائمة وبيانات موثقة؛ خلاف ذلك اعرض تحذير MISSING_REAR_ART دون ادعاء حركة مكتملة. يمكن وضع diagnostic واضح للأصول القديمة، بلا تسميته الحركة النهائية.
3. timeline: 1050 ms تشمل hold 430–480، حدث واحد عند 430. دعم pause/restart/cancel/seek وسرعة بطيئة. seek لا يطلق أحداثًا. restart يبدأ دورة جديدة. استعادة الحالة. الخاصة تبقى unavailable حتى اعتماد العادية.
4. واجهة المعاينة: تشغيل/إيقاف/إعادة/تقدم وتراجع إطار/سرعة .25x/تبديل السيفين/الكاميرا/VFX. nearest وتصحيح pixel snapping للعرض؛ لا renderer blur. حركة ظلال منفصلة. لا تغيير نظام الضرر أو main.
5. أداة Python CLI لا تولد رسومات: inspect-gif للمراجع (metadata/contact sheets)، inspect-sheet لفحص 4×4 وحدود alpha/duplicate hashes، extract-sheet لاستخراج 16 خلية كما هي دون إعادة رسم أو per-frame auto scaling، تجميع Godot captures إلى GIF مع durational rounding مقاس. أعط مسارات input/output صريحة؛ لا تلمس الأصول المعتمدة. ترفض extraction عند dimensions غير قابلة للقسمة على grid أو clipping أو محتوى يعبر الخلايا. بيانات pivots يجب أن تأتي من annotations، لا اختلاقها. يمكن إنتاج تقرير فحص حتى عند رفض extraction.
6. اختبارات meaningful لـtimeline باستخدام SceneTree headless، واختبارات Python للاستخراج ورفض العيوب وتوقيت GIF. أدوات export تكتب المخرجات فقط إلى staging الجديد المطلوب عند تشغيلها؛ لا تعدل PNGs بنفسك ولا تولد صورًا. الاختبارات بfixtures صناعية مؤقتة مسموحة.
7. وثّق commands والحدود والملفات المفقودة. لا claims لاعتماد/نجاح دون تشغيل.

## القيود والأدلة

- implement فقط touches أعلاه. يمكن قراءة metadata من game_factory وweapon catalog؛ لا صور في سياق Aider.
- لا تعديل tools/test_map.json لأنه يتداخل مع TASK-0071؛ شغل اختبارات المهمة صراحة وسجّل الحاجة لتسجيلها لاحقًا.
- لا auto commits أو dirty commits، ولا push أو merge. المشرف يراجع diff والاختبارات ويحفظ provenance الصادق.
- أصول جديدة قيد الإنتاج في TASK-0072، ليست dependency لهذا المشغّل المستقل، لكنها شرط عرض نهائي. لا تزور rear view باستخدام side frame مقلوب.
- changed-test route ثم اختبارات المهمة وGodot import/headless. سجّل أوامر فعلية ونتائجها في docs/HERO_ATTACK_RUNTIME.md.
- provenance للكود Aider/openai/gpt-4o، وللصور Codex/image_gen. لا تنسب الكود إلى Codex.

## نتيجة محاولة التشغيل — 2026-10-31

شُغّل Aider 0.86.2 فعليًا من .venv/Scripts/aider.exe في هذا worktree، بالنموذجين المحددين، باستخدام message-file ومنع auto/dirty commits. لم ينتج أي كود أو اختبار.

العائق المثبت: OPENAI_API_KEY: Not set ثم litellm.AuthenticationError: AuthenticationError: OpenAIException - The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable.

فُحص وجود الاعتماد فقط في بيئة العملية وبيئة مستخدم Windows دون طباعة أي قيمة؛ غير متاح. اختار المالك «أكمل الرسوم والتسليم الآن»، لذا لا يعاد التشغيل ولا يطلب المفتاح في المحادثة.

التكلفة/الاستهلاك: unknown؛ فشل المصادقة ليس دليل استهلاك صفري مقاس. لا commit للكود ولا اختبارات runtime أو captures جديدة.

التالي: بعد تهيئة مصادقة Aider محليًا، استئناف هذه المهمة نفسها دون إنشاء نسخة مكررة؛ ثم اختبارها مع أصول TASK-0072 الصالحة.
