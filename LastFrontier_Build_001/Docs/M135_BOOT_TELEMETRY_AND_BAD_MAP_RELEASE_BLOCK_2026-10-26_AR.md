# M135 — إصلاح المراقبة المبكرة وبوابة منع إعادة استخدام خريطة Unreal الفاشلة

**التاريخ:** 26 أكتوبر 2026  
**الفرع:** `m135-boot-observability-gates`، مستقل عن main وM66 وM128 وM134.  
**حالة البناء:** لم يُنفذ Unreal Compile أو Cook أو Android Run أو Google Play Upload.

## ما تم تنفيذه مباشرة على GitHub

1. في `Source/LastFrontier/Private/World/LFWorldDirector.cpp` أُضيفت رسائل لتأكيد دخول `BeginPlay`، واكتشاف غياب المجسمات الأساسية للمحرك، وعد الأعداء المنشأين فعليًا والكشف عن فشل إنشاء بعضهم. حافظنا على تسلسل مراحل Android وأوامر الاستعداد القديمة. هذه **أدوات رصد في مصدر نسخة مستقبلية فقط**؛ لا تغير حزمة Google Play 218.
2. في `Source/LastFrontier/Private/Core/LFGameMode.cpp` أُضيف `CROWNFALL_BOOT_PLAYER_SPAWN_FAILED` إذا فشل `SpawnActor` لشخصية اللاعب، إلى جانب علامة النجاح الموجودة سابقًا.
3. أُضيف `Scripts/M135_KnownBadMap_ReleaseBlock_ReadOnly.py`: يكشف بالـGit blob SHA-1 الملف الذي أثبت تشغيل Unreal سابقًا فشل طبخه، ويُرجع `BLOCKED_HISTORIC_UE_COOK_FAILURE` مع exit 2. يتحقق أيضًا من magic header، ويرفض الملفات المفقودة والروابط الرمزية. **حتى عند نجاحه لا يدعي صلاحية خريطة أخرى** دون اختبار UE الحقيقي.
4. أُضيف `Scripts/test_M135_known_bad_map_gate.py` (6 اختبارات اصطناعية) و`Scripts/test_M135_boot_observability.py` (اختباران لمواضع أدوات الرصد). لا تتطلب Unreal Engine أو أي ملف خاص.
5. أُضيف Workflow `.github/workflows/m135-knownbad-map-gate-and-observability.yml` يبدأ تلقائيًا عند Push على الفرع M135 بصلاحية `contents: read` ومن دون تشغيل Unreal/VM/Gradle أو استعمال مفاتيح التوقيع.

## النتيجة المؤكدة

- التشغيل الأول: `40276875319` فشل في حالة اختبار واحدة، بسبب تصنيف الملف المفقود خطأ كـ`READ_FAILED` بدل `MISSING_OR_UNSAFE`.
- صُحح الخلل باحتفاظ `FileNotFoundError` بحالة `BLOCKED_MISSING_OR_UNSAFE_MAP`.
- **التشغيل التالي `40276954047`: SUCCESS، 29/29 اختبارًا ناجحًا** (21 اختبار M131/M133، و8 اختبارات M135)، بالإضافة إلى نجاح 7 سكربتات اصطناعية تاريخية M121–M127، وصياغة Bash، وفحص الملفات.
- أثبت سجل CI الجديد صراحة:
  `M135_MAP_STATUS=BLOCKED_HISTORIC_UE_COOK_FAILURE`
  `M135_RELEASE_MAP_BLOCKER=WORKING_AS_DESIGNED`
  `M131_STRUCTURAL_ERRORS=0`
  `M131_REVIEW_ONLY=5`
- رابط السجل الموثق: https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/40276954047
- تقرير/سجل Unreal الأصلي لخريطة M60 بتاريخ 7 أكتوبر: https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/37645589203 — `LogLinker Serialization error FName index 64 outside [0, 44)`، `Cook ExitCode 25`.
- الملف GitHub الحالي له Git blob OID `965b78fc071c21412f966b70712eb30724799c20` المطابق لملف M60 القديم. **لا نفترض أنه خريطة M84/M106 الأصلية**، إذ توثق السجلات اللاحقة نجاح M85 map load وM86 Cook في VM منفصلة.

## ماذا يثبت نجاح الاختبارات؟

فحصنا منطق أداة منع خريطة معطوبة، وأن رسائل تشخيص C++ موجودة، وانعدام أخطاء بنيوية مطلقة وفق قواعد M131، وصلاحية Python/Bash، ونجاح اختبارات صناعية. **لا يثبت هذا أن C++ يُجمَّع بUnreal 5.8 أو أن التطبيق يبدأ على Android.**

## الباقي لإصلاح إغلاق 218

- الخادم الأصلي `crownfall-m62-build` وخرائط `M84_EDITOR_SANDBOX_v218`/`M106_RELEASE_SANDBOX_v218` وحزمة AAB الأصلية: **لم يتم الوصول إليها** بالموصل الحالي.
- تقرير Android stack trace الأول أو logcat/Android vitals الخاص بالإصدار الذي شُغّل فعلاً: **غير متاح**.
- يجب اختبار أن خريطة VM الأصلية مختلفة عن GitHub الفاشلة عبر فحص البصمات من M133، ثم إذا لزم إعداد مصدر نظيف مع Full Unreal Build/Cook/Package واختبار جهاز مستقل. **لا تنسخ خريطة GitHub الفاشلة إلى M84/M106.**
- تحديد خطأ GooglePAD/JNI مقابل OBB/Pak مقابل Vulkan/RHI مقابل الخطأ الأصلي لا يزال **غير مثبت**.
- يمنع الدمج أو النشر اعتمادًا على نجاح فحص المصدر وحده؛ عند إعداد نسخة لاحقة تحتاج versionCode جديدًا غير مستخدم وأعلى من 218 بعد التحقق من Play.

## حدود الأمان
لا تعديل لـ`main` أو `m66` أو `m128` أو `m134`، ولا تغييرات على Google Play، ولا أي وصول إلى JKS. جميع تعديلات M135 موثقة على الفرع المعزول فقط. فحص الخريطة **يقرأ** البيانات ولا يغيرها.

## المراجع الرسمية
- Epic Unreal 5.8 logging: https://dev.epicgames.com/documentation/unreal-engine/logging-in-unreal-engine
- Epic SpawnActor: https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UWorld/SpawnActor
- Epic SetTimerForNextTick: https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/FTimerManager/SetTimerForNextTick
