# M136 — استعادة خريطة Unreal الأصلية المعطوبة في نسخة مستقلة، دون تكلفة بناء

**التاريخ:** 26 أكتوبر 2026.  
**الفرع:** `m136-isolated-unreal-map-recovery` مشتق من `m135-boot-observability-gates`.

## سبب هذه المرحلة

- مراجعة كاملة لملف M65 المحفوظ في Library باسم `CROWNFALL_M65_UNREAL_SOURCE_RELEASE_CANDIDATE.zip` أكدت وجود `Scripts/create_testmap_in_unreal.py` و`prepare_testmap_ue58.sh`. الوثائق القديمة M64/M65 توضح صراحة أن خريطة M60 لم تكن ضمن الحزمة، وأن إنشاء بديل بواسطة Unreal Editor ممكن — لا بمجرد Python نظام التشغيل.
- GitHub يحتوي `LastFrontier_Build_001/Content/Maps/TestMap.umap` Git blob `965b78fc071c21412f966b70712eb30724799c20`. هذا هو **نفس الملف** الذي فشل أثناء Cook واقعي لتشغيل `37645589203` بتاريخ 7 أكتوبر برسالة `FName index 64 outside [0,44)`.
- خلال تشغيل GitHub Actions M60 التاريخي `37645589203` اكتمل تنزيل UE5.8 وتجميع `LastFrontierEditor` بنجاح، لكن **Cook فشل** بسبب الخريطة. أي أن مشكلة M60 التاريخية ليست مجرد غياب كود لعبة؛ وإنشاء خريطة جديدة يمكن أن يزيل ذلك العائق التاريخي.
- سجلات M85/M86 تصف نجاح خريطة أخرى على M84/VM، لكن لا يوجد وصول للمحرك أو للخريطة الأصلية أو AAB 218 من الاتصال الحالي. ممنوع تغيير خريطة M84/M106 أو افتراض أنها مطابقة لمستودع GitHub.

## التنفيذ الجديد

1. `Scripts/M136_Isolated_Map_Sandbox.py`: يقرأ نسخة M60 الفاشلة المعروفة بالبصمة، وينسخ المشروع إلى **مجلد مؤقت جديد خارج المستودع**، ثم يعزل الخريطة في `M136_Quarantine` داخل النسخة المؤقتة. يرفض أي خريطة أخرى أو مجلد غير مستقل. لا يلمس الملف الأصلي.
2. في النسخة المؤقتة **فقط**، يفعّل `PythonScriptPlugin` و`EditorScriptingUtilities`، ويوجه `GameDefaultMap` و`EditorStartupMap` مؤقتًا إلى `/Engine/Maps/Entry` حتى لا يحاول Editor فتح خريطة GitHub المعطوبة.
3. `Scripts/M136_Create_TestMap_In_Unreal.py`: برنامج مخصص **لـPython المدمج داخل Unreal Editor 5.8**، يستدعي `LevelEditorSubsystem.new_level('/Game/Maps/TestMap', False)` وينشئ `PlayerStart` واحدًا ويحفظ المستوى، بينما يترك إضاءة ومجسمات اللعبة لآلية `ALFWorldDirector` الموجودة مسبقًا. لا يولد ملف `.umap` مزيفًا.
4. أمر `finalize` في برنامج Sandbox يتحقق من وجود ملف UE map جديد ذي رأس صالح **ومختلف عن الملف الفاشل** وسجل Editor يحتوي علامة الإنشاء، ثم يعيد إعدادات `.uproject` و`DefaultEngine.ini` الأصلية داخل النسخة المؤقتة بحروفها نفسها. حتى هذا **لا يثبت نجاح Cook/Android Runtime**.
5. `Scripts/test_M136_isolated_unreal_map.py`: **10 اختبارات اصطناعية** لحماية الملف الأصلي، العزل، إعدادات الـEditor، غياب ملفات JKS/AAB، ورفض الاستبدال أو المخاطر والتراجع عن الإعدادات.
6. `.github/workflows/m136-isolated-map-recovery-preflight.yml`: GitHub Actions على الفرع المعزول، **مهلة قصوى 6 دقائق**، دون Unreal/Gradle/SDK أو أسرار، ويفحص Sandbox فعليًا ويرفض إعادة استخدام الخريطة الفاشلة.

## نتيجة موثقة

- تشغيل GitHub Actions: **40278478695 — SUCCESS**، بعد مراجعة جميع خطوات الـJob وتفاصيل سجل التنفيذ.
- **39/39 اختبارات Python اصطناعية ناجحة** (29 قديمة من M131/M133/M135 + 10 اختبارات M136 الجديدة).
- `M136_PYTHON_SYNTAX=PASS`.
- `M136_BROKEN_MAP_QUARANTINED_IN_EPHEMERAL_SANDBOX=PASS`.
- `M136_SOURCE_MAP_UNCHANGED=PASS`.
- `M136_HISTORICAL_CORRUPT_MAP_RELEASE_BLOCKED=PASS`.
- `M136_NEW_MAP_GENERATED_BY_UNREAL=NOT_RUN` — هذه العبارة مهمة لتجنب وصف تهيئة Sandbox بأنها معالجة نهائية.
- الرابط: https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/40278478695

## المتطلبات المتبقية لإنتاج اختبار Android فعلي

- بيئة مزوّدة بـ **Unreal Engine 5.8 Editor وBuild.sh وRunUAT.sh** وAndroid SDK/NDK/JDK؛ محرك Unreal غير موجود داخل حزمة M65 أو GitHub أو بيئة العمل المحلية الحالية.
- تشغيل أمر Editor `-ExecutePythonScript=...` على النسخة المعزولة لإنتاج TestMap ثنائية حقيقية. **لم يتم تشغيله بعد**.
- بعد استعادة إعدادات المشروع، إجراء UE Editor load ثم Build/Cook/Package مناسب؛ ممنوع استخدام خريطة GitHub الفاشلة وممنوع نقل التغييرات قسرًا إلى M84/M106.
- اختبار Android حقيقي على جهاز مستقل أو بيئة اختبار سحابية تثبّت APK/AAB وفواصل asset-pack المناسبة؛ مقارنة `obbassets` و JNI وربط stack trace للفشل إن وقع.
- استخدام versionCode لم يُستعمل سابقًا أعلى من 218 إن تقرر إرسال نسخة اختبار جديدة، بعد مراجعة Play Console؛ لا تُستخدم مفاتيح JKS إلا في بيئة توقيع مصرح بها.

## لماذا لم أبدأ بناءً ثقيلًا الآن؟

التشغيل الأصلي M60 استغرق من 15:38 حتى 16:47 UTC تقريبًا قبل أن يفشل Cook. GitHub Actions في المستودعات الخاصة لديها رصيد دقائق مجاني **محدود** وقد تُفرض رسوم بعد نفاده، ولا يتيح الموصل الحالي قراءة رصيد مستخدم GitHub أو الوصول إلى خادم Google Cloud الذي يحمل المحرك والخريطة M84/M106. التزام المستخدم بالمسار المجاني يمنع بدء تشغيل ضخم مجهول التكلفة.

## الحالة الأمنية

- التعديلات الوحيدة في فرع M136: أدوات Python وWorkflow وتقرير توثيقي.
- لم يُلمس `main`, `m66`, `m128`, `m135`, بيئات M84/M106، توقيع JKS أو Google Play.
- **ما أُنجز:** إصلاح خطة استعادة الخريطة وجاهزية Sandbox واختبارات فعلية للإجراءات الوقائية.
- **ما لم ينجز:** تشغيل محرر Unreal نفسه أو توليد خريطة ثنائية صالحة أو Build/Cook أو اختبار هاتف/Android 218. لا دليل على حل الإغلاق بعد الشعار.

## مصادر فنية رسمية
- Epic UE5.8 Python Editor scripting: https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python
- Unreal Engine 5.8 `ULevelEditorSubsystem::NewLevel`: https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Editor/LevelEditor/ULevelEditorSubsystem/NewLevel
- GitHub Actions minutes and billing: https://docs.github.com/en/billing/concepts/product-billing/github-actions
