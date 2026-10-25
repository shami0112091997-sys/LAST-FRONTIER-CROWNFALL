# CROWNFALL Stronghold — M131: تطبيق تصحيحات المصدر والتدقيق النهائي

**التاريخ:** 25 أكتوبر 2026  
**الفرع المعزول:** `m131-isolated-source-repairs-20261025` (من M130 ← M129 ← M128)  
**نوع العمل:** إصلاح كود مصدر وتطوير فحوص قراءة فقط. **لا Compile / Cook / Package / Android run / VM / Play upload / GitHub Actions**.

## الحالة قبل التصحيح

- المشاهدة العملية الوحيدة: لعبة مع شاشة Unreal تُغلق بعد الشعار خلال نحو ثانية على هاتف المختبر. تحديد رقم الإصدار المثبت على الهاتف نفسه لم يُتحقق منه مباشرة. رقم حزمة AAB المفحوصة في Play Console هو **218**.
- صفحة حزمة 218 في Google Play تؤكد أن `obbassets` تستخدم **Install-time**. هذا **لا** يثبت أن Unreal فتح أو ركب المحتوى عند الإقلاع؛ وهو يجعل تأخر تنزيل `fast-follow` غير ملائم لتفسير العطل.
- صفحة Android vitals بفلاترها السابقة لم تعرض تقارير، ولم يتوفر تقرير ما قبل الإطلاق. غياب التقارير ليس دليلاً على عدم حدوث crash.
- حزمة AAB الأصلية وStack Trace وlogcat وVM ومحتويات Java/Native الناتجة ليست متاحة في هذه الجلسة.
- M128 أضاف `GooglePAD` و`bPackageDataInsideApk=False` و`bEnablePlugin=True` **في المصدر فقط**؛ لم يُبن المرشح أو يُختبر.
- مصدر GitHub يحمل `StoreVersion=215` بينما إصدار Play محل التحقيق `218`؛ لذلك لا يجوز افتراض تطابق الإعدادات التنفيذية.

## تصحيحات M131 المنفذة فعليًا (على هذا الفرع فقط)

| رقم | الملف | السبب والإجراء | مستوى الإثبات |
|---|---|---|---|
| 1 | `Source/LastFrontier/Private/Enemy/LFEnemy.cpp` و`LastFrontier.Build.cs` | عرّف `AAIController` و`AutoPossessAI=PlacedInWorldOrSpawned` وأضف `AIModule`؛ لضمان امتلاك الأعداء المولدين Controller. | إصلاح مصدر؛ ينتظر تجربة AI/Compile |
| 2 | `Private/UI/LFHUD.cpp` و`Public/UI/LFHUD.h` | حدّث عدّ الأعداء كل 0.25 ثانية بدل بحث `GetAllActorsOfClass` لكل DrawHUD. | تحسين كلفة حسابية مؤكد نصيًا؛ أثر FPS غير مقاس |
| 3 | ملفات HUD نفسها | أضف `bHasSeenEnemies` فلا تظهر رسالة الفوز قبل إنشاء الأعداء بعد تأجيل تحميل العالم. | حماية من خطأ منطق ناشئ عن التعديل |
| 4 | `Private/World/LFWorldDirector.cpp` و`Public/World/LFWorldDirector.h` | إنشاء الأرض مباشرة، وتوزيع أربع مراحل أخرى على استدعاءات `SetTimerForNextTick` عند Android، مع إبقاء المسار التقليدي خارج Android وحفظ `CROWNFALL_M60_WORLD=READY`. | تحسين محتمل لذروة الإقلاع؛ لم يُختبر على الهاتف |
| 5 | `LFWorldDirector.cpp` | تباعد المصابيح النقطية على Android من 750 إلى 1500 (10 بدل 18) دون تغيير توزيع PC. | تقليل عدد الأضواء ديناميكية الإنشاء؛ أثر GPU غير مقاس |
| 6 | `Private/Core/LFGameInstance.cpp` و`Public/Core/LFGameInstance.h`, `Private/Core/LFGameMode.cpp` | نقاط تتبع `CROWNFALL_BOOT_GAMEINSTANCE_INIT` و`CROWNFALL_BOOT_GAMEMODE_BEGINPLAY` وتسجيل فشل إنشاء WorldDirector. | تشخيص لنسخة اختبار مستقبلية؛ لا يفحص AAB 218 القديمة |
| 7 | `Scripts/M68_Staged_Android_Build.sh` | منع `NEXT <= 218` حتى مع إدخال قيمة خاطئة لآخر إصدار Play. | سد ثغرة منطقية في بوابة اختيار الرقم |
| 8 | `.github/workflows/crownfall-android-build.yml` و`crownfall-production-qa.yml` | تمييز مسار **WebView 214** بالاسم؛ حصر كلمات مرور توقيع WebView في خطوة البناء وإزالة التصدير إلى `GITHUB_ENV` لكل خطوات الوظيفة. | مراجعة أمنية ومصدرية؛ لم يُشغّل Workflow |
| 9 | `Scripts/M131_Unreal_Repo_Integrity_ReadOnly.py` | إضافة فاحص مصدر فقط: uproject، GooglePAD، AAB flags، بنية map header، AI/HUD/staging، رقم إصدار GitHub، وازدواج هوية WebView. يطبع حالات ثابتة فقط ولا يقرأ JKS. | برنامج موجود؛ ليس أداة إثبات crash |
| 10 | `Scripts/test_M131_source_integrity.py` | **6 اختبارات انحدار اصطناعية** تغطي بنية المصدر، مطابقة/اختلاف رقم الإصدار، خريطة تالفة، غياب AI Controller، إعدادًا مكررًا، ورسالة فوز قبل الأعداء. | نُفذت نسخة مطابقة من منطق الاختبارات محليًا، 6/6 PASS دون Unreal |

## مراجعة تشغيل الأدوات

- Source scan مباشر عبر GitHub: **11/11** تأكيدًا أوليًا لاتساق التعديلات في ملفات المصدر، ثم مراجعة نقاط بدء الإقلاع وشرط منع الفوز المبكر بعد إضافتها.
- `python3 -m py_compile` لأداة ومجموعة اختبارات M131 (نسخة محلية مطابقة): **نجح**.
- `python3 -m unittest discover ... -p 'test_M131_*.py' -v` في بيئة Python محلية باستخدام ملفات مؤقتة مصطنعة: **6/6 PASS**.
- لم يتم تشغيل أدوات M131 على VM الحقيقية أو الحزمة 218 أو تثبيت APK.
- لا تعني نجاحات فحوص المصدر نجاح بناء Unreal أو تشغيل اللعبة.

## الأخطاء والمخاطر التي **لم تثبت معالجتها** بعد

1. **سبب انهيار 218 غير معروف**: مطلوب أول دليل Java/JNI/Native/RHI/AssetMount من مصدر مستقل موثوق.
2. **GooglePAD/OBB**: Play يبين `Install-time`. وفقا لوثائق Android، install-time pack قد تكون ملفاتها داخل split APK ويجب الوصول إليها بواسطة `AAssetManager` أو الآلية الصحيحة التي يتبعها المحرك. لا تفترض وجود مجلد مفكوك، ولا تفترض فشل PAD دون فحص طريقة التخزين وتكامل UE الحقيقي.
3. **اختلاف مصدر GitHub عن M106**: إعداد GitHub `StoreVersion=215`؛ لا تعوض ملف إعدادات M106 الخاص من GitHub، لأنه قد يضم إعدادات التوقيع وسياق مختلفًا.
4. **الشحن باستخدام Cook/Build قديمين**: M119 أعاد استخدام مخرجات سابقة. مرشح M128/M131 يغيّر الإضافات والسلوك، وبالتالي يجب Build/Cook/Stage/Package كامل في بيئة جديدة عند إذن مرحلة الاختبار؛ لا `skipbuild/skipcook` عشوائيًا.
5. **SDK/RHI**: UE5.8 توصي SDK35 وNDK r27c وJDK21.0.3؛ مصدر GitHub يستهدف SDK36. هذا يستدعي اختبار توافق محدد فقط، لا خفض Target SDK عشوائيًا في مخالفة سياسة Play.
6. **مسارا Android بنفس الهوية**: ما زال مشروع WebView التاريخي يحمل `com.crownfall.stronghold`؛ أعيدت تسمية workflows للتمييز لكن لم يُغيّر معرف الحزمة أو يُحذف المشروع القديم.
7. **الميزات المرئية**: 10 مصابيح على Android ومرحلة world deferral تحتاج فحص جودة وأداء مستقل؛ لا تعتبرها تحسينات مثبتة حتى القياس.
8. **الأصول والخرائط**: الملف `TestMap.umap` في GitHub رأس Unreal صالح ظاهريًا، وليس اختبار فتح/طبخ. محتوى البناء الكامل قد يكون على VM وغير موجود في GitHub.

## ترتيب الخطوات التالية المأذونة فقط بعد تحقق بيئة الاختبار

1. على Play Console فقط: تأكد من رقم الإصدار النشط لمسار **Internal Testing** الذي وصل إلى المختبر وقت الفشل (صفحة AAB قد تكون Draft).
2. إن توفرت AAB 218 الأصلية بصورة موثوقة: قارن SHA-256، افحص split/asset-pack Manifest و`GameActivity`/DEX/JNI ومحتويات OBB بطريقة قراءة فقط؛ لا ترفع JKS.
3. عند موافقة المالك على اختبار مستقل: استنساخ M106 في مساحة VM **معزولة** مع نسخ محمية، وتطبيق التغييرات الصغيرة بعد المراجعة، ثم Full Unreal Build/Cook/Stage/Package. **لا تستخدم 218 ولا تفترض أن 219 متاح**؛ تحقق من أعلى رقم Play الفعلي ثم اختر أعلى منه.
4. اختبر النسخة على جهاز اختبار مستقل (محلي أو مختبر سحابي بإذن وتكلفة متفق عليها)، واحتفظ بنتيجة فتح `TestMap` وثبات الحركة والقتال والإضاءة وتوقيت بدء العالم وStack Trace إن وقع crash.
5. لا تطبق أي Merge إلى `main` أو `m66` ولا تنشر تحديثًا قبل نجاح اختبار Unreal الفعلي ثم اختبار Internal Testing.
6. في حال ظهور `NoSuchMethodError` افحص JNI؛ `PakFile/OBB` افحص asset mount؛ `VK_ERROR` افحص الرسومات؛ `SIGSEGV` اربط الرموز المطابقة؛ لا تغيّر هذه الأسباب جميعًا مرة واحدة.

## الحالة

**تغييرات المصدر منفذة ومحفوظة في M131 فقط.**  
**حالة 218 في Google Play: لم تتغير.**  
**المفتاح JKS وكلمات المرور: لم تُقرأ أو تُنقل أو تُعرض.**  
**`main`, `m66-smart-recovery`, `m128-googlepad-delivery-candidate-only`: دون كتابة.**  
**Root cause وBuild/Android runtime: UNKNOWN/NOT RUN.**

## المصادر الرسمية

- Epic Unreal Engine 5.8 Android requirements: https://dev.epicgames.com/documentation/unreal-engine/android-development-requirements-for-unreal-engine
- Epic GooglePAD: https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine
- Epic AutoPossessAI: https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/EAutoPossessAI
- Epic FTimerManager::SetTimerForNextTick: https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/FTimerManager/SetTimerForNextTick
- Epic mobile lighting: https://dev.epicgames.com/documentation/unreal-engine/performance-guidelines-for-mobile-devices-in-unreal-engine
- Android PAD install-time native: https://developer.android.com/guide/playcore/asset-delivery/integrate-native
- Google Play vitals: https://support.google.com/googleplay/android-developer/answer/9859174
