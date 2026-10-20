# CROWNFALL M128 — إعداد تصحيح GooglePAD التجريبي (غير مثبت على الهاتف)

**الحالة:** تعديل مصدر مرشح في فرع مستقل، بتاريخ 21 أكتوبر 2026. **ليس إصلاحًا مثبتًا ولا حزمة مبنية أو إصدارًا منشورًا**.

## السبب الذي دفع لهذا التعديل
- نتيجة اختبار الهاتف للإصدار 218: Play install ناجح؛ تظهر شاشة شعار Unreal ثم يعود النظام إلى الشاشة السابقة خلال أقل من ثانية.
- ملف المشروع المرجعي في GitHub يحتوي على `"DisableEnginePluginsByDefault": true` دون GooglePAD صريح، بينما تنص وثائق Epic على أن GooglePAD مفعلة افتراضيًا في المشاريع المعتادة. تعطيل الإضافات الافتراضية يحتاج مراجعة التفعيل الفعلي، ولا يثبت وحده أن تكامل Java مفقود.
- ملف Android المرجعي يحتوي `bPackageDataInsideApk=True`. وثائق Epic لتسليم `main.obb` كتجميعة **install-time** تنص على تعطيل `Package Data inside APK`؛ وقد شوهدت `obbassets/assets/main.obb.png` في الحزمة 218.
- **ليس لدينا** من الهاتف `logcat` أو `Android vitals stack trace`، ولم نفحص محتوى حزمة 218 الفعلي هنا. هذه قرائن اختبار فقط، ولا يجوز الجزم بأنها سبب الانهيار.

## التعديل المعزول المنفذ في هذا الفرع
- `LastFrontier_Build_001/LastFrontier.uproject`: أضفنا فقط `"Plugins": [{"Name": "GooglePAD", "Enabled": true}]`، وأبقينا `DisableEnginePluginsByDefault=true` وكافة وحدات المشروع.
- `LastFrontier_Build_001/Config/DefaultEngine.ini`: استبدلنا فقط `bPackageDataInsideApk=True` بـ`False`، وأضفنا قسم `[/Script/GooglePADEditor.GooglePADRuntimeSettings]` يحوي `bEnablePlugin=True`.
- تركنا `GameDefaultMap=/Game/Maps/TestMap` و`Vulkan` و`MinSDKVersion` و`TargetSDKVersion` واسم الحزمة كما هي.
- فحص المقارنة الآلي بين هذا الفرع و`m127-jni-forensic-audit-fixes` أثبت أن ملفي الإعدادات لم تتغير فيهما قيم أخرى؛ **هذا ليس Compile/Cook/Run**.

## تحذير بالغ الأهمية
**لا تنسخ ملف `DefaultEngine.ini` من GitHub مباشرة إلى VM M106.**
نسخة GitHub المرجعية ما زالت تحتوي على `StoreVersion=215` ولا تضم بيانات توقيع M106 الخاصة؛ استبدالها سيضر إعدادات الإصدار. عند بدء الإصلاح يجب إعداد **Sandbox جديد** من مصدر موثوق يطابق أحدث مشروع، والتأكد من وجود النسخ الاحتياطية، ثم تطبيق **التعديلات الثلاثة فقط** بصورة جراحية داخلها، مع الاحتفاظ ببيانات توقيع JKS خارج المستودع. لا تُستخدم كلمة مرور JKS في سكربتات أو GitHub.

## بوابات قرار الإصدار التصحيحي
1. **أولاً: الدليل من الهاتف**: تقرير Google Play Console → Pre-launch report → Stability أو Android vitals → Crashes، أو `adb logcat` منتقى من جهاز موثوق. ميّز بين JNI وAssetPack وPakFile وVulkan وSIGSEGV/low-memory.
2. شغّل أدوات M122/M125/M126 المحسنة محليًا على **AAB الأصلية للإصدار 218** داخل VM، وراجع Manifest لوحدة `obbassets` وتعريفات دوال GooglePAD. فحص static لا يحل محل سجل الهاتف.
3. افحص إعدادات **M106 الحقيقية** وملف `GooglePAD.uplugin` وتكوين `UGooglePADRuntimeSettings` الفعّال قبل اعتماد المرشح؛ لا تفترض أن مرجع GitHub هو النسخة الحرفية المستخدمة للرفع.
4. إن أكدت الأدلة مشكلة GooglePAD/OBB، طبّق المرشح على نسخة منفصلة من العمل. نظرًا لتعديل حالة plugin والتغليف يجب عمل Build/Cook/Stage/Package صالحين وفحوص جديدة؛ **لا تعِد استخدام `-skipbuild -skipcook` بصورة عمياء**.
5. اختبر تشغيل Android على جهاز حقيقي وصولاً إلى TestMap والحركة قبل رفع أي تصحيح. استخدم `versionCode > 218` (مثل 219 فقط إن لم يُستخدم)، ومفتاح التوقيع الخاص المسجّل؛ **Internal Testing فقط**. أبقِ الإصدار 218 متاحًا كدليل للمقارنة وفق خطة الاختبار.
6. لو أظهر السجل `VK_ERROR` أو `dlopen failed` أو خطأ C++ غير مرتبط بالأصول، **لا تستخدم هذا المرشح كإصلاح افتراضي**.

## ما لم نفعله
- لا وصول إلى Cloud VM أو Play Console أو هاتف المستخدم في هذه الجلسة.
- لم نغيّر `main` أو `m66-smart-recovery`، ولم نشغل GitHub Actions أو Build/Cook/Stage أو نرفع AAB.
- لم ننسخ أو نكشف JKS أو كلمات المرور، ولم نغيّر النسخة المنشورة.

## مراجع موثوقة
- Epic Unreal 5.8 GooglePAD: https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine
- Epic GooglePAD configuration and `bEnablePlugin`: https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/GooglePADEditor/UGooglePADRuntimeSettings
- Epic UE plugins: https://dev.epicgames.com/documentation/en-us/unreal-engine/plugins-in-unreal-engine
- Android Google Play Asset Delivery: https://developer.android.com/guide/playcore/asset-delivery
- Android Logcat: https://developer.android.com/tools/logcat

**الخطوة التالية المعلقة:** فحص ملف AAB 218 الأصلي أو أول stack trace. لا يوجد حتى الآن دليل على أن هذا التصحيح يجعل اللعبة تعمل.
