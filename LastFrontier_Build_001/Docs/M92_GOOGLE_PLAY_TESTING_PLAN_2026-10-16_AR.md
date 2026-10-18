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


## M91 real VM signed AAB content audit PASS — screenshot 2026-10-16 23:53 local
- User reconnected to original Google Cloud VM `crownfall-m62-build` in correct project `project-f1aa4101-551b-4dbe-981` and `us-central1-a` (earlier typo included extra trailing 1 and was corrected). VM status RUNNING; SSH prompt confirmed.
- Executed read-only M91 against **new M84 QA AAB** `$HOME/crownfall/M84_EDITOR_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab`. Real terminal screenshot: `M91_BYTES=73612837`, `M91_ZIP=PASS`, `M91_SIGNATURE_EXIT=0`, `M91_AUDIT_COMPLETE`. Note `jarsigner -verify` without `-strict` returned 0; no claim Play Upload cert matches.
- `unzip -l` showed `base/assets/UECommandLine.txt` (54 bytes), `base/assets/vkqualitydata.vkq` (23,275 bytes), and importantly **`obbassets/assets/main.obb.png` (~38,994,330 bytes)**. This is consistent with Unreal Android asset-pack delivery including game content. Archive ZIP/sig valid; **real manifest targetSdk36, package/version218, bundletool validate, nested OBB game's pak/ucas and on-device gameplay remain unverified**. Older M77 41.9MB Debug AAB must not be uploaded.
- Signer public cert: `Owner: C=US, O=Android, CN=Android Debug`; SHA256 `6C:74:9E:D8:29:72:52:80:03:9C:F5:4C:E8:B2:9E:0B:05:B3:49:16:9B:36:55:AD:24:D7:D8:B0:C0:55:C9:E6`. Since certified upload key Play SHA256 `40:C0:...:A1:B8` differs, **do not upload as Internal Testing track/Production**.
- Google official Internal App Sharing docs https://support.google.com/googleplay/android-developer/answer/9844679?hl=en explicitly allow debug-signed AAB uploaded by authorized uploader, re-sign with Google's internal sharing key, max 100 downloads per link and expires after 60 days. Epic 5.8 docs https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine describe .obb inside install-time asset pack `obbassets`; no external OBB upload is required. Google does platform validation at upload; device asset delivery remains to be verified.
- Next practical step: exit SSH to Cloud Shell, copy `M84.../Binaries/Android/LastFrontier-Android-Shipping.aab` to Cloud Shell home with `gcloud compute scp crownfall-m62-build:/home/shami0112091997/crownfall/M84_EDITOR_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab ~/CROWNFALL_M90_QA_218.aab --zone=us-central1-a --project="$(gcloud projects list --format='value(projectId)' | head -n 1)"`; use `cloudshell download ~/CROWNFALL_M90_QA_218.aab` to phone (Google docs https://docs.cloud.google.com/shell/docs/using-cloudshell-command); user can upload from private phone file to Google Play Console Internal App Sharing upload page after signed-in. No public buckets/sharing; file still proprietary.
- **This transfer has NOT been executed on user's Cloud Shell and no Google upload or device test has yet occurred.** Continue from terminal after user's next screenshot. Do not recompile/cook/packaging for this test.


## M105 / M106 distribution rejection diagnosis (user screenshot 2026-10-18)
- Google Play Internal Testing rejected re-signed 218 AAB `CROWNFALL_M98_PLAY_UPLOAD_218.aab` because application was debuggable. M103 `bundletool dump manifest` explicitly showed `M103_DEBUGGABLE=true`, `M103_TEST_ONLY=ABSENT_DEFAULT_FALSE`.
- User VM screenshot M105: source M84 project and M90 QA packaging log exist, log lists `bundleDebug`, `bundleDebugResources`, `packageDebugBundle`, `processDebugManifest` and related Debug Gradle tasks. No Release task detected; this establishes the used QA packaging task was DEBUG even though Unreal .so Shipping. Both M105 manifest group counts 0 are inconclusive (audit path matching), not evidence release manifests were absent. Root cause is release/distribution packaging route; changing JAR signer alone cannot fix.
- New guarded script `Scripts/M106_Prepare_Distribution_Sandbox.sh` committed on `m66-smart-recovery` prepares a NEW directory `$HOME/crownfall/M106_RELEASE_SANDBOX_v218`, copies M84 while excluding `Intermediate/`, old `Saved/StagedBuilds/`, previous AAB/APKs and keystores. Updates ONLY copied `Config/DefaultGame.ini` to `ForDistribution=True`, `BuildConfiguration=PPBC_Shipping`, `IncludeDebugFiles=False`. Preserves cooked ASTC and Android Shipping .so, checks original map and config hashes, and refuses to overwrite destination. Tested locally with project fixture and duplicate-run rejection. **NOT yet executed on user's VM.** Does not run UAT, sign, or upload.
- Next steps: user transfers M106 shell script privately to VM, runs it, shows `M106_PREPARE_COMPLETE=PASS`; THEN separately inspect UE5.8 Distribution signing settings securely and consider proper UAT packaging using `-clientconfig=Shipping -distribution` with clean regenerated Android intermediates, preserving old outputs, and verify `bundleRelease` plus final `android:debuggable=false/absent` before user signs with ORIGINAL Google Play upload key. Do not use old M90 QA-only script for Play; do not modify version 217.
- References: https://dev.epicgames.com/documentation/en-us/unreal-engine/signing-android-projects-for-release-on-the-google-play-store-with-unreal-engine ; https://dev.epicgames.com/documentation/unreal-engine/project-section-of-the-unreal-engine-project-settings ; https://developer.android.com/studio/publish/preparing .


## M106 confirmed on original VM (user screenshot 2026-10-18 ~20:16 local)
- User executed direct Cloud Shell to original VM `crownfall-m62-build` and the M106 isolated Distribution preparation script successfully. Terminal showed: `M106_PREFLIGHT=PASS`, `M106_DISTRIBUTION_CONFIG=PASS`, `M106_MAP_INTEGRITY=PASS`, `M106_COOK_PRESERVED=PASS`, `M106_BUILD_NOT_STARTED=CONFIRMED`, and `M106_PREPARE_COMPLETE=PASS`.
- Expected new workspace: `$HOME/crownfall/M106_RELEASE_SANDBOX_v218`. Source M84 kept in place; old Gradle Intermediate excluded when copying. This only proves sandbox preparation, not Gradle Release packaging or Google Play acceptance. Do not re-run M106 over existing output; next M107 **read-only** audit of fresh sandbox ForDistribution/Shipping settings, UE UAT availability, Android overrides and keystore setup (metadata only, no secrets). Then plan a controlled true `-distribution` `Shipping` stage/package, verify manifest debuggable false/absent and `bundleRelease`, compare payload, sign with original Play upload key privately, and test device.


## M107 release preflight completed (user Cloud Shell screenshot)
- User screenshot confirms M107 read-only executed remotely on original `crownfall-m62-build` against `$HOME/crownfall/M106_RELEASE_SANDBOX_v218`: `M107_PROJECT=PASS`; `M107_RELEASE_CONFIG=PASS`; `M107_OLD_GRADLE=ABSENT`; `M107_GAME_CONTENT=PASS`; `M107_SHIPPING_BINARY=PASS`; `M107_UAT=PASS`; `M107_ANDROID_OVERRIDES=NONE` (limited grep for literal debuggable under Build/Android only); ~130G free disk; `M107_BUILD_NOT_STARTED=CONFIRMED`; `M107_AUDIT_COMPLETE`.
- IMPORTANT next gate M108: official UE5.8 Android Release signing docs require Distribution Signing Key Store, Key Alias and passwords; M106 explicitly excludes private *.jks/keystore from sandbox, and original upload JKS was on Google Cloud Shell instead of VM. Before starting -distribution UAT, perform redacted READ-ONLY audit of signing readiness: don't print passwords or put JKS in GitHub/command lines. We cannot infer UAT bundleRelease succeeds from M107. Prefer safe plan for signing the true release AAB in authorized private environment and verifying Google Play cert, avoiding a Debug AAB re-sign. Official docs https://dev.epicgames.com/documentation/en-us/unreal-engine/signing-android-projects-for-release-on-the-google-play-store-with-unreal-engine and https://developer.android.com/studio/publish/preparing .
