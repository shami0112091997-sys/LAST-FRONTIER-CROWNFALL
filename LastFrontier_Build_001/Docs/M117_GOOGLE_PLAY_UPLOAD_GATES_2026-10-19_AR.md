# CROWNFALL — خطة إطلاق نسخة Android 218 إلى Google Play Internal Testing
**تاريخ التدقيق:** 19 أكتوبر 2026  
**المصدر:** سجلات VM المصوّرة M115–M116، مستودع LAST-FRONTIER-CROWNFALL، سجلات المكتبة السابقة، إرشادات Google Play وEpic الرسمية.  
**الحالة:** خطة تنفيذ وملفات تدقيق — **لم يبدأ بناء Release أو رفع إلى Google Play**.

## هدف محدد
رفع نسخة **LAST FRONTIER: CROWNFALL** بصيغة `.aab`، ذات `package=com.crownfall.stronghold`، و`versionCode=218` *إذا كان ما زال متاحًا في Play Console*، إلى قناة **Internal Testing** فقط. ليس إطلاقًا عامًا.

## الأدلة المؤكدة (على VM من صور المستخدم)
- M114: مطابقة شهادة الرفع عبر اختبار JAR تجريبي؛ ليس AAB للعبة.
- M115: `M115_PREFLIGHT_COMPLETE`، مع `M115_BUILD_NOT_STARTED=CONFIRMED`.
- M116: JKS موجود، SHA256 مطابق للنسخة الأصلية، وصلاحياته 600/400 مقبولة بحسب الفحص.
- M116: ملف `DefaultEngine.ini` مملوك للمستخدم ولا يمنح المجموعة/الآخرين أذونات قراءة أو كتابة.
- M116: قسم AndroidRuntimeSettings واحد، إعداد KeyStore وKeyAlias موجودان مرة واحدة، ولا يوجد حقل KeyStorePassword.
- M116: `M116_STORE_PASSWORD=PASS` بعد إدخال سري صحيح في الطرفية؛ لا يُطبع السر ولا يعاد استخدامه من الدردشة.
- M116: أربعة ملفات رئيسية (المشروع والخريطة الأصلية والمطبوخة ومكتبة arm64)، و`ForDistribution=True`، و`PPBC_Shipping`، و`StoreVersion=218` و`bEnableBundle=True` — **8 اختبارات وجود/قيم بسيطة نجحت**.

## السبب المؤكد لرفض حزمة 218 السابقة
الحزمة M90/M98–M105 كانت **Debug Gradle** رغم وجود `.so` Shipping في Unreal. وثّقت سجلات M105 ظهور مهام `bundleDebug` و`processDebugManifest`، وأظهر manifest سابق `debuggable=true`. لذلك **ممنوع إعادة توقيع AAB القديمة وتسميتها Release**. يلزم Gradle Release حقيقي، وتوقيع Upload Key المعتمد.

## بوابات الاستعداد قبل Build
1. **أولًا: Google Play Console:** في `Test and release → Latest releases and app bundles` أو `App bundle explorer` تحقق من **أعلى versionCode مسجّل**، بما فيه المسودات والاختبارات. كانت 217 هي أعلى نسخة ظهرت في الصور التاريخية؛ هذا غير كافٍ لإثبات أن 218 لم تُرفع لاحقًا. إذا كانت 218 مستخدمة، لا تبنِ بنفس الرقم؛ عدّل نسختك في sandbox بأمان قبل البناء وبعد التنسيق مع بيانات المتجر.
2. شغّل `M117_GooglePlay_Preflight_ReadOnly.sh` على VM الأصلي، داخل M106 دون أي تعديل. فحصه لا يقارن كلمة مرور ولا يُصدر Build.
3. **إذا ظهرت BLOCKED:** أوقف المحاولة وأصلح السبب؛ لا تكرر UAT تلقائيًا.
4. **إذا ظهر PRELIMINARY_READY:** أعد تجهيز `KeyStorePassword` بطريقة **مؤقتة ومقيدة الصلاحيات** في M106 وحده، عبر إدخال تفاعلي غير ظاهر؛ يُحفظ الأصل في نسخة احتياطية مقيّدة وتُستعاد إعداداته بعد المحاولة. امتنع عن نشر كلمة المرور في GitHub أو `ps` أو أوامر shell أو المحادثة أو ملفات build logs المرسلة للآخرين. تحقّق من عدم بقائها في ملفات Intermediate/Gradle بعد إنهاء العملية. لا تنشئ مفتاح JKS جديدًا أثناء هذا المسار.
5. عند اكتمال بوابات الأمان والمفتاح وGoogle Play versionCode ومساحة القرص، **تشغيل Build واحد فقط** على M106 باستخدام Unreal AutomationTool مع Android ASTC، `Shipping` و`-distribution`، إعادة Stage/PAK من المحتوى المطبوخ المحفوظ مع Package Release. تحقق من أن مهام Gradle تضمنت **`bundleRelease`** لا `bundleDebug`، وأن UAT انتهى برمز خروج 0 وأنتج AAB جديدة غير فارغة. لا تدمج أو تنشر شيئًا تلقائيًا.

## فحص AAB قبل رفعها
استخدم `M118_GooglePlay_AAB_ReadOnly_Audit.sh` للتحقق من:
- بنية ZIP سليمة، BundleConfig وAndroidManifest في وحدة base، ومكتبات arm64.
- **محتوى لعبة حقيقي** لا مجرد `UECommandLine.txt`: أرشيف OBB asset-pack أو PAK/UCAS/UTOC يزيد مجموع محتواه عن 5 MB في هذا المشروع.
- تحقق JAR signer وعدم وجود شهادة Debug؛ **SHA256 للشهادة العامة** يجب أن يطابق شهادة Upload Google Play الأصلية، لا بصمة JKS ولا شهادة App Signing المختلفة.
- `bundletool validate`، ومعاينة Manifest: `com.crownfall.stronghold`، `versionCode=218`، `targetSdkVersion=36`، و`debuggable` و`testOnly` غير موجودين أو `false`.
- مراجعة اصطفاف native libraries وbundle لصفحات 16KB. لا يعتبر اجتياز الأداة وحده إثبات تشغيل الهاتف الفعلي.
- فحص أذونات الشبكة وSDK/بيانات الخصوصية واتساق Data Safety والإعلانات والفئة العمرية مع النسخة الفعلية، لا وثائق WebView القديمة.

## بعد قبول الفحص
1. انسخ AAB **النهائية الموقّعة** من VM إلى Cloud Shell عبر نقل خاص وآمن، ثم نزّلها إلى الهاتف دون أي حاوية عامة أو روابط مشاركة مفتوحة.
2. في Google Play Console اختر تطبيق `CROWNFALL: Stronghold` → **Test and release → Testing → Internal testing → Create new release**، وارفع `.aab`، واستعرض التحذيرات وأخطاء Play؛ لا تنشر Production.
3. بعد قبول Google، اختبر التثبيت وفتح TestMap والحركة والتحكم والقتال والـHUD والأصول على هاتف حقيقي، ثم راجع Android vitals/Pre-launch report وتوافق الأجهزة قبل أي توسيع.
4. لا يعتبر إنشاء الملف على الخادم ولا الاختبار اليدوي بالهاتف وحده دليل إتاحته في متجر Google.

## مخاطر وقرارات أمنية مهمة
- كشف كلمة مرور JKS مسبقًا في المحادثة يزيد مخاطر التسريب. يُوصى بجدولة **إعادة تعيين Upload Key من Google Play** عند التخطيط الآمن لذلك، وليس إعادة إنشاء أو إعادة تعيين مفتاح App Signing الذي تديره Google. لا تقدِم على إعادة التعيين قبل فهم أثرها على الرفع الجاري وإعداد شهادة الرفع الجديدة؛ تحتاج إجراء رسمي في Play Console.
- لا تغيّر `M63_REAL_MOBILE` ولا `M84_EDITOR_SANDBOX_v218` ولا `main` أو ملفات Unreal الثنائية الأصلية.
- الفحوص الاصطناعية (12 حالة) تقيس منطق السكربتات فقط؛ لم تتصل بـVM أو Play Console أو تتحقق من AAB حقيقية.
- بعض إصدارات Unreal قد تنقل الاعتمادات مؤقتًا إلى مخرجات Gradle ضمن مساحة العمل. يُمنع نشر مجلد Intermediate أو سجلات تحتوي بيانات خاصة، وتجب مراجعة النسخ المؤقتة قبل مشاركتها.

## المرجع الرسمي
- Unreal 5.8 signing: https://dev.epicgames.com/documentation/en-us/unreal-engine/signing-android-projects-for-release-on-the-google-play-store-with-unreal-engine
- Unreal 5.8 Android settings: https://dev.epicgames.com/documentation/en-us/unreal-engine/android-settings-in-the-unreal-engine-project-settings
- Google Play target API 36 from 31 Aug 2026: https://support.google.com/googleplay/android-developer/answer/11926878
- Google Play Internal testing: https://support.google.com/googleplay/android-developer/answer/9845334
- Upload key reset: https://support.google.com/googleplay/android-developer/answer/9842756
- App version explorer: https://support.google.com/googleplay/android-developer/answer/9859152
- 16 KB page-size guidance: https://developer.android.com/guide/practices/page-sizes
- Bundletool: https://developer.android.com/tools/bundletool
## بوابة Google Play Version — تحقق مباشر من لقطة الشاشة (19 أكتوبر 2026، 03:54 بتوقيت قطر)
- فتح المالك شاشة **جميع حزم التطبيقات / All app versions** في حساب Play Console الخاص باللعبة. تظهر عبارة **5 إصدارات للتطبيق** وصفحة **1–5 من 5**.
- القائمة كاملة كما ظهرت في الصورة: `217 (2.2.0)`، `216 (2.2.0)`، `215 (2.2.0)`، `214 (2.1.2)`، `212 (2.1.2)`.
- **218 غير معروض ضمن أي من الإصدارات الخمسة في هذه الصفحة عند التصوير**؛ لذا `versionCode=218` هو الإصدار التالي المرشح، بشرط عدم حدوث رفع أحدث أثناء البناء ووجود أي إصدار بحالة معلقة في موضع آخر.
- إثبات وجود 217 لا يعني أن 218 موقعة أو مبنية: الحالة الفعلية لنسخة Unreal Release هي `NOT_BUILT_OR_UPLOADED` حتى آخر صورة.
- الانتقال إلى M117 Preflight للقراءة فقط، ثم تجهيز Distribution Signing داخل M106 وحده، ثم `bundleRelease` جديد، فحص AAB والمحتوى و16 KB قبل رفع الاختبار الداخلي. ممنوع إعادة توقيع حزمة M90 Debug واعتبارها Release.
- المصدر المرئي: صورة Play Console المرسلة بالمحادثة، التاريخ المحلي 19 أكتوبر 2026 ~03:54. المرجع الرسمي: https://support.google.com/googleplay/android-developer/answer/9844279/inspect-app-versions-with-the-app-bundle-explorer
