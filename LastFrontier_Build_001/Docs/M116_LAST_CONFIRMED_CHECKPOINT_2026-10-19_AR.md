# CROWNFALL — أحدث نقطة موثقة M115 → بوابة M116 (19 أكتوبر 2026)

## الأدلة الأحدث (لا نبدأ من M60)
- الصورة التي قدمها المالك من جلسة SSH على جهاز `crownfall-m62-build` تظهر `M114_KEY_FOUND=PASS`، والتوقيع الناجح على JAR **تجريبي**، ثم `M114_CERTIFICATE=PASS` و`M114_SIGNING_COMPLETE=PASS` بعد مقارنة الشهادة العامة بمفتاح الرفع الأصلي.
- الصورة نفسها تعرض `M115_PROJECT=PASS`، `M115_SIGNING_KEY=PASS`، `M115_AUTOMATION_TOOL=PASS`، `M115_DISTRIBUTION=PASS`، `M115_ANDROID_CONFIG=PASS`، `M115_SHIPPING_CONTENT=PASS`، `M115_GRADLE_STATE=CLEAN`، و`M115_PREFLIGHT_COMPLETE`.
- الصورة تعرض أيضًا `M115_BUILD_NOT_STARTED=CONFIRMED`؛ لا يوجد دليل في هذه الصورة على Build/Package/Upload جديد للنسخة 218.
- تحذير self-signed على JAR الاختبار ليس فشل توقيع، ولكنه لا يثبت أن AAB النهائي موقّع أو مقبول في Google Play.

## مقارنة مع الحالة المحفوظة
- آخر commit على `m66-smart-recovery` عند مراجعة 19 أكتوبر هو `e9ddb2465fdfca818a89fdc64d81d7f9b43109f8` (توثيق M113B/اختبار المفتاح المحلي). تقدم VM الظاهر في الصورة وصل M115، وهو أحدث من المحتوى الموثق في m66.
- `M106_RELEASE_SANDBOX_v218` على VM نسخة مستقلة؛ يجب الحفاظ على `M63_REAL_MOBILE` و`M84_EDITOR_SANDBOX_v218` ونسخ JKS الأصلية.
- في M90 وM91 ظهرت AAB Debug بسعة 73,612,837 بايت، ورفض Play إصدار Debug؛ لن نعيد توقيع هذه الحزمة ثم نسميها Release.
- الـJKS المتوقع: `Build/Android/CROWNFALL_v0.8_upload_key.jks` داخل M106، alias `crownfall-upload`، مع مطابقة SHA-256 **لملف JKS** المعروف من سجل الاستعادة، وليس نشر المفتاح أو كلمة مروره.

## M116 — خطوة التنفيذ التالية
1. استخدام `Scripts/M116_Release_Signing_ReadOnly_Gate.sh` على جهاز VM للتحقق *قراءة فقط* من أصل النسخة، ملف JKS، البصمة، صلاحيات الملف، إعدادات Distribution ونسخة 218 ووجود إعدادات Unreal Distribution Signing دون كشف أي كلمة مرور.
2. إن ظهرت `KEYSTORE_SETTING_NOT_CONFIGURED` أو `KEY_ALIAS_NOT_CONFIGURED` أو `KEYSTORE_PASSWORD_NOT_CONFIGURED`: **توقف**. ينبغي تجهيز إعدادات التوقيع بصورة محلية مؤقتة ومحميّة خارج GitHub قبل UAT. لا تطلب كلمة المرور في الدردشة، ولا تطبع محتوى ini.
3. إذا ظهر `M116_READONLY_GATE=PASS`: وضع خطة Build واحدة مستقلة بعد التأكد من عدم وجود إصدار 218 مستخدم في Play Console، وحدود التكلفة والتخزين. يتطلب UAT الحقيقي `Shipping` و`-distribution` مع بناء حزمة Gradle Release، وليس `bundleDebug`.
4. بعد الحزمة: التحقق من manifest `android:debuggable=false` أو غيابه، إصدار `218`، package `com.crownfall.stronghold`، شهادة رفع Google Play الأصلية، `bundletool validate` وأصول Unreal/ARM64، ثم تجربة Internal Testing فقط بعد فحص مستقل.
5. لا تمس الفروع `main` أو `m66-smart-recovery` ولا تعدّل أي ملف Unreal ثنائي، ولا تشغّل GitHub Actions تلقائيًا.

## سلامة الحساب والسرية
- هذا المستند **لا يتضمن مفاتيح أو كلمات مرور**. لا يثبت أي سطر PASS تنفيذ Build أو Google Play Upload جديدًا.
- استعمل توجيهات المالك في ملف `PROJECT_OPERATING_RULES_2026-10-19_AR.md` بفرع `policy/safe-work-rules-2026-10-19`.
- إرشادات Epic: https://dev.epicgames.com/documentation/en-us/unreal-engine/signing-android-projects-for-release-on-the-google-play-store-with-unreal-engine
- إعدادات UE Android: https://dev.epicgames.com/documentation/unreal-engine/android-settings-in-the-unreal-engine-project-settings

## إضافة مراجعة أمنية — بوابة M116 المحسنة (19 أكتوبر 2026)
- تم تحديث `Scripts/M116_Release_Signing_ReadOnly_Gate.sh` إلى مراجعة ثانية أكثر تحفظًا. لا تُصدر أمر Build، ولا تفتح JKS، ولا تطلب كلمة مرور، ولا تطبع قيم إعدادات التوقيع أو تعدل ملفات الـVM.
- تقرأ فقط وجود .uproject وTestMap الأصلية والمطبوخة وملف Shipping arm64 وRunUAT، وتتحقق من إعدادات Shipping/Distribution وPackageName وStoreVersion 218 وTargetSDKVersion 36 وBundle.
- تفحص ملف JKS المحلي فقط: عدم وجود symbolic link، مالك الملف، صلاحيات وصول المجموعة والآخرين، وتطابق SHA256 **للملف** مع البصمة الموثقة سابقًا؛ لا تعني مطابقة البصمة أن كلمة المرور أو إعداد Unreal للتوقيع صحيحة.
- تفحص حقول KeyStore وKeyAlias وKeyStorePassword في `DefaultEngine.ini` دون طباعة قيمة كلمة المرور. KeyPassword يمكن أن تكون فارغة إذا تطابقت مع كلمة مرور Keystore بحسب إرشادات Epic.
- إذا ظهر حقل كلمة مرور في Config قابل للقراءة من المجموعة/الآخرين، تتوقف البوابة. وإذا كانت القيمة موجودة في إعداد خاص محدود الوصول، تصنفها للمراجعة ولا تعتبر ذلك إثبات توقيع نهائي.
- **مخرجات مرحلة M116 المحسنة مقصودة على شكل HOLD:** `M116_AUDIT_COMPLETE=PASS` يعني اكتمال فحصها المحدود فقط، و`M116_RELEASE_BUILD_AUTHORIZED=NO` مع `M116_GATE=HOLD_FOR_PRIVATE_SIGNING_SETUP` يعني أن بناء Release ما زال معلقًا لحين إعداد توقيع خاص آمن وفحص حالة versionCode في Play. رمز الخروج 3 عند انتهاء الفحص بلا خطأ هو إيقاف سلامة مقصود، وليس تعطل Unreal.
- اختبارات محلية اصطناعية سبعة للفحص (دون أي JKS حقيقي أو كلمات مرور حقيقية): الحالة الأساسية، مفتاح مفقود، رقم إصدار غير صحيح، أذونات مفتاح متساهلة، Intermediate/Android موجود، كلمة مرور في ini قابل للقراءة، وكلمة مرور في ini محدود الوصول — جميعها طابقت النتائج المتوقعة. **هذا ليس تنفيذًا على VM.**
- اختبارات محلية بأداة sha256sum اصطناعية تؤكد التفرع المنطقي للسكربت فقط؛ لم يتم تقديم دليل حقيقي جديد على صحة ملف JKS الموجود على VM ولا على Build.
- لا ترفع أي ملفات خاصة إلى GitHub أو تعيد استخدام AAB القديم بتوقيع Debug. لا تغيّر main أو m66 أو M63/M84، ولا تعيد كتابة TestMap.
- التالي: تشغيل البوابة المحسنة على **VM الأصلية** ضمن جلسة موثوقة ومراجعة مخرجاتها غير السرية؛ بعدها تجهيز توزيع Signing مؤقت ومحدود الصلاحيات دون نشر الأسرار أو حفظها في GitHub؛ ثم بناء Release مضبوط واحد مع فحص bundleRelease وAndroid manifest والشهادة والأصول، وبعدها اختبار داخلي على الجهاز.
