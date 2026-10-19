# CROWNFALL — خطة تشخيص وتعافٍ من تعطل تشغيل الإصدار 218

**تاريخ المراجعة:** 19 أكتوبر 2026 | **المرحلة:** M121 | **الوضع:** تحقيق للقراءة فقط، دون إنشاء حزمة أو رفع إصدار جديد.

## 1. الحقائق المثبتة

- المشروع: `LAST FRONTIER: CROWNFALL / CROWNFALL: Stronghold`، اسم تطبيق Android `com.crownfall.stronghold`، Unreal Engine 5.8.3، نسخة Google Play الداخلية `versionCode=218` (`versionName=2.2.0`).
- بُنيت حزمة AAB موقعة عبر M119. ظهرت `M119_UAT_EXIT=0` و`M119_CONFIG_RESTORED=PASS` ومؤشرات `bundleRelease`، وتحقق M118 من شهادة الرفع و`bundletool validate` وManifest وSDK 36 وغياب Debug/TestOnly.
- اجتازت مكتبات ARM64 الأربع المعبأة فحص PT_LOAD 16KB، والحزمة نقلت مع تطابق SHA-256. **لا يعني هذا نجاح الإقلاع على جهاز فعلي.**
- Google Play أتاح التنزيل؛ ثُبت التطبيق على جهاز المستخدم، وبعد فتحه يظهر شعار Unreal على شاشة سوداء ثم يغلق خلال أقل من ثانية. **تشغيل الخريطة واللعب FAIL أو غير متحقق؛ سبب الإغلاق مجهول.**
- قبل أي إصلاح يجب جمع stack trace أو `logcat` للجهاز؛ لا تعديلات على `main` أو نسخ M63/M84 أو مفاتيح التوقيع، ولا إعادة استخدام versionCode 218 مع تحديث جديد.

## 2. أدلة ثابتة من الملفات العامة في GitHub

| الملاحظة | الملف/الشاهد | مستوى اليقين |
|---|---|---|
| وجود `DisableEnginePluginsByDefault: true` مع عدم وجود إدراج صريح لـ`GooglePAD` في descriptor المرجعي | `LastFrontier_Build_001/LastFrontier.uproject` على فرع m66 | ثابت في المرجع، لم يُتحقق بعد من M106 على VM |
| `bPackageDataInsideApk=True` و`bSupportsVulkan=True` و`GameDefaultMap=/Game/Maps/TestMap` | `LastFrontier_Build_001/Config/DefaultEngine.ini` بفرع m66 | ثابت في المرجع، قد تختلف نسخة M106 |
| محتوى `obbassets/assets/main.obb.png` داخل AAB، وهو حزمة أصول منفصلة | تقرير `bundletool` / M118 المصور | وجود الأصول ثابت؛ نجاح توفيرها أو تحميلها على الجهاز غير معلوم |
| ملفات `TestMap.umap` الأصلية والمطبوخة موجودة وبُنيت | M116 وM119 | وجودها ثابت، لكن تحميلها على Android غير مثبت |
| يوجد تطبيق آخر Android WebView في المستودع يستخدم اسم الحزمة نفسه | `CROWNFALL_Stronghold_Android/.../MainActivity.java` | ثابت؛ هذا مشروع/مسار بناء مختلف، ولا يجوز الخلط بينه وبين AAB Unreal 218 |

### فرضية ذات أولوية عالية للفحص: Google Play Asset Delivery

توثيق Epic يشير إلى أن GooglePAD تتطلب تفعيل التكامل، وأن تسليم OBB بشكل **install-time asset pack** يستلزم تعطيل **Package Data inside APK**. وجود `obbassets` مع `bPackageDataInsideApk=True` في مرجع المصدر و`DisableEnginePluginsByDefault=True` يستحق التحقيق، لكن **ليس إثباتًا** أن ملفات البناء الحقيقية لا تحتوي على الإضافة أو أن هذا سبب الانهيار. قد تختلف نسخة M106 عن المستودع أو تكون هناك إعدادات خاصة بالمحرك.

**التحقق الآمن:** افحص نسخة M106 الحالية من `.uproject` و`DefaultEngine.ini` وإضافات GooglePAD المفعلة، وتكوين وحدة `obbassets` داخل AAB. بعد ذلك افحص logcat بحثًا عن رسائل `AssetPack`, `GooglePAD`, `OBB`, `Failed to open descriptor file`, `PakFile`.

### فرضيات أخرى، لا تُنفذ إصلاحاتها دون دليل

1. **Vulkan/RHI أو مشغل الرسومات:** راجع أول فشل `Vulkan`, `VK_ERROR`, `RHI`, `EGL` في السجل؛ عند ثبوت ذلك فقط، جرّب إعداد عرض بديل في نسخة تجريبية جديدة.
2. **تحميل map/content/shader:** ابحث عن `TestMap`, `LogPakFile`, `Failed to load`, `ShaderCodeLibrary`, `Missing package` قبل تعديل Cook.
3. **Java/JNI/مكتبات ديناميكية:** افحص `AndroidRuntime FATAL EXCEPTION`, `UnsatisfiedLinkError`, `dlopen failed`, `SIGSEGV/SIGABRT`, `libUnreal.so`.
4. **توافق نظام/صلاحيات/تخزين:** ابحث عن `Permission denied`, `SecurityException`, `FileNotFoundException`. لا تطلب من المستخدم تعطيل حماية الجهاز أو منح صلاحيات عامة.

## 3. ترتيب جمع الأدلة عند العودة

### المسار الأول — Google Play Console (أفضل خيار من الهاتف دون توصيلات)

- `Play Console` → `CROWNFALL` → **Monitor and improve / المراقبة والتحسين** → **Android vitals / مؤشرات Android الحيوية** → **Crashes and ANRs / الأعطال**. فلتر `218` ثم انظر إلى الاستثناء والـstack trace إن وُجد؛ قد تتأخر المعلومات وقد تتطلب موافقة جهاز المختبر على مشاركة التشخيصات.
- افتح **Pre-launch report / تقرير ما قبل الإطلاق** → **Stability / الثبات** إن توفر لهذا الإصدار؛ بعض اختبارات Google توفر نموذج الجهاز والسجل والفيديو. قد لا يتوفر التقرير فورًا أو قد لا يعيد إنتاج العطل.
- شارك **السطور ذات الصلة فقط** أو صورة واضحة من الاستثناء، لا تفاصيل حساب المطور أو أرقام الأجهزة أو معلومات المستخدمين الآخرين.

### المسار الثاني — تسجيل من هاتف Android نفسه

- إذا لم تتوفر بيانات Google Play، يمكن تشغيل اللعبة مرة واحدة لتأكيد العطل، ثم **الإعدادات → خيارات المطور → أخذ تقرير عن خطأ / Take bug report**؛ الانتظار حتى ينتهي جمعه.
- **تحذير خصوصية:** تقرير bugreport قد يشمل معلومات شخصية، شبكة Wi-Fi، تطبيقات أخرى، معرفات وسجلات خاصة. لا ترفع ZIP الخام إلى GitHub أو مشاركته علنًا؛ ابدأ بإظهار الاستثناء المتعلق بـ`com.crownfall.stronghold` فقط بعد حذف المعلومات الحساسة.
- عند توفر كمبيوتر موثوق وADB، يمكن قراءة سجل `crash` عبر `adb logcat -b crash -d -v threadtime` وكذلك الرسائل المتعلقة بالتطبيق من `main` و`system`. لا تنشر السجلات الكاملة.

## 4. الأدوات التي أُعدت دون تغيير اللعبة

- `M121_AAB_AssetDelivery_ReadOnly.py`: يبحث داخل AAB عن وحدات `obbassets` وملفات OBB ومحتوياتها، ويتحقق من إعداد `bPackageDataInsideApk` ووجود تفعيل GooglePAD الصريح في الـuproject. يطبع **أعدادًا وحالات فقط**؛ رمز `REVIEW` ليس فشل تشغيل مثبتًا.
- `M121_Private_Crash_Clues_ReadOnly.py`: يقبل ملف تقرير نصي مفصول وآمن محليًا ويطبع عدادات مؤشرات (`NATIVE_CRASH`, `ASSET_DELIVERY`, `GRAPHICS`, `UNREAL_CONTENT` إلخ)، **لا يطبع نص السجلات** ولا يزعم اكتشاف السبب تلقائيًا.
- `test_M121_local.py`: خمس اختبارات اصطناعية للتحقق من سلوك الأدوات. **لم تُختبر هذه الأدوات على AAB الحقيقي أو الهاتف؛ لا يُسجّل أنها أثبتت السبب.**

## 5. سياسة التعديل قبل نسخة إصلاح جديدة

1. احفظ تفاصيل الخطأ مع وقت حدوثه واسم المكتبة وأول stack trace؛ إن لم يظهر، توقف عند فرضيات، ولا تعبث بملفات الخرائط.
2. طابق سجل التعطل مع **الضبط الفعلي في M106** لا مجرد الإعداد الموجود في GitHub، وحدد الفرق إن وجد.
3. أنشئ نسخة معزولة جديدة من المشروع، وغيّر الحد الأدنى **المثبت بالحجة التقنية** فقط. لا تمس `M63_REAL_MOBILE` أو `M84_EDITOR_SANDBOX_v218` أو M106/AAB218 الأصلية.
4. قبل أي بناء، افحص سياسة المتجر وتوفر versionCode جديد **أعلى من 218** (مثل 219 إذا كان متاحًا)، واستخدم مفتاح الرفع الموثوق دون كشفه؛ لا تكرر رقم 218.
5. بعد البناء، كرّر فحوص AAB والشهادة وManifest وtargetSdk و16KB والأصول، ثم **اختبار إقلاع محلي فعلي** قبل التحميل إلى Play Internal Testing؛ لا تعتبر نجاح Cook/Package ضمانة للتشغيل.
6. أوقف النشر العام والإعلانات/المختبرين الإضافيين حتى نجاح تشغيل نسخة الإصلاح داخل الاختبار الداخلي.

## 6. مراجع رسمية تمت مراجعتها

- Epic UE5.8 Google Play Asset Delivery: https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine
- Epic UE5.8 Android Support: https://dev.epicgames.com/documentation/en-us/unreal-engine/android-support-for-unreal-engine
- Epic UE5.8 Packaging Android: https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-android-projects-in-unreal-engine
- Google Play Crashes/ANRs: https://support.google.com/googleplay/android-developer/answer/9859174
- Google Play Pre-launch report: https://support.google.com/googleplay/android-developer/answer/9844487
- Android capture bugreport: https://developer.android.com/studio/debug/bug-report
- Android logcat: https://developer.android.com/tools/logcat

## 7. الأمن والحفظ

- كلمة مرور JKS سبق أن ظهرت داخل المحادثة؛ لا تُعاد كتابتها أو نسخها إلى السكربتات أو GitHub أو التقارير. تغيير Upload Key ينبغي أن يتم لاحقًا عبر إجراءات Google Play الرسمية إذا اقتضت خطة الحماية، لا أثناء تشخيص العطل.
- لا يمكنني الوصول إلى شاشة الهاتف أو السجلات الحية أو `Cloud Shell` ذاتيًا من هذه المحادثة؛ إجراء تحليل حاسم يتطلب لاحقًا سجل خطأ فعليًا أو تشغيل أدوات القراءة بموافقة اتصال المستخدم.
- كل سكربت/توثيق جديد يوضع في **فرع تشخيص معزول**، دون تفعيل GitHub Actions أو المساس بالفرع `main` أو نشر تطبيق جديد.