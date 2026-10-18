# CROWNFALL — أحدث نقطة موثقة M115 → بوابة M116 (19 أكتوبر 2026)

## الأدلة الأحدث (لا نبدأ من M60)
- الصورة التي قدمها المالك من جلسة SSH على جهاز `crownfall-m62-build` تظهر `M114_KEY_FOUND=PASS`، والتوقيع الناجح على JAR **تجريبي**، ثم `M114_CERTIFICATE=PASS` و`M114_SIGNING_COMPLETE=PASS` بعد مقارنة الشهادة العامة بمفتاح الرفع الأصلي.
- الصورة نفسها تعرض `M115_PROJECT=PASS`، `M115_SIGNING_KEY=PASS`، `M115_AUTOMATION_TOOL=PASS`، `M115_DISTRIBUTION=PASS`، `M115_ANDROID_CONFIG=PASS`، `M115_SHIPPING_CONTENT=PASS`، `M115_GRADLE_STATE=CLEAN`، و`M115_PREFLIGHT_COMPLETE`.
- الصورة تعرض أيضًا `M115_BUILD_NOT_STARTED=CONFIRMED`؛ لا يوجد دليل في هذه الصورة على Build/Package/Upload جديد للنسخة 218.
- تحذير self-signed على JAR الاختبار ليس فشل توقيع، ولكنه لا يثبت أن AAB النهائي موقّع أو مقبول في Google Play.

## مقارنة مع الحالة المحفوظة
- آخر commit على `m66-smart-recovery` وقت المراجعة هو `0aeb7fe30b68e0d266db94f8a8468bc4d434b7b9`، يتناول M108 وإعداد M109؛ تقدم VM تجاوز ما هو موثق هناك.
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
