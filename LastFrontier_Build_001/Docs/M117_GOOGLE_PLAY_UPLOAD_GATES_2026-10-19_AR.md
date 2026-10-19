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

## نتيجة M117 الفعلية — محاذاة مكتبة Android الرئيسية
- صورة الطرفية بتاريخ 19 أكتوبر 2026، نحو 04:10 بتوقيت قطر من خادم `crownfall-m62-build`، داخل M106 sandbox، تعرض `M117_LOAD_SEGMENTS=4` و`M117_NATIVE_16KB=PASS` و`M117_NATIVE_CHECK_COMPLETE` لملف `Binaries/Android/LastFrontier-Android-Shipping-arm64.so`.
- الفحص استخدم `readelf -W -l` وتحقق أن محاذاة كل مقطع `LOAD` في **هذه المكتبة فقط** لا تقل عن 16384 بايت. لا يمثل فحص المكتبات الأصلية الأخرى داخل AAB، أو محاذاة ZIP للحزمة، ولا يثبت تثبيت اللعبة على جهاز ذي صفحات 16KB.
- صورة سابقة نحو 04:00 من الجلسة نفسها تؤكد `M117_FREE_GIB=129.1` و`M117_DISK=PASS` و`M117_GRADLE=CLEAN` و`M117_UAT=READY` و`M117_PREFLIGHT_COMPLETE`، وهذه بوابات موارد وأدوات فقط.
- صورة Play Console نحو 03:54 تُظهر جميع الإصدارات المسجلة 212 و214 و215 و216 و217، و218 غير موجود ضمن الخمسة في تلك اللحظة؛ يجب إعادة تأكيد الرقم إذا حدث نشر أو رفع لاحق.
- **المانع التالي الوحيد المثبت في M106**: `KeyStorePassword` غير موجود في `Config/DefaultEngine.ini` رغم نجاح مصادقة JKS في M116. العمل المقترح: إعداد Signing مؤقت ومحدود الصلاحيات في M106، إجراء إنتاج Gradle `bundleRelease` جديد، ثم التحقق من AndroidManifest والتوقيع وbundletool وجميع ملفات ELF/ZIP 16KB قبل الرفع.
- لا تشارك كلمة المرور في GitHub أو المحادثة أو السجلات، فهي ظهرت سابقًا في الدردشة ويجب مراجعة مخاطر انكشافها.
- مراجع Google الرسمية: https://developer.android.com/guide/practices/page-sizes ، https://developer.android.com/tools/bundletool

## M119 actual VM preflight — screenshot at 04:46 Qatar
- Cloud Shell upload produced a filename with suffix `-1.py`; user found it with `find`, verified SHA256, and privately copied it by `gcloud compute scp` to `$HOME/M119_Secure_Release_218_STAGE_20261019.py` on original `crownfall-m62-build`.
- On original VM, screenshot shows `M119_VM_FILE=PASS`, `M119_PYTHON_SYNTAX=PASS`, `M119_PREFLIGHT=PASS`, `M119_CONFIG_RESTORATION_SOURCE=M118_BACKUP_VERIFIED`, `M119_MODE=READ_ONLY`, `M119_BUILD_STARTED=NO`.
- This confirms **M119's own preflight passed on the VM** and M118 backup matches the current private config; no true Gradle bundleRelease, UAT run, AAB build or upload has yet occurred.
- M119 --build temporarily places the JKS store password in **isolated VM M106** Config/DefaultEngine.ini while UAT runs; normal exit/most signals restore the M118 backup. This is not robust to SIGKILL/power loss. Mobile Cloud Shell disconnects have been observed, so use a persistent tmux session if available, verify rollback after build, and treat private Intermediate/Android and logs as sensitive before sharing any artifacts.
- Next safe step: credential-free check for `tmux` on VM and review guarded build procedure before pressing ahead.

## M119 built AAB — verified from user's VM screenshot ~04:55 Qatar
- Screenshot from original VM `crownfall-m62-build` shows `M119_PREFLIGHT=PASS`, `M119_KEYSTORE_AUTHENTICATION=PASS`, `M119_TEMP_SIGNING_CONFIG=INSTALLED_PRIVATE`, `M119_UAT_START=YES`, `M119_CONFIG_RESTORED=PASS`.
- Terminal subsequently reports `M119_PRIVATE_LOG_PASSWORD_SCAN=NOT_PRESENT`, `M119_GRADLE_OUTPUTS=PRIVATE_INSPECTION_REQUIRED`, `M119_GRADLE_BUNDLE_RELEASE_TASK=SEEN`, `M119_GRADLE_BUNDLE_DEBUG_TASK=NOT_SEEN`, `M119_SUCCESS_MARKER=SEEN`, `M119_UAT_EXIT=0`, `M119_AAB_PLAINTEXT_SECRET_SCAN=PASS`, `M119_AAB_CREATED=YES_NEEDS_M118_AUDIT`.
- Thus a **new Android AAB was created by successful Shipping/Distribution packaging** with a release-task marker; this does NOT certify its embedded app ID, versionCode, target SDK, debuggable flag, upload certificate, assets or compatibility.
- Next: **M118 read-only AAB audit** of the unique file under `$HOME/crownfall/M106_RELEASE_SANDBOX_v218/Binaries/Android/*.aab`: check zip, bundle config, ARM64, payload, JAR signature + public upload-cert fingerprint, and bundletool manifest validation/16K where available. If bundletool or Android tooling is missing, pause and report `REVIEW` rather than treating it as PASS. Do not start a second build or reveal passwords.
- Before Google Play upload: ensure full bundle and app compliance checks. Version 218 absent from all five Play Console AAB records at ~03:54 local; re-confirm if needed. Internal testing only.

## M118 real VM AAB audit at 05:16 Qatar — signed upload cert matched
- User's screenshot from original VM after successful M119 Shipping/Distribution bundleRelease displays the first **read-only M118 AAB examination**, with exactly one `*.aab` matched under `$HOME/crownfall/M106_RELEASE_SANDBOX_v218/Binaries/Android`.
- `M118_AAB_BYTES=117411826`, `M118_ZIP=PASS`, `M118_STRUCTURE=PASS`, `M118_ARM64_LIBS=4`, `M118_GAME_ASSETS_BYTES=35648460`, `M118_SIGNATURE=PASS`, `M118_UPLOAD_CERT=PASS`, `M118_BUNDLETOOL=NEEDS_SETUP`, `M118_INITIAL_AUDIT_COMPLETE`.
- The signature matched the **public original Google Play upload certificate**, not the debug certificate; confirms AAB's package integrity under jarsigner and expected signer identity in this limited audit. Unlike previous Debug package this is a newly built candidate but **Play acceptance is not yet established**.
- Hard gate remains: bundletool `validate`; AndroidManifest package `com.crownfall.stronghold`, versionCode 218, targetSdk 36, `debuggable` and `testOnly` absent/false; bundle native libraries and ZIP alignment for 16KB; confirm policy metadata before internal testing upload.
- Because a `bundletool` executable was not found on PATH, next safest action is a **bounded read-only discovery** for an existing trusted bundletool JAR (Java is installed); do not download random scripts or modify SDK/Gradle without checking provenance. No new Build/Upload is required.
- Password was exposed previously in conversation. Do not put secrets in command arguments, reports, GitHub, logs, or screenshots. Manage upload-key rotation through official Google Play console after protected release workflow is stabilized.

## M118 Google bundletool manifest and 16KB config — screenshot ~05:25 Qatar
- User screenshot from verified `crownfall-m62-build` shows `M118_PACKAGE=PASS`, `M118_VERSION_218=PASS`, `M118_TARGET_API_36=PASS`, `M118_16KB_CONFIG=PASS`, and `M118_FINAL_CHECK_COMPLETE`.
- These checks used Google's trusted `bundletool-all-1.18.3.jar` on the newly built signed 218 AAB to inspect actual manifest package `com.crownfall.stronghold`, versionCode `218`, targetSdkVersion `36`, and bundle config's `PAGE_ALIGNMENT_16K`.
- **Crucial limitation:** screenshot does not visibly show `M118_NON_DEBUG` or `M118_NON_TEST_ONLY`, although earlier supplied command intended to check them; do not mark these checks PASS without terminal evidence. Also, `PAGE_ALIGNMENT_16K` is bundle packaging configuration, NOT a proof that all four in-bundle arm64-v8a ELF program segments are 16 KB aligned.
- Next read-only gate: explicitly verify `application/@android:debuggable` and `@android:testOnly` in manifest and perform per-ELF `PT_LOAD` `p_align >= 16384` and offset/vaddr congruence for all `base/lib/arm64-v8a/*.so`; then Play Console internal testing upload with device verification if all pass. Avoid rebuild or secret exposure.

## M118 definitive non-debug / non-test-only flags — VM screenshot 05:30
- Owner screenshot shows direct `bundletool dump manifest --xpath` flags checks after fresh M119 AAB validation: `M118_debuggable=PASS` and `M118_testOnly=PASS` in VM terminal at 19 Oct 2026 ~05:30 Qatar.
- The script checked both properties absent/empty/false; these results remove the prior **unverified manifest flag** blocker from M118. The earlier `M118_PACKAGE=PASS`, `M118_VERSION_218=PASS`, `M118_TARGET_API_36=PASS` and `M118_16KB_CONFIG=PASS` still stand.
- Remaining technical gate: inspect **all four packaged arm64-v8a .so ELF PT_LOAD segments** for 16KB p_align and file-offset / virtual-address congruence, distinct from the previously checked only main Unreal .so and bundle `PAGE_ALIGNMENT_16K` metadata. No need to rebuild merely to run this read-only audit.
- After a PASS, transfer privately and upload signed versionCode 218 AAB to **Internal testing only**, review Play Console's generated bundle inspection and testing results, and confirm there are no new app policy declarations or version changes.

## M118 four packaged ARM64 libraries verified 16KB — 05:37 Qatar
- Owner-provided Cloud Shell screenshot on `crownfall-m62-build` 19 October 2026 ~05:37 local documents `M118_LIBRARIES=4`, `M118_LIBRARY_1=PASS`, `M118_LIBRARY_2=PASS`, `M118_LIBRARY_3=PASS`, `M118_LIBRARY_4=PASS`, `M118_ALL_ARM64_16KB=PASS`.
- Read-only Python inspection opened the verified new `LastFrontier-Android-Shipping.aab` and checked four packaged `*/lib/arm64-v8a/*.so` ELF64 little-endian AArch64 libraries, requiring all PT_LOAD alignments >= 16KB, power-of-two alignment and congruent offsets and virtual addresses.
- Also established before this screenshot: `bundletool validate=PASS`, manifest actual package `com.crownfall.stronghold`, versionCode=218, targetSdkVersion=36, debuggable/testOnly absent/false, page alignment metadata PAGE_ALIGNMENT_16K. Original upload key certificate matched. The signed `*.aab` size is 117,411,826 bytes. No further build required on the evidence so far.
- Next: privately copy **exact existing signed AAB** from VM into Google Cloud Shell (via `gcloud compute scp`), validate copied byte count and SHA-256 against source, then download locally over authenticated Cloud Shell and upload to **Play Console Internal Testing only**, review warnings and resolve app content/declarations if requested. Do NOT publicly share binary or credentials.
- Passing these technical checks does not guarantee Play Console will accept the upload or confirm runtime compatibility. Device testing and Play review remain open.
- Official transfer docs: https://docs.cloud.google.com/sdk/gcloud/reference/compute/scp ; https://docs.cloud.google.com/shell/docs/using-cloudshell-command

## M120 signed AAB transfer to Cloud Shell — 05:46 Qatar
- New owner screenshot shows Google Cloud Shell transfer from original VM `crownfall-m62-build` over `gcloud compute scp` to private Cloud Shell path `$HOME/CROWNFALL_218_Release_Signed.aab`, via Google Cloud project `project-f1aa4101-551b-4dbe-981`, zone `us-central1-a`.
- Transfer progress reached `100%`, and shell explicitly reported `M120_TRANSFER=PASS` and `M120_SIZE=PASS`; source M119 signed AAB expected exact size `117411826` bytes.
- These checks verify successful transfer and byte count, **not content byte-for-byte identity**; compare SHA-256 of the copied AAB and VM source before download/upload.
- Once SHA-256 matches, use private `cloudshell download` to download the copy to owner's authenticated Android device and upload only to Google Play **Internal testing**. Preserve VM source, Cloud Shell copy, and all signing backups. Do not use public storage or trigger additional Build.
- Previous M118 results remain: signed/upload cert PASS, bundletool validate PASS, package com.crownfall.stronghold, versionCode 218, targetSdkVersion 36, non-debug/non-test-only PASS, 16KB bundle alignment and all 4 ARM64 ELF libs PASS. Play Console will still independently validate upload and app policy requirements.

## M120 private Cloud Shell transfer SHA256 PASS — 05:48 Qatar
- Owner screenshot after complete private `gcloud compute scp` shows `M120_SHA256=PASS` from Google Cloud Shell: computed SHA-256 on `$HOME/CROWNFALL_218_Release_Signed.aab` and compared against `sha256sum` executed by `gcloud compute ssh` on original `crownfall-m62-build` at `$HOME/crownfall/M106_RELEASE_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab`.
- Thus uploaded-to-Cloud-Shell candidate AAB **matches the original release AAB byte-for-byte**, on top of verified 117411826-byte length; no second build is needed.
- Next step: use official `cloudshell download "$HOME/CROWNFALL_218_Release_Signed.aab"` from Cloud Shell (not remote VM) to private owner's Android downloads, confirm the file is complete; in Google Play Console choose CROWNFALL → Internal testing → Create new release, select exact signed versionCode 218 AAB, review policy warnings and draft before releasing to invited testers. Do not upload publicly or change production.
- This is a complete *transport* gate, not Google Play acceptance; Play upload has **not** occurred in evidence received at this checkpoint.
- Official docs: https://docs.cloud.google.com/shell/docs/using-cloudshell-command ; https://support.google.com/googleplay/android-developer/answer/9859348 .
