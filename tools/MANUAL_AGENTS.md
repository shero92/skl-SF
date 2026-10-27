# التشغيل اليدوي للوكلاء

من المستودع:

```powershell
.\tools\run_agents_manual.ps1 -DryRun
.\tools\run_agents_manual.ps1 -Agents codex,claude -MaxTasks 10 -MaxMinutes 150 -IncludeArt
.\tools\run_agents_manual.ps1 -Agents codex -MaxTasks 3
```

الحدان مشتركان للجلسة كلها. لا يستدعي DryRun النماذج ولا يكتب سجلات. التشغيل الفعلي يستخدم نسخة تنسيق نظيفة تحت `%LOCALAPPDATA%/rtk/skl-SF/manual/`، ويحافظ على تغييرات نسختك الأصلية. السجلات والملخصات في `.agents/monitoring/.local/` داخل نسخة التنسيق. المشغّل المجدول واليدوي يستخدمان قفل المستودع نفسه؛ تشغيل آخر مشغول يخرج دون تكرار التنفيذ.

تُنفَّذ المهام البرمجية عبر `agent_runner.py` في worktrees مستقلة وخالية من الصور أثناء جلسة النموذج. ملفات البنية التحتية تذهب إلى PR للمراجعة. لا تتحول `review` إلى `done` تلقائيًا. عند فشل اختبار عادي توجد محاولة إصلاح واحدة ضمن touches نفسها. أخطاء السلامة توقف الجلسة وتحفظ الأدلة؛ المهمة المحجوبة أو حد استخدام وكيل لا يوقفان مهام الوكيل الآخر المستقلة.

## أدلة المتطلبات

يمكن أن يحتوي frontmatter للمهمة على `evidence_manifest` يشير إلى JSON داخل المستودع. يحتوي الملف مصفوفة `requirements` غير فارغة. كل متطلب يحدد `kind` و`status=approved` و`approved_at` و`approved_by` أو `reviewer` و`provenance={source,kind}`.

- `reference`: مسار مرجع PNG، `sha256` و`pixel_size`. تُفحص الموافقة قبل قراءة بايتات المرجع؛ ثم البصمة وترويسة PNG دون فك الصورة.
- `measurement`: قياسات معتمدة ذات `scope` و`target`.
- `visual_approval`: اعتماد مالك صريح، منتج ومراجع وجلسات مستقلة، وربط ببصمة الهدف أو commit.

غياب الأدلة أو اختلاف البصمة يحجب المهمة المعنية فقط. توقّف المهلة يسجل الحالة الفعلية ولا يخترع اكتمالًا أو حجبًا لم يُحفظ في سجل المهمة.

## مسار الرسم الاختياري

`-IncludeArt` لا يفترض أن تسجيل الدخول يوفّر أداة صور. لا يوجد adapter مُفعّل افتراضيًا. إذا لم توجد أداة معتمدة تُحجب مهمة الرسم ويستمر العمل المستقل.

عند توفر adapter حقيقي ومراجع، يضيف المالك أو PR معتمد `.agents/planner/manual_art_adapters.json`، بقسم `agents` لكل من `codex` و`claude` حسب الحاجة. يحتوي إعداد adapter على `status=approved` و`approved_by` و`approved_at` و`image_tool_verified=true` و`path` لملف Python داخل `tools/` و`sha256` المطابق له. لا يغيّر المشغّل الصلاحيات ولا يصنع هذا الاعتماد.

واجهة adapter:

```text
python tools/<approved_adapter>.py --task TASK-#### --art-request ART-#### --review-only --deadline <absolute_monotonic_deadline>
```

يعمل داخل worktree مخصص لطلب ART، ولا ينشئ commits أو يغيّر ملفات خارج delivery. يجب أن يستخدم أداة الصور المعتمدة فعلًا؛ لا بديل إجرائي منخفض الجودة. يجب أن يطابق manifest كل `output_paths` بالضبط، ويحدد `request_id`, `producer`, `tool`, `model`, `reference_sha256`، ولكل ملف `path`, `sha256`, `pixel_size`, `origin`, `footprint`, `collision`, `shadow`. يمنع تكرار المسارات أو الكتابة فوق تسليمات موجودة أو أي اعتماد بصري ذاتي، حتى داخل بيانات فرعية. المشغّل يفحص البنية والبايتات، ثم يرفع PR بحالة delivered للمراجعة؛ لا يدمج الرسم أو يعدّل production assets.

لا تُثبَّت Scheduled Tasks ولا تُغيَّر إعدادات الأمان. يلزم تسجيل دخول GitHub وCLIs وتفعيل execution موثّق وفق سياسة المستودع. إن بقيت نسخة التنسيق متسخة أو مهمة منقطعة، احفظها للمراجعة؛ لا تحذفها لاستئناف التشغيل.
