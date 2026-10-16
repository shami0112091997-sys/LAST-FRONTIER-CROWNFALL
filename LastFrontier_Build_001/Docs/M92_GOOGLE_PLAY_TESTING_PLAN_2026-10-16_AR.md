# CROWNFALL M92 — خطة اختبار Google Play (16 أكتوبر 2026)

## الهدف
الاختبار الحقيقي من Google Play فقط، وليس النشر العام أو تأكيد جودة AAA من دون قياس الجهاز. تُمنع مشاركة مفاتيح JKS وكلمات المرور عبر GitHub أو المحادثة.

## آخر حالة مؤكدة
- M78 Android Shipping Compile PASS، M85 Editor/World load PASS، M86 Cook PASS (220 packages)، M88 Stage/Pak PASS، M89 خمسة أرشيفات PASS.
- M90 Packaging على M84 المحمية PASS: AAB جديد 73,612,837 بايت في `$HOME/crownfall/M84_EDITOR_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab`. لم تُفحص محتوياته أو شهادة توقيعه بعد.
- إعدادات المشروع: `com.crownfall.stronghold`، الإصدار 218، targetSDK36؛ يجب إثبات القيم الفعلية في Manifest. الحزمة القديمة M77 (41,916,003 bytes) ذات توقيع Android Debug وبلا بيانات اللعبة المعبأة بالكامل، ولا يجوز رفعها.
- شهادة مفتاح رفع Google Play من DER/نسختي JKS العامة: SHA256 `40:C0:DB:40:40:BE:0B:F9:B2:50:BD:4D:64:F9:7E:34:05:33:06:C2:C0:25:DC:3F:86:EC:48:BC:2A:DE:A1:B8`.

## بوابة G1 قبل أي رفع
تشغيل فحص M91 للقراءة فقط على AAB **M90**: سلامة ZIP، BundleConfig.pb وAndroidManifest.xml وDEX وARM64، وجود ملفات بيانات لعبة فعلية (.pak/.ucas/.utoc أو ما يعادلها بأرشيفات الوحدات)، `keytool -printcert -jarfile` لمعرفة شهادة الموقّع، `jarsigner -verify`. إن توفر bundletool، فحص `validate` وmanifest package/versionCode/targetSdk، والتوافق مع صفحات 16KB. لا يُستنتج نجاح الحزمة من الحجم فقط. أي فشل = لا رفع ولا إعادة بناء عشوائية.

## المسار A — Internal App Sharing للاختبار السريع أولًا
مرجع: https://support.google.com/googleplay/android-developer/answer/9844679?hl=en
- Google Play Console > CROWNFALL > Test and release > Internal testing > Internal app sharing (قد يظهر أيضًا Setup > Internal app sharing).
- يسمح Google برفع AAB موقّع بأي مفتاح (حتى Debug) وإعادة توقيعه بشهادة خاصة بالمشاركة الداخلية، بدون استخدام JKS الأصلي. **ليس** إصدار Internal Testing رسميًا ولا يحتسب للاختبار المغلق المطلوب للإنتاج.
- بمجرد اجتياز G1: نقل AAB M90 من VM إلى جهاز/متصفح خاص مؤمّن، لا استضافة عامة؛ السماح فقط لمختبرين موثوقين أو قائمة بريدية وعدم نشر رابط الاختبار علنًا؛ رفع الحزمة ووضع تسمية M90 QA 218، ومشاركة الرابط. حد 100 مستخدم لكل رابط، وصلاحية الرابط 60 يومًا.
- على جهاز المختبر: Google Play Store > Settings > About > النقر على Play Store version سبع مرات > تفعيل Internal app sharing؛ افتح الرابط من حساب مخوّل. اختلاف شهادة هذا المسار عن النسخ المثبتة سابقًا قد يتطلب إلغاء النسخة الموجودة (مع نسخ بيانات الحفظ مسبقًا).

## المسار B — Internal Testing الرسمي
مرجع: https://support.google.com/googleplay/android-developer/answer/9845334?hl=en
- يحتاج AAB موقّعًا بمفتاح الرفع المسجّل (ليس Debug)، ومطابقة شهادة SHA256 أعلاه، وبيانات Manifest الفعلية: `com.crownfall.stronghold` وversionCode218 وtargetSDK36 وARM64 و16KB. المفتاح الخاص يبقى في بيئة محمية، ولا يُرفع إلى GitHub.
- Google Play Console > Test and release > Testing > Internal testing > Testers: إنشاء قائمة بريدية تصل حتى 100 مختبر، عنوان لاستقبال الملاحظات وحفظ الإعدادات؛ ثم Create release/إدارة إصدار، رفع AAB المطابق، مراجعة تحذيرات Play قبل طرحه داخليًا للمختبرين فقط. قد يستغرق ظهور رابط المشاركة عدة ساعات.
- اختبار التنزيل والتثبيت عبر Google Play؛ مقارنة الأجهزة والتشغيل ومشاكل Crash/ANR/رسومات ناقصة/FPS، ثم مراجعة Pre-launch report وAndroid Vitals إن توفرا. لا نشر إنتاجي.

## متطلبات الإنتاج منفصلة
- Google Play للهواتف يشترط API36 للإصدارات الجديدة والتحديثات منذ 31 أغسطس 2026: https://support.google.com/googleplay/android-developer/answer/11926878?hl=en .
- الحسابات الشخصية التي أُنشئت بعد 13 نوفمبر 2023 قد تحتاج اختبارًا مغلقًا بـ12 مختبرًا لمدة 14 يومًا متصلة قبل طلب الوصول إلى الإنتاج، ولا يغني الاختبار الداخلي أو المشاركة الداخلية عنه: https://support.google.com/googleplay/android-developer/answer/14151465?hl=en .
- راجع تقرير ما قبل الإطلاق للتوافق والأداء والأعطال: https://support.google.com/googleplay/android-developer/answer/9842757?hl=en .

## الخطوة المطلوبة
انتظر نتائج M91 للملف M90 الجديد. ثم بناءً على سلامة الأصول والتوقيع نختار مشاركة التطبيقات داخليًا عبر Google (إن كان Debug) للاختبار السريع، وبعدها الإصدار الرسمي لقناة Internal Testing بالمفتاح الأصلي. **لم تُنفذ أي عملية رفع إلى Google Play في M92**.
