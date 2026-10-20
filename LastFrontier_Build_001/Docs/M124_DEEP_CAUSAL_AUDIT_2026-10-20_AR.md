# CROWNFALL — تحقيق سببي معمّق في إغلاق نسخة Google Play 218

**آخر مراجعة:** 20 أكتوبر 2026 (توقيت قطر)  
**نوع التحقيق:** تحليل السجلات التاريخية والمصدر المرجعي والوثائق الرسمية؛ لا وصول مباشر إلى هاتف المستخدم أو Google Play Console الخاص أو VM الأصلية.  
**نتيجة التشغيل الوحيدة المثبتة:** تطبيق `com.crownfall.stronghold` من قناة الاختبار الداخلي يُثبَّت ثم يظهر شعار Unreal Engine ويعود إلى Android في أقل من ثانية. **السبب الجذري لم يُحدّد بعد**.

## 1. ما أصبح مثبتًا من شواهد المشروع

1. استُخدم UE 5.8.3 في VM `crownfall-m62-build` ومجلد الإصدار المعزول `M106_RELEASE_SANDBOX_v218`.
2. M119 أجرى UAT مع `-skipbuild -skipcook -stage -pak -package -distribution`؛ النتيجة `EXIT=0` وظهور `bundleRelease`. أي أن بيانات Cook وبرنامج Shipping مُعاد استخدامهما من مراحل سابقة، وليست إعادة طبخ كاملة.
3. الحزمة الموقّعة 218 حجمها **117,411,826 بايت**، اجتازت ZIP وJAR signing و`bundletool validate` وManifest الحزمة/API36 وفحوص ARM64 و16KB. تطابق SHA-256 بين VM وCloud Shell عند نقل AAB.
4. يوجد محتوى لعب حقيقي، ومن ضمن ملف AAB وحدة `obbassets` و`main.obb.png` (المسار يظهر في نتائج الفحوص القديمة). نجاح بنية الحزمة ليس ضمانًا لوصول ملفاتها إلى محرك Unreal.
5. Google Play أتاح الرابط وأكمل التثبيت؛ لم تصل اللعبة إلى شاشة الخريطة أو التحكم. لم يقدم الهاتف `logcat` أو `ApplicationExitInfo` أو Stack Trace بعد.
6. فشل قديم في تسلسل ملف خريطة M60 (`FName index`)، لكن M85 تحقق من تحميل `TestMap` في Unreal Editor لاحقًا وم86 طبخ 220 حزمة Android ASTC؛ ليس لدينا دليل أنه سبب المشكلة الحالية. لا نعدّل الخريطة دون أثر خطأ حديث.

## 2. تقييم فرضيات العطل حسب أولوية الفحص، وليس الاحتمال الإحصائي

| الأولوية | فرضية | دليل لصالح فحصها | ما الذي قد ينفيها أو يؤكدها؟ |
|---|---|---|---|
| عالية | تناقض تسليم بيانات OBB/PAD | `.uproject` المرجعي يعطّل إضافات المحرك افتراضيًا ولا يُدرج `GooglePAD`، بينما `DefaultEngine.ini` المرجعي يتضمن `bPackageDataInsideApk=True`، ويوجد `obbassets` فعلًا في AAB | نسخة M106 الفعلية، Manifest وحدة `obbassets`، وأثر `LogPakFile` أو `GooglePAD` من الجهاز |
| عالية للفحص القريب | عدم تطابق دالة JNI بين `libUnreal.so` و`classes.dex` | حالة معروفة في منتدى Epic لـGooglePAD تنتهي بعد Splash بخطأ `Failed to find Method`. الإصدارات مختلفة، لذلك هو نموذج خطأ فقط | ظهور `NoSuchMethodError` / `AndroidThunkJava_GooglePAD` في سجل الجهاز؛ مقارنة ثابتة غير حاسمة بين `.so` و`.dex` في AAB |
| متوسطة | فشل تحميل مكتبة native أو دالة ديناميكية | التشغيل ينتهي قبل المشهد؛ ELF alignment صالح لكنه لا يتحقق من `dlopen` وتبعيات الرموز | `UnsatisfiedLinkError` / `dlopen failed` / `linker` في logcat |
| متوسطة | Vulkan/RHI/تعريفات GPU | المرجع يضبط `bSupportsVulkan=True`؛ تختلف دعم وأخطاء تعريفات الأجهزة | `VK_ERROR`, `RHIInit`, EGL أو backtrace من تعريف الرسومات؛ موديل الهاتف مطلوب للتوافق |
| متوسطة-منخفضة | ملفات Cook/Map/Shader لم تُحمَّل أو تنقصها إعدادات التوزيع | UAT إعادة استخدام Cook وBuild قد تبقي مشكلة خفية؛ نجاح Cook لا يثبت إقلاعًا | `Failed to open descriptor`, `PakFile`, `ShaderCodeLibrary`, `Failed to load package`, `TestMap` |
| غير محددة | إنهاء نظام Android/الذاكرة/توقف طبيعي | العودة للشاشة لا تميز crash من force finish أو exit | `ApplicationExitInfo` وbuffer crash/main/system |
| أدنى دون دليل | API 36 وحده أو إغلاق حساب Play | API36 قد يغيّر السلوك، لكن Android 16 تغييرات واجهة/عودة لا تفسّر وحدها إغلاقًا آنيًا؛ Play قبِل التثبيت | تقرير استثناء صريح أو تعارض Android 16 مؤكد، لا التخمين |

**قيود منهجية أساسية:** ملف المرجع في GitHub يحمل `StoreVersion=215` بينما M106 المستخدم في الحزمة رفع رقم 218؛ إذًا هناك فروق مثبتة بين المرجع والبناء الفعلي. لا ننسب قيمة أي إعداد من المستودع تلقائيًا إلى AAB النهائية.

## 3. أدلة موثوقة من التوثيق الرسمي

- وفق Epic UE 5.8: إضافة GooglePAD مفعلة افتراضيًا في الحالة الطبيعية؛ عند استخدام install-time OBB ينبغي ضبط GooglePAD وفق الوثائق وتعطيل `Package Data inside APK`. لكن `DisableEnginePluginsByDefault=true` قد يغير الحالة الفعلية؛ يلزم فحص إعدادات M106 لا الاكتفاء باسم الإضافة.
- وفق Google Play: asset pack من نوع `install-time` يجب أن يكون متاحًا عند إطلاق التطبيق؛ من نوع `fast-follow` قد يصل بعد تثبيت التطبيق. لذا صفة `install-time` وحدها لا تفسر عدم وجود ملفات؛ يحتاج التشخيص إلى دليل أن Unreal لم يجد مسارها/لم يستطيع تركيب الأرشيف.
- تعليقات مجتمع Epic (UE4 قديم) تصف `NoSuchMethodError: AndroidThunkJava_GooglePAD_Available` و`Failed to find Method` مباشرة بعد splash. هذا **تشابه أعراض** لا يصلح برهانًا لتطبيق UE5.8.3 الحالي؛ يجب فحص `libUnreal` وDex وسجل الهاتف.
- وثائق Epic الخاصة بـUE 5.8 توصي Android SDK35 ضمن toolchain موثق، بينما M106 يستهدف API36 استجابة لسياسة Play لعام 2026. فارق الاختبار سبب لمراجعة التوافق بعد ظهور السجل، **وليس تشخيص crash قائم بذاته**.

## 4. ثلاث أدوات آمنة، كل واحدة تجيب سؤالًا مختلفًا

**M121:** يراجع وجود وحدات الأصول، عدد المكتبات والأرشيفات.  
**M122:** يقرأ Manifest `obbassets` عبر نسخة `bundletool` موثقة SHA256 ويحدد INSTALL_TIME/FAST_FOLLOW/ON_DEMAND ويقارن .uproject وini داخل M106.  
**M124 (جديد):** يفحص **AAB الحالية للقراءة فقط** باحثًا عن أسماء GooglePAD/JNI داخل ملفات `*.so` (أصلية) و`*.dex` (Java). اختبارًا محليًا اصطناعيًا حقق 8/8. **وجود نص دالة في كلا الملفين لا يثبت أنها معرفة أو قابلة للنداء، وغيابه لا يثبت عدم وجودها.** اكتشاف اسم JNI داخل Native دون Dex يؤسس أولوية أعلى لفحص `NoSuchMethodError` على الهاتف، وليس إصلاحًا آليًا.

أمر M124 الافتراضي على **VM الأصلية فقط**، بعد نقل البرنامج إليها بطريقة خاصة والتحقق من نصه:

```bash
python3 "$HOME/crownfall/M124_AAB_JNI_Crosscheck_ReadOnly.py"
```

يستهدف الحزمة الموجودة في `M106_RELEASE_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab`. لا يطبع أسرارًا أو محتوى ملفات أو مسارات ملفات؛ يُظهر أسماء مؤشرات ثابتة وأرقامًا محدودة. لا يُعيد بناء اللعبة ولا يغيّرها. إذا كان البرنامج غير موجود على VM، فلا تعتبِر أن الفحص نُفذ؛ ارفعه إليه أولًا بعد مراجعة مصدره.

## 5. الطريق الأقصر للحصول على السبب الحقيقي

**الخيار الأول (هاتف فقط، دون توصيل ADB):** Google Play Console → `Test and release` → `Testing` → `Pre-launch report` → `Details` → `Stability`؛ افتح فشل الإصدار 218 إن توفر. وبخلاف ذلك `Monitor and improve` → `Android vitals` → `Crashes and ANRs`، اختيار الإصدار 218 ثم تفاصيل stack. تقارير Pre-launch قد تعمل تلقائيًا حسب سعة مختبر Google؛ لا يمكن افتراض أنها اكتملت.

**الخيار الثاني (جهاز ADB موثوق فقط، إن كان متاحًا):** بعد فتح اللعبة مرة واحدة وجمع وقت الفشل:

```bash
adb shell dumpsys activity exit-info com.crownfall.stronghold
adb logcat -b crash -d -v threadtime
```

فحص exit-info يحدد إن كانت العملية `APP CRASH(NATIVE)` أو `APP CRASH` أو `SIGNALED` أو `LOW MEMORY` حسب ما سجّله النظام. بعد معرفة PID الصحيح يمكن مراجعة مقتطفات logcat ذات العلاقة فقط. قد تتضمن السجلات معرفات وتفاصيل شخصية؛ لا ترسل خام `bugreport` أو `logcat` الكامل في المحادثة أو GitHub. أرسل **مقتطف الاستثناء/السبب بعد تنقيح البيانات الحساسة**.

## 6. قواعد السلامة وبوابة الإصلاح

1. لا تتسبب بتكرار العطل عشرات المرات، ولا تمسح بيانات اللعبة أو تلغي تثبيتها قبل جمع الدليل.
2. لا تغير GooglePAD وVulkan وSDK وCook دفعة واحدة؛ تحقق من عطل واحد، عدّل سببًا واحدًا، ثم اختبر نسخة معزولة.
3. إن تم تغيير plugin/native code أو pack/cook settings، فلا يُسمح باستعمال ثنائيات/أصول قديمة عبر `-skipbuild` و`-skipcook` تلقائيًا.
4. أي إصلاح يُرقّم `versionCode > 218` بعد التحقق من الأرقام المتاحة، ويُختبر محليًا قبل رفعه **إلى Internal Testing فقط**.
5. تبقى المفاتيح الخاصة والـJKS وسجلات Gradle السرية على VM، والفروع `main` و`m66-smart-recovery` ونسخ M63/M84/M106 بلا تغيير.
6. هذا التحقيق **لم** يحصل على سجل الهاتف أو بيانات Android Vitals الخاصة، **ولم** يفحص ملف AAB النهائي bytes مباشرة في جلسة ChatGPT؛ أي ادعاء بغير ذلك غير صحيح.

## المراجع

- Epic GooglePAD UE5.8: https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine
- Epic Android development requirements UE5.8: https://dev.epicgames.com/documentation/unreal-engine/android-development-requirements-for-unreal-engine
- Epic plugin architecture: https://dev.epicgames.com/documentation/en-us/unreal-engine/plugins-in-unreal-engine
- Google Play Asset Delivery modes: https://developer.android.com/guide/playcore/asset-delivery
- Google Play pre-launch report: https://support.google.com/googleplay/android-developer/answer/9842757
- Android native crash debugging: https://developer.android.com/ndk/guides/debug
- Android ActivityManager historical process exits: https://developer.android.com/reference/android/app/ActivityManager
- Android logcat: https://developer.android.com/tools/logcat
- Epic forum symptom example (UE4, not proof): https://forums.unrealengine.com/t/google-play-asset-delivery-crash-after-splash-screen/210162