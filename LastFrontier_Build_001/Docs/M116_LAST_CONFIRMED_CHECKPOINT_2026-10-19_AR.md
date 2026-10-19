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

## نتيجة VM جديدة: فحص M116 الأولي من صورة 19 أكتوبر 2026 ~03:01 بتوقيت قطر
- الصورة المباشرة بعد اتصال SSH بالخادم الأصلي `crownfall-m62-build` تظهر:
  - `M116_KEY=FOUND` (وجود غير فارغ، لم يُقارن SHA أو الصلاحيات في هذا الفحص).
  - `M116_KeyStore=SET`.
  - `M116_KeyAlias=SET`.
  - `M116_KeyStorePassword=NOT_SET`.
  - `M116_READONLY_CHECK_COMPLETE`.
- هذا فحص Bash مختصر للوجود وأسماء إعدادات التوقيع وليس تشغيل سكربت `M116_Release_Signing_ReadOnly_Gate.sh` الكامل؛ لم يحدث `M116_READONLY_GATE=PASS` ولا `bundleRelease` ولا إصدار AAB جديد.
- التشخيص: اسم الـJKS والـalias مضبوطان لكن `KeyStorePassword` غير مضبوط في `Config/DefaultEngine.ini` الخاص بـM106. هذا **لا** يعني تلف أو فقدان كلمة المرور الأصلية؛ سجلات M114 أثبتت نجاح التوقيع التجريبي.
- تعليمات السلامة: لا تدخل كلمة المرور في GitHub أو المحادثة أو مخرجات `grep` أو سطر الأوامر؛ التحقق التالي SHA-256 للـJKS ومُلكيته والصلاحيات فقط، ثم تصميم مسار توقيع مؤقت وخاص وفق Unreal 5.8 قبل أي Build Release. لا تمس الأصل M63/M84 ولا تعرض أية أسرار.
- مصادر رسمية: https://dev.epicgames.com/documentation/en-us/unreal-engine/android-settings-in-the-unreal-engine-project-settings ؛ https://dev.epicgames.com/documentation/en-us/unreal-engine/signing-android-projects-for-release-on-the-google-play-store-with-unreal-engine

## نتيجة موثقة جديدة — M116 JKS Integrity من صورة VM (19 أكتوبر 2026 ~03:03 بتوقيت قطر)
- نفّذ المالك عبر SSH على `crownfall-m62-build` فحصًا للقراءة فقط للملف `$HOME/crownfall/M106_RELEASE_SANDBOX_v218/Build/Android/CROWNFALL_v0.8_upload_key.jks`.
- مخرجات الصورة: `M116_KEY_SHA256=PASS`, `M116_KEY_PERMISSIONS=PASS`, `M116_KEY_AUDIT_COMPLETE`.
- الفحص قارن SHA-256 لملف JKS مع البصمة المعروفة مسبقًا؛ واختبر أن صلاحيات الملف `600` أو `400`، ولم يعرض كلمة المرور أو يستخدم المفتاح للتوقيع.
- نطاق النتيجة: تطابق ملف JKS والموافقة على معيار الصلاحيات المختصر؛ **ليس** دليل صحة إعداد KeyStorePassword في Unreal، ولا بناء AAB Release جديد، ولا قبول Play.
- آخر عائق معروف: `M116_KeyStorePassword=NOT_SET` في `Config/DefaultEngine.ini` الخاص بالـM106 sandbox، بينما `KeyStore=SET` و`KeyAlias=SET`. لا تُدخل كلمة مرور في محادثة أو GitHub أو أمر ظاهر.
- الخطوة التالية: فحص مالك وصلاحيات `DefaultEngine.ini` دون طباعة محتوى الملف أو أي سر؛ ثم اعتماد أسلوب مؤقت وآمن لتزويد إعداد Distribution Signing بالاعتماد الصحيح في sandbox وحده، والتحقق من versionCode في Play قبل بناء Release واحد. أبقِ `main` و`m66` ومجلدات M63/M84 كما هي.

## VM checkpoint M116 — Android configuration file protection (user screenshot ~03:09 Qatar, 19 October 2026)
- Shell session confirmed on `crownfall-m62-build` in isolated `$HOME/crownfall/M106_RELEASE_SANDBOX_v218`.
- The owner reported `M116_CONFIG_OWNER=PASS`, `M116_CONFIG_PRIVACY=PASS`, `M116_CONFIG_AUDIT_COMPLETE` from a read-only test of `Config/DefaultEngine.ini`. This test checks ownership and that group/other permission bits are zero (does not reveal passwords).
- Previous checkpoints: `M116_KEY_SHA256=PASS`, `M116_KEY_PERMISSIONS=PASS`; configuration fields `KeyStore=SET`, `KeyAlias=SET`, `KeyStorePassword=NOT_SET`.
- Security interpretation: no reason to recreate JKS. Do not write or publish signing password to GitHub, shell history, or chat; do not yet claim M116 full gate, bundleRelease, signed AAB, or Play upload.
- Next logical phase: inspect the **structure only** of the AndroidRuntimeSettings INI section and duplicate signing field counts, without printing values; then privately verify original credentials and apply release-only signing configuration to isolated M106 with secure rollback. Never alter M63 or M84.
- Epic Android settings documentation: https://dev.epicgames.com/documentation/en-us/unreal-engine/android-settings-in-the-unreal-engine-project-settings

## M116 Android Signing Layout — user VM screenshot 19 October ~03:14 Qatar
- On verified original `crownfall-m62-build`, read-only awk returned `M116_ANDROID_SECTIONS=1`, `M116_KEYSTORE_FIELDS=1`, `M116_ALIAS_FIELDS=1`, `M116_PASSWORD_FIELDS=0`, `M116_SIGNING_LAYOUT=PASS`.
- Interpretation: exactly one `[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]` section, one `KeyStore` field, one `KeyAlias`, and no `KeyStorePassword` field at present in isolated M106's `DefaultEngine.ini`. This PASS is only the **layout/uniqueness predicate**; it does not validate field values, execute private-key signing, perform Build/Cook/Package, or imply Play acceptance.
- Next gated step is **one confidential password validation** on VM using the existing original JKS and Java keytool `-storepass:env`, entered via an invisible interactive prompt. Never write the password into GitHub/chat/command-line args; avoid retry loops. If it passes, plan ephemeral, backup-and-rollback Release-only configuration inside M106 and review logs/secrets exposure before one `bundleRelease` packaging attempt. `KeyPassword` may remain blank when it equals store password per Epic.
- References: https://docs.oracle.com/en/java/javase/17/docs/specs/man/keytool.html and https://dev.epicgames.com/documentation/en-us/unreal-engine/android-settings-in-the-unreal-engine-project-settings

## M116 VM interactive keytool check — 19 October ~03:18 Qatar
- New owner-provided VM screenshot displays a **single** hidden-input `keytool -list -storetype JKS -alias crownfall-upload -storepass:env M116_STORE_PASS` attempt and output `M116_STORE_PASSWORD=FAIL`.
- The earlier one-liner redirected both tool stdout/stderr to `/dev/null`. The result is an **undifferentiated negative**; no specific underlying reason is known. Do **not** infer corrupt JKS, incorrect recovery record, wrong alias, or broken key from this alone.
- This does not contradict confirmed `M116_KEY_SHA256=PASS`, `M116_KEY_PERMISSIONS=PASS`, `M116_CONFIG_OWNER=PASS`, `M116_CONFIG_PRIVACY=PASS`, `M116_SIGNING_LAYOUT=PASS`, or the M114 independent signing success. None of those prove remote Java's environment/passphrase intake.
- Hold UAT and any release signing configuration until diagnostics. Avoid repeated password guesses. The immediate next **read-only, credential-free** check should verify `command -v keytool`, `java -version`, `keytool -list --help` availability, and `[ -t 0 ]` interactive stdin without printing any secret. If these work, plan a controlled, single follow-up invocation that retains sanitized error **category only** and never leaks entered secrets.
- Preserve M106 sandbox, source backups, key, GitHub branches, and previous AAB. No release build/upload was started from this screenshot.

## M116 clarification — original user did not enter password
- User explicitly clarified after the screenshot that **no password was entered** during the earlier M116 terminal interaction. This accounts for the observed `M116_STORE_PASSWORD=FAIL`: the failure is an uncompleted/empty-password verification, **not evidence of wrong credentials** or JKS corruption.
- Earlier M114 offline/private-key-signing PASS, JKS hash PASS, and permissions PASS remain valid.
- Do not retry with arbitrary guesses. Next: on the original trusted VM, start `keytool -list -storetype JKS -keystore "$K" -alias crownfall-upload` with a real interactive password prompt, enter the existing original password on that terminal **only** (not in chat or saved script). Check result before any release build. No version 218 release bundle has been shown.

## M116 original JKS password validated — VM screenshot ~03:29 Qatar
- User provided new Cloud Shell screenshot on `crownfall-m62-build`, showing a **second** test with actual password entry: `M116_STORE_PASSWORD=PASS` and `M116_PASSWORD_CLEARED`.
- Test ran Java `keytool -list -storetype JKS -keystore "$K" -alias crownfall-upload -storepass:env M116_STORE_PASS` with stdout/stderr suppressed. This verifies keystore access and alias under supplied credentials, **not** yet Unreal Distribution Signing, key-specific password usage, or signed release AAB.
- The previous `FAIL` was explained by user not entering any password, not an authentication failure.
- Existing checkpoints: JKS SHA-256 PASS, JKS permissions PASS, DefaultEngine.ini owner/privacy PASS, Android signing layout PASS; `KeyStorePassword` absent in INI. No build has started.
- Important: password was disclosed in chat earlier. Never replicate it in this repo, in command arguments, logs, screenshots, or documentation. Consider future credential rotation through Google Play upload-key reset only after evaluating impact; not required to proceed with this audit.
- Next: inspect Distribution/Shipping, package ID, store version, bundle flags, original/cooked TestMap and binary in M106 without printing secrets. Then plan secure temporary signing configuration with rollback before any build.

## M116 VM release-readiness presence checks — screenshot ~03:31 Qatar
- Latest owner-provided Cloud Shell screenshot from original `crownfall-m62-build` confirms four `M116_FILE=PASS` outputs for M106 sandbox `LastFrontier.uproject`, original `Content/Maps/TestMap.umap`, cooked `Saved/Cooked/Android_ASTC/LastFrontier/Content/Maps/TestMap.umap`, and `Binaries/Android/LastFrontier-Android-Shipping-arm64.so`.
- Confirms two `M116_DISTRIBUTION=PASS` outputs for `ForDistribution=True` and `BuildConfiguration=PPBC_Shipping` in `Config/DefaultGame.ini`.
- Confirms two `M116_ANDROID=PASS` outputs for `StoreVersion=218` and `bEnableBundle=True` in `Config/DefaultEngine.ini`, followed by `M116_READINESS_COMPLETE`.
- All **8/8 narrow existence/sub-string checks** passed. Prior screenshot shows `M116_STORE_PASSWORD=PASS` for original JKS and alias. This does not yet prove correct full Android section settings, bundleRelease packaging, APK/AAB signing, or Play eligibility.
- Remaining: `KeyStorePassword` is not yet configured in M106. Do not paste it into chat, GitHub, command arguments, or public shell history. Plan ephemeral signing credentials only in isolated M106 with secure backups, verify no leaking logs, then run one controlled Release build only when specifically authorized and ready. Preserve M63/M84 source and original JKS.
