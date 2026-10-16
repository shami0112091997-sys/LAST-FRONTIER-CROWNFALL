# CROWNFALL — M69 Android First / AAA target — 2026-10-16

## القرار الملزم لمسار التطوير
المستخدم اعتمد Android أولاً للعبة LAST FRONTIER: CROWNFALL، مع جودة AAA كهدف بصري طويل المدى وليس وصفاً للحالة الحالية. الأولوية: نسخة Unreal حقيقية تعمل بثبات على هاتف Android، ثم توسيع المحتوى البصري والتفاعلي بصورة قابلة للقياس، وبعد ذلك Play Console. لا تُعد لعبة جاهزة لمجرد نجاح preflight أو وصول ملفات إلى GitHub.

## مرجع المشروع الآمن
- المستودع الخاص: shami0112091997-sys/LAST-FRONTIER-CROWNFALL
- الفرع الآمن: m66-smart-recovery (لا تعديل تلقائي لـ main)
- خادم البناء/الأصول الأحدث: crownfall-m62-build
- Unreal الحالي على VM: $HOME/UE_5.8.3
- نسخة المحتوى الأحدث على VM: $HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001
- الحفاظ على TestMap.umap وأصول uasset الأصلية قبل التعديل. الاختبار على نسخة معزولة + SHA256 ثم اختبار إعادة الفتح.
- منع مشاركة ملف التوقيع JKS أو أسراره وGitHub tokens وGoogle credentials، وإبقاء نتائج ADB الخام على جهاز الاختبار، خارج المستودع.
- لا استخدام مفرط أو متكرر لموارد GitHub Actions، ولا توفير موارد Google Cloud مدفوعة أو توسيع VM دون موافقة صريحة.

## الحالة المثبتة مقابل المخطط
- M60: نجح تجميع Editor، لكن Cook فشل في Actions run 37645589203. السجل تضمن Serialization error في TestMap.umap (FName index 64 خارج [0,44))، ثم Editor exit 139 وUAT exit 25. هذا خاص بتلك الخريطة/التجربة وليس حكماً آلياً على خريطة VM M63.
- M63: توجد نتائج سابقة لتحميل خرائط واختبارات أصول على VM، لكن AAB Shipping نهائي صالح للنشر غير مثبت.
- StreetLamp01: 30,610 مثلثاً في LOD0 وSetLods=-1 ثم rollback PASS. لا تعديل للـLOD قبل معرفة السبب الحقيقي.
- Assets M63 audit: 11 StaticMesh, 6 Textures. ليست جودة AAA مكتملة.
- Github M60: كود LFWorldDirector ينشئ 18 PointLights (9 على طول المسار × جانبين). يجب فحص تكلفتها على الجهاز قبل اختيار بدائل (إضاءة ثابتة/تقليل المدى/ظلال غير متحركة/خفض عدد الأضواء).
- الرسومات الحالية تعتمد جزئياً على Engine BasicShapes. المواد والشخصيات الفيكتورية والأنيميشن/الأصوات والمؤثرات الأصلية غير مكتملة.
- الإصدار في إعدادات GitHub هو StoreVersion 215، بينما سجل M66 يرجع إلى إصدار سابق على Play برقم 217. يجب فحص أعلى versionCode في Console.
- Data Safety المدرج لنسخة WebView 2.1.2 لا يمكن نسخه تلقائياً إلى Unreal. يجب فحص manifest وSDKs والبيانات الفعلية.
- ملف M68 الآمن موجود لكنه لم يُنفذ على VM في هذه الجلسة. لا تدّعِ نجاحه دون سجل.

## أهداف الأداء المقترحة (ليست نتائج)
| فئة الجهاز | الهدف | قياس القبول المقترح |
| منخفض | 30 FPS مع جودة مرنة | 15 دقيقة لعب؛ p95 frame time <= 40 ms، لا crash؛ خفض التفاصيل عند الحاجة |
| متوسط | 30 FPS مستقرة | 15 دقيقة؛ p95 frame time <= 40 ms؛ لا تقطيع مستمر |
| مرتفع | 60 FPS اختياري إن أمكن | 15 دقيقة؛ p95 frame time <= 22 ms؛ الرجوع إلى 30 FPS عندما تتطلب الحرارة |
هذه أهداف أولية قابلة للتعديل بعد تجربة حقيقية على أجهزة مختلفة. لا تثبت أرقام FPS بقراءة dumpsys gfxinfo وحدها لأن Unreal قد يعرض بإطار Native Vulkan؛ اعتمد Unreal Insights وAndroid GPU Inspector والتتبعات الفعلية. سجّل درجة الحرارة/thermal throttling والذاكرة والإطارات، ولا تقارن نتائج جلسة قصيرة بمتطلبات لعب ممتد.

## خطة تطوير متدرجة
### المرحلة A — إصلاح بوابات M68 (شرط مسبق)
1. تشغيل Scripts/M68_Release_Preflight_ReadOnly.sh على VM وقراءة التقرير.
2. تشغيل تشخيص StreetLamp M67 وتحديد مسبب -1، دون إعادة المحاولة العمياء.
3. اختبار تحميل M63 TestMap بواسطة UnrealEditor-Cmd على نسخة Stage؛ رفض Serialization errors فوراً.
4. تأكيد Android toolchain ودعم targetSdk 36 عملياً في المحرك قبل البناء.
5. فحص رقم أعلى versionCode ومفتاح التوقيع في Play Console دون كشف الأسرار.

### المرحلة B — Android playable vertical slice
- قلعة فيكتورية صغيرة متماسكة: دخول/خروج/بناء غطاء، ممرات وإضاءة، ميكانيك حركة وتصويب واشتباك وأعداء.
- واجهة لمس مناسبة لهواتف مختلفة، منظور ثالث، حساسية الكاميرا، منطقة Fire واضحة، إيقاف مؤقت وإعدادات جودة، واجهة عربية/إنجليزية بعد الاختبار.
- تسجيل لمس الشاشة والتصادم والشخصيات وعدم تداخل الأزرار مع عصا الحركة.
- مواد وملفات صوت وأصول 3D أصلية أو مرخّصة بوضوح. لا أصول مزيفة لتكبير حجم AAB.
- القياس على الأجهزة قبل زيادة المؤثرات ورفع عدد الأعداء.

### المرحلة C — تحسينات قابلية التوسع
- ملفات جودة Android_Low/Mid/High مرشحة في Docs/M69_AndroidQualityProfiles_CANDIDATE.ini، غير مفعلة في Config؛ اعتمدها بعد إثبات اختيار DeviceProfile وتوافقها مع تعريفات UE المحلية.
- تقليل كلفة PointLights، اختصار مواد عالية التعقيد، instancing، texture compression ASTC، mesh LOD اختبارياً فقط بعد حل StreetLamp، وقياس GPU.
- توازن GPU/CPU/Memory، تجهيز PSO لتقليل التقطيع على الأجهزة المدعومة.
- جودة ممتازة لا تعني تفعيل كل مؤثرات PC على الهاتف.

### المرحلة D — إطلاق Android
- Build/Cook/Package حقيقي UE Shipping على مشروع staging؛ signed AAB مع ملف SHA256، واصدار أعلى من أعلى نسخة Console.
- تحقق bundletool من package, versionCode, target SDK, arm64, permissions; تحقق دعم صفحات 16KB لتطبيقات 64-bit، وشهادة upload والتوافق.
- اختبار من Google Play internal/closed حسب حساب المطور؛ 15 دقيقة لعب متصلة على ثلاثة مستويات قدر الإمكان، وعدم انهيار وإعدادات حرارية آمنة.
- سياسة خصوصية HTTPS واضحة ووسيلة تواصل معتمدة، بيانات Data safety تطابق التطبيق الحقيقي، تصنيف عمري/أصول المتجر/متطلبات الحساب.
- لا رفع للإنتاج قبل تحقق الأدلة وموافقة صاحب اللعبة.

## أدوات M69 التي أضيفت
1. Scripts/M69_Android_Device_Evidence_ReadOnly.sh: أدوات adb على كمبيوتر متصل بهاتف اختبار به اللعبة مثبتة وتعمل بالفعل، تجمع معلومات ذاكرة/حرارة/إطارات داعمة لمدة 15 دقيقة افتراضياً. لا تبدأ اللعبة ولا تنصبها ولا تغير الجهاز ولا ترفع السجلات؛ لا تثبت FPS النهائي.
2. Docs/M69_AndroidQualityProfiles_CANDIDATE.ini: ملفات جودة مرشحة للبحث وليست مفعلة؛ لا تنسخها إلى Config مباشرة.

## المراجع الرسمية
- Google Play API 36: https://support.google.com/googleplay/android-developer/answer/11926878
- Unreal Engine 5.8 Android profiles: https://dev.epicgames.com/documentation/en-us/unreal-engine/customizing-device-profiles-and-scalability-in-unreal-engine-projects-for-android
- Epic Android profiling: https://dev.epicgames.com/documentation/unreal-engine/how-to-use-unreal-insights-to-profile-android-games-for-unreal-engine
- Google Android ADPF thermal: https://developer.android.com/games/optimize/adpf/best-practices-adpf
- Android 16KB pages: https://developer.android.com/guide/practices/page-sizes
- GitHub Actions legitimate project use: https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features

## أول إجراء تنفيذي تالٍ
اجمع نتيجة M68 read-only من VM الحالية، ثم تحقق من تحميل الخريطة في Unreal، وأصلح خطأ Cook إن ظهر. لا تبدأ build ثقيل أو تخصّص موازنة رسومات نهائية أو ترفع AAB قبل ذلك.


## تحديث سلامة سكربت M68 بعد التدقيق
- تم تعديل Scripts/M68_Staged_Android_Build.sh على الفرع الآمن فقط كي يتم تجميع LastFrontierEditor للنسخة المعزولة قبل محاولة تحميل خريطتها، لأن ملفات Binaries الأصلية ليست ضمن النسخ.
- يرفض السكربت إجراء البناء المكلف مبكراً إذا كان PythonScriptPlugin غير مفعل في مشروع وضع فيه DisableEnginePluginsByDefault=true؛ عندها ننتقل إلى اختبار الخريطة بمسار C++ Editor-only commandlet الموثّق من M63، أو نراجع خيار تمكين المكون على النسخة التجريبية فقط.
- تم تعديل فحص تحميل الخريطة ليستخدم LevelEditorSubsystem.load_level وفق مثال وثائق Epic للـ Unreal 5.8، مع منع قبول وجود الخريطة على القرص دون تحقق حقيقي.
- أضيفت مراجعة SHA256 للخريطة الأصلية بعد اكتمال البناء؛ لا يجوز بناء أو رفع المنتج قبل رؤية سجل 실행 فعلي يؤكد نجاح Compile / Map load / Cook / AAB / device.
- أداة M69 لجمع أدلة الهاتف جرى فحص صياغتها بـ bash -n واختبار رفض الجهاز بدون تطبيق مثبت باستخدام mock adb محلي؛ **لم يُنفّذ اختبار هاتف حقيقي** بعد.


## آخر تشخيص للاتصال بالخادم (صورة Cloud Shell)
- ظهر موجه الأوامر باسم المستخدم على crownfall-m62-build؛ كان المستخدم متصلاً بالخادم الحقيقي بالفعل.
- أمر gh api فشل بسبب gh: command not found. لا توجد ضرورة لتثبيت gh لتنفيذ فحص محلي. محاولة حفظ الأمر عبر > /tmp/m68-audit.sh قد تنتج ملفاً فارغاً إذا فشل gh؛ لا تعتمد عليه.
- أمر gcloud compute ssh الذي أُطلق من داخل نفس VM أعاد no active account selected. لا حاجة للقيام بـ gcloud auth login داخل VM لهذا الغرض، ولا حاجة للاتصال بالخادم مرة أخرى.
- أفضل خطوة تالية: فحص محلي للقرص والملفات وإعدادات Unreal بخط أمر قراءة فقط. تجنب تنزيل أدوات أو منح رموز اعتماد جديدة قبل إثبات الحاجة.
- هذه الأخطاء تتعلق بالبيئة والأوامر، ولا تثبت فشل جديد للعبة أو تلف خريطة M63.


## تحقق VM الجديد من صورة المستخدم (16 أكتوبر 2026 حوالي 08:18 محليًا)
فحص محلي يعتمد على أوامر shell للقراءة فقط، وقد ظهر ما يلي في الصورة:
- المسار الحقيقي للمشروع: /home/shami0112091997/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001/LastFrontier.uproject -> PASS لوجود ملف غير فارغ.
- خريطة /Content/Maps/TestMap.umap -> PASS لوجود ملف غير فارغ فقط، **ليس اختبار تحميل/سلامة serialization**.
- /home/shami0112091997/UE_5.8.3/Engine/Binaries/Linux/UnrealEditor-Cmd -> PASS لوجود ملف غير فارغ فقط، **ليس تجميعًا جديدًا**.
- Live DefaultEngine.ini: PackageName=com.crownfall.stronghold, StoreVersion=216, TargetSDKVersion=36, bBuildForArm64=True.
- القرص /dev/root بحجم 243G، مستخدم 109G، متاح 134G، استخدام 45%.
- يظهر تعارض إصدار: live StoreVersion=216، وسجل M66 يذكر نسخة Play 217؛ لا ترفع AAB برقم 216، ولا تخمّن أعلى رقم، تحقق عبر Play Console، ثم استخدم رقمًا أعلى داخل نسخة staged فقط.
- النتيجة: VM preliminary structural preflight PASS؛ compile, real map load, Cook, Android signed AAB, on-device performance ما زالت NOT VERIFIED. سعة القرص وحدها لا تضمن النجاح، يلزم فحص RAM وAndroid SDK/NDK وأدلة تحميل الخريطة.
- المرحلة القادمة الآمنة هي التعرف على آلية M63 editor-only commandlet وتشخيص PythonScriptPlugin وملفات البناء الموجودة، دون تعديل الأصول أو تشغيل Cook.


## فحص المستخدم التالي (صورة Cloud Shell، 16 أكتوبر 2026 08:20)
- بعد مراجعة screenshot ظهر وجود الملفات الفعلية:
  - Source/LastFrontierEditor/Public/CrownfallAtomicMapCommandlet.h
  - Source/LastFrontierEditor/Private/CrownfallAtomicMapCommandlet.cpp
- .uproject يعلن DisableEnginePluginsByDefault=true ولكن PythonScriptPlugin وEditorScriptingUtilities مفعّلان صراحةً للـEditor. AndroidPermission وGooglePAD مفعّلان، وGoogleARCore وOnlineSubsystem غير مفعّلين. هذا يحل الغموض حول PythonScriptPlugin: ليس محظورًا بالضرورة بسبب سياسة تعطيل المكونات الافتراضية.
- free -h: RAM total 31GiB، used 389MiB، free 26GiB، available ~30GiB؛ swap total 15GiB، used 3.0MiB. هذه **قراءة الموارد** لا تثبت نجاح Unreal عند التشغيل.
- SHA256 لخريطة M63 TestMap.umap: 591855a572cb07a8fd6775f546b6ff818e706b9b62d09050f0533268b2edfad7 (يجب إعادة المقارنة إن ظهر تعارض كتابة).
- الاستنتاج: commandlet المصدر موجود، المكونات التحريرية مفعلة والموارد جيدة مبدئياً؛ **اختبار تحميل الخريطة الحالي ما زال غير منفذ**. الخطوة التالية قراءة C++ commandlet لمعرفة بارامتر load-only والتأكد من عدم تنفيذ save/atomic mutation قبل تشغيله.


## فحص لقطة 16 أكتوبر 2026 08:23 (سجل M63 السابق)
- من سجل M63_CPP_LOAD_ONLY_RUN.log المؤرخ 2026-10-14: CROWNFALL_CPP_LOAD_ONLY_STARTED=PASS, LOAD_PACKAGE=PASS, PACKAGE_NAME=/Game/Maps/TestMap, PACKAGE_CONTAINS_MAP=TRUE, FIND_WORLD_IN_PACKAGE=PASS, WORLD_NAME=TestMap, CROWNFALL_CPP_LOAD_ONLY=PASS. سجل تاريخي ناجح **لا يثبت إعادة الاختبار اليوم أو نجاح Cook أو Android**.
- في المصدر الحي Source/LastFrontierEditor/Private/CrownfallAtomicMapCommandlet.cpp ظهرت UEditorLoadingAndSavingUtils::SaveMap(World, Dst) في السطر 87؛ هذا commandlet **يكتب خرائط ولا يصلح كأداة قراءة فقط**. لا تشغّله على مشروع VM الأصلي. يجب فحص اسم destination والسلوك الفعلي، واستخدام نسخة معزولة فقط.
- أبلغ المستخدم استمرار ظهور تحذيرات ACL مع الاختبارات السابقة. لم تظهر هنا قرينة تربطها بفشل التحميل.
- الخطوة التالية: فحص أدلة CLI السابقة أو إنشاء probe مستقل آمن ثم اختبار على staged copy، مع نسخ احتياطي وSHA256.


## Android toolchain screenshot checkpoint 2026-10-16 08:26
- Server: crownfall-m62-build (user already connected in SSH shell).
- Screenshot checked read-only: ANDROID_HOME and ANDROID_SDK_ROOT=/home/shami0112091997/Android/Sdk; NDKROOT=/home/shami0112091997/Android/Sdk/ndk/27.2.12479018; JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64.
- Java shows OpenJDK 21.0.12.1, 64-bit. Installed SDK platforms: android-35 and android-36. Installed NDK: 27.2.12479018 (r27c). UE_5.8.3/Engine/Platforms/Android directory FOUND.
- Epic UE5.8 Android docs recommend NDK r27c, Build Tools 35.0.1, JDK 21 and SDK 35. Google Play new apps/updates require API 36 from Aug 31 2026. Presence of SDK 36 is not proof UE's Android Gradle build supports target 36: next validate actual installed Build Tools 35.0.1, local SDK metadata, then Turnkey VerifySdk and staged package, without installing or changing anything blindly.
- Live project config previously reported StoreVersion=216, history references Play code 217. Version for next release remains blocked until highest Play Console code confirmed.
- Real map load-only M63 PASS is historical. Still no verified Shipping AAB or on-device measured FPS.
- No automatic resource provisioning, cloud sign-in, app upload, or source mutation in this checkpoint.


## Screenshot 2026-10-16 08:29 — Android build tools complete
- This is an observed screenshot of a local read-only VM shell test, not a UAT/Turnkey or Cook pass.
- Android SDK build tools include 35.0.1; required 35.0.1/aapt2 and zipalign: PASS.
- SDK platforms/android-36/android.jar: PASS.
- NDKROOT/source.properties: PASS; Pkg.Revision = 27.2.12479018 (r27c).
- JAVA_HOME/bin/javac: PASS; earlier Java 21 was confirmed.
- UE 5.8 official requirements: NDK r27c, Build Tools 35.0.1, JDK21, recommended target SDK35. Google Play after Aug 31 2026 requires target SDK36 for new/updated regular Android apps: actual packaging support must be validated; do not claim UE5.8 supports API36 from installed sdk files alone.
- NEXT GATE: UE Turnkey -command=VerifySdk -Platform=Android (not InstallSdk, not ExecuteBuild) from already-present RunUAT.sh; capture output/exit code. VerifySdk is specified by official Epic CLI docs to inspect local SDK version compatibility, without invoking packaging. Engine AutomationTool may update its own temporary build artifacts or logs, but do not modify the game source.
- Keep project originals unchanged, do not publish or use current 216 as final version; Play Console earlier 217 remains historical until checked.


## Unreal Android Turnkey SDK verification — 2026-10-16 08:31
- Authenticated session on VM crownfall-m62-build executed existing Engine/Build/BatchFiles/RunUAT.sh Turnkey -command=VerifySdk -platform=Android -unattended -utf8output, timeout 300; log path $HOME/crownfall/M69_TURNKEY_VERIFY_ANDROID.log.
- Screenshot confirms VERIFY_EXIT=0 and AutomationTool exiting with ExitCode=0 (Success).
- Android installed SDK validity: Status=Valid, MinAllowed_Sdk=r27c, MaxAllowed_Sdk=r29, Current_Sdk=r27c, Allowed_AutoSdk=r27c; flags InstalledSdk_ValidVersionExists, Support_FullSdk, Sdk_HasBestVersion.
- Verified underlying SDK: platforms android-35 and android-36; build-tools 35.0.1; NDK 27.2.12479018 (r27c); Java 21.
- Valid Turnkey SDK does NOT prove targetSdkVersion 36 package compatibility, Unreal editor map load in the current source, successful Cook, signed AAB, device 16KB memory page or Play Console acceptance.
- Follow-up should be a low-cost read-only content/commandlet audit, followed by isolated staging, then a single controlled real build only after independent map and package version checks. Do not re-run costly GitHub runners or install extra SDK.


## M70 compilation observed pending — screenshot 2026-10-16 08:38
- M70 staged snapshot exists at /home/shami0112091997/crownfall/M70_ANDROID_STAGE_20261016T053500Z; source M63 is separate.
- Shell output confirms M70_STAGE_COPY=PASS from earlier and now M70_PREFLIGHT=PASS; this preflight requires staged LastFrontier.uproject and TestMap.umap non-empty, binary equality to original TestMap, and no symlink in staged Content.
- Build command started as: UE_5.8.3/Engine/Build/BatchFiles/Linux/Build.sh LastFrontierEditor Linux Development <staged>/LastFrontier.uproject -NoHotReloadFromIDE -Progress, wrapped in timeout 1800 with output redirected to $HOME/crownfall/M70_EDITOR_COMPILE.log.
- Latest screenshot has a waiting cursor and **does not show M70_COMPILE_EXIT or M70_MAP_UNCHANGED**. Therefore compile success or failure NOT VERIFIED. Do not re-run builds or start Cook; wait for terminal completion, then interpret actual return code and preserved map diff.
- Compile is real work on the existing VM, not a detached background automation. Source project original should remain untouched; until finished, no new command in same shell.


## M70 real Editor compile PASS — screenshot 2026-10-16 08:40
- Confirmed actual VM shell output from screenshot: M70_PREFLIGHT=PASS; M70_COMPILE_EXIT=0; Result: Succeeded; M70_MAP_UNCHANGED=PASS.
- Compile ran on isolated stage: $HOME/crownfall/M70_ANDROID_STAGE_20261016T053500Z; original is $HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001.
- Exact compile report: $HOME/crownfall/M70_EDITOR_COMPILE.log. Compile verifies LastFrontierEditor on Linux with UE5.8.3; no new Android Cook/Package or AAB tested.
- Next gate: controlled UE Python commandlet load-only /Game/Maps/TestMap on M70 stage with sha256 checks of original and staged TestMap before/after. PythonScriptPlugin and EditorScriptingUtilities were confirmed enabled on VM; LevelEditorSubsystem.load_level returns bool per official UE5.8 docs. No SaveMap, no original M63 editor tools.
- Only after map load passes and version/signing decisions resolved should run a single Shipping Android build. No false claim of production readiness.


## منهج التدقيق الإلزامي لجميع الإجراءات — توجيه المستخدم 2026-10-16
المستخدم يطلب: أعلى قدر متاح من البحث والعمق والدقة والتحقق من المصادر، وعدم التسرع أو تكرار الأخطاء، وتطبيق هذا المبدأ على **كل خطوة مستقبلية** في مشروع CROWNFALL.

### بوابات إلزامية قبل/أثناء/بعد أي تنفيذ
1. **قبل التنفيذ — جمع الحقائق:** ارجع أولًا إلى أحدث سجلات VM وGitHub والمخرجات الفعلية والصور، وميّز الأدلة المثبتة عن الفرضيات أو نتائج اختبارات قديمة. حدِّد البيئة والمسار والإصدار والتبعيات والهدف الدقيق.
2. **التحقق من المصادر:** ارجع إلى الوثائق الرسمية ذات الصلة (Epic Unreal Engine 5.8.3، Android SDK/NDK، Google Play، GitHub وGoogle Cloud) وتحقق من صلاحية نسختها وتوافقها مع المطلوب. لا تعتمد على توجيهات أو حلول غير موثقة عندما تكون المصادر الأصلية متاحة.
3. **مراجعة الأمر بالكامل:** افحص الصياغة والأقواس والاقتباسات والمسارات ومتغيرات البيئة وحقوق الوصول؛ لا تُصدر أمرًا للنسخ من الهاتف إلا بعد التأكد من أنه مناسب للـShell المقصود ولا يحوي نصوصًا غير قابلة للنسخ، وأنه لا يكتب فوق البيانات دون داعٍ.
4. **الحماية أولًا:** العمل بنسخة stage منفصلة من M63؛ النسخ الاحتياطية ومقارنة SHA256 قبل وبعد؛ لا تغييرات في TestMap.umap أو .uasset الأصلية، ولا كشف JKS أو كلمات المرور أو الرموز الخاصة، ولا ترخيص/مشتريات أو تغيير إعدادات حسابات الإنتاج دون إذن.
5. **اختبارات مرحلية قابلة للتحقق:** Prefight -> Compile -> load-map -> Cook -> Package -> signed AAB -> bundletool/16KB/API36/permissions/certificate -> real Android device thermal/FPS/crash tests -> Play Console checks. لا تُحسب الخطوة PASS بلا سجل تنفيذ أو نتيجة واضحة.
6. **أدنى استخدام للموارد:** استخدم اختبارات القراءة فقط أولًا، ولا تُكرر CI مكلفًا أو تبدأ خوادم أو توسع موارد GCP دون حاجة وإذن؛ احترم شروط الاستخدام والحدود الرسمية للمنصات.
7. **عند ظهور خطأ:** أوقف الخطوات التابعة فورًا، احفظ السجل، حدد السبب الجذري، استرجع الحالة الأصلية عند الحاجة، ثم اختبر الإصلاح في بيئة مستقلة، ولا تكرر أمرًا فاشلًا بشكل أعمى.
8. **شفافية كاملة:** وضح ما نُفذ حقيقة وما بقي مجرد خطة، ولا تدّعِ وصول AAA أو وجود AAB نهائي أو نشر Google Play دون برهان. لا توجد طريقة لضمان صفر أخطاء، لكن يُلزم تطبيق وسائل المنع والتحقق أعلاه.
9. **استمرارية:** سجّل النقطة التالية ونتيجة كل اختبار في هذا الملف/السجلات، حتى لا يبدأ العمل من الصفر في الجلسة التالية.

### الحالة عند اعتماد المعيار
آخر نتيجة موثقة بالصورة: M70_COMPILE_EXIT=0, Result Succeeded, M70_MAP_UNCHANGED=PASS. اختبار تحميل TestMap الأحدث عبر Python لم يُثبت نجاحه؛ الصورة 08:44 أظهرت أن الأمر لم يبدأ بسبب مشكلة نسخ ([cmd]: command not found). **الخطوة التالية هي تشخيص/إصلاح هذا الإشكال في تنفيذ الأمر مع مراجعة Shell قبل تشغيل اختبار الخريطة على M70، دون تجاوز بوابة الاختبار.**


## M70 verified safe inline Python commandlet gate — 2026-10-16
- User said "افعل" to continue from M70 staged compile PASS and unexecuted map-load test due to terminal pasting issue. No SSH command execution access is currently connected, so the next VM command still must be executed in user's existing Cloud Shell terminal.
- Verified against **Epic UE 5.8** documentation for PythonScriptPlugin: UnrealEditor-Cmd with -run=pythonscript and -script=<inline Python code> is officially supported; LevelEditorSubsystem.load_level("/Game/Maps/TestMap") returns bool and closes previous level without saving.
- A standalone local Bash gate (M70_Stage_Map_Load_Gate.sh) was prepared and validated with bash -n, Python compile, and three mock runs: normal PASS, serialization-error REJECT, altered-staged-map REJECT. **Mock tests are not execution of Unreal**. Logs are saved outside project.
- The script resolves authoritative M63 and staging M70 paths, requires matching map SHA256 before launching the staged project's UnrealEditor-Cmd, sets a 600-second timeout, checks an explicit print marker and all critical error patterns, then checks the original and staged map SHA256 against pre-run snapshots. It never invokes SaveMap, Cook, BuildCookRun, or Google Play publish.
- Source original: $HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001. Staged: $HOME/crownfall/M70_ANDROID_STAGE_20261016T053500Z. Unreal: $HOME/UE_5.8.3.
- **No new M70 map load PASS yet.** Do not proceed to Android Shipping until the user reports the script's actual M70_LOAD_EXIT and M70_MAP_INTEGRITY, or equivalent directly verified engine log.

## M70 map-load commandlet outcome — 2026-10-16 08:56
- Actual VM screenshot shows M70_LOAD_EXIT=255; M70_MAP_INTEGRITY=PASS; M70_LOAD_TEST=FAIL.
- Real Unreal Python log says AttributeError: module 'unreal' has no attribute 'get_editor_subsystem', when called from headless -run=pythonscript; the Python script exception caused Unreal commandlet exit -1/255. This is a missing API in the current commandlet environment, **not evidence of corrupt map**. No current source file damage is visible; explicit map integrity matched.
- Epic UE5.8 documentation cautions that headless Python commandlet is tricky for level-loading. 5.8 Python API lists unreal.load_package(name) and unreal.find_object(outer,name,type). Use those to inspect UPackage / UWorld in M70 stage instead of trying get_editor_subsystem again. Code is syntactically checked locally (Bash -n, Python compile), but Unreal run is still PENDING. No SaveMap, no mutations or Cook until a real PASS.
- Next target: M70_WORLD_EXIT=0, M70_WORLD_LOAD_TEST=PASS, M70_MAP_INTEGRITY=PASS, plus absence of relevant LogLinker serialization errors. A pass proves package/world load only, not complete level simulation, performance or Android cook.


## M71 corrected map probe after image 09:12 (2026-10-16)
- Last actual console screenshot: M70_WORLD_EXIT=255, M70_MAP_INTEGRITY=PASS, M70_WORLD_LOAD_TEST=FAIL. Python log says SyntaxError: '(' was never closed (<string>, line 1), with script cut at unreal.load_package(, indicating inline -script code was truncated/misparsed. Earlier inline get_editor_subsystem test failed for the same SyntaxError. Therefore do NOT assert get_editor_subsystem is missing from UE; that was an unsupported earlier hypothesis.
- UE 5.8 official scripting guide supports -run=pythonscript -script=<file path> as well as inline Python. To avoid repeat parsing errors, created M71 standalone Python-file probe script on m66-smart-recovery branch.
- Staged project M70 only. Python source file and execution log live outside Content and original M63 project in $HOME/crownfall. Probe calls load_package then find_object to verify UWorld. No SaveMap/cook/compile/Play calls.
- Before invoking engine: compare live and stage TestMap binaries, record SHA-256, verify required paths, Python3 compile checks. After engine: compare both hashes, verify explicit M71_WORLD_OK and zero exit, check critical errors. Time limit 600s.
- Script passed local Bash syntax and Python AST parsing plus mock gate checks (normal PASS simulation and mutated source preflight reject). It has NOT run on the user's actual UE VM.
- Need M71_UNREAL_EXIT=0, M71_MAP_INTEGRITY=PASS, M71_WORLD_TEST=PASS before next Cook gate. Map package test not equivalent to gameplay runtime test.


## M71 actual VM probe results — 2026-10-16 09:17
- Screenshot is a live result from crownfall-m62-build: M71_UNREAL_EXIT=0; M71_MAP_INTEGRITY=PASS; M71_WORLD_TEST=FAIL.
- Logged nonfatal warnings shown by grep: "Failed to find game directory: /home/shami0112091997/UE_5.8.3/LastFrontier/Binaries" and ACL/AnimBone compression settings object missing. No screenshot evidence of a LogLinker serialization error or failure to load the TestMap asset.
- The result gate requires an exact M71_WORLD_OK marker. The screenshot did not show that marker, so do **not** treat an engine exit code 0 as proof that the package/world probe ran successfully. No new Cook/Android build initiated.
- Next step must be READ-ONLY log forensics, not repeat execution: show contents of $HOME/crownfall/M71_world_probe.py and match LogPython/PythonScriptCommandlet/TestMap/M71_WORLD_OK/ExitCode from $HOME/crownfall/M71_world_probe.log, including tail. Decide from evidence whether Python commandlet ran and why marker not present.
- Earlier M63 C++ load-only commandlet confirmed package/world PASS historically. If M71 was silently skipped by Python plugin or command-line dispatch, prefer proven C++ load-only mode on staged M70 after inspecting source for no-save behavior.
- Epic UE5.8 script docs allow -run=pythonscript -script=absolute_file.py in headless mode; they also explicitly state level-loading in commandlet can be tricky. Do not invent an API root cause without log evidence.


## تصحيح نتيجة M71 من سجل التنفيذ — 2026-10-16 09:20
**تصحيح فني اعتمادًا على صورة السجل الكاملة:** ملف Python المنفذ فعليًا هو:
```python
import unreal
p = unreal.load_package("/Game/Maps/TestMap")
assert p is not None, "PACKAGE_MISSING"
w = unreal.find_object(p, "TestMap", unreal.World)
assert w is not None, "WORLD_MISSING"
print("M71_WORLD_OK")
```
سجل محرك Unreal يوضح `LogPythonScriptCommandlet: Display: Running Python script: /home/.../M71_world_probe.py` ثم `Python script executed successfully`، `Success - 0 error(s), 4 warning(s)` وخروج عملية M71 = 0 مع `M71_MAP_INTEGRITY=PASS`. يثبت ذلك أن شرطي assert للـPackage والـWorld اجتازا عند تشغيل هذا الملف. لم يُعرض `M71_WORLD_OK` في سجل المحرك بسبب استخدام `print` الذي لم يظهر كرسالة `LogPython`؛ لذا `M71_WORLD_TEST=FAIL` كانت نتيجة تحقق نصي سلبية كاذبة، **وليست دليلًا على فساد الخريطة أو فشل التحميل**.

مراجعة التحذيرات: `Failed to find game directory .../UE_5.8.3/LastFrontier/Binaries` وتحذيرات ACL ظهرت مع خروج 0؛ لا نثبت ارتباطها بخلل محتوى الخريطة من هذه الأدلة. تم تعديل أداة M71 في GitHub لتستخدم `unreal.log("M71_WORLD_OK")` بدل `print` في أي تشغيل لاحق، لكن لا حاجة لإعادة الاختبار فقط للحصول على النص. هذا **نجاح فحص Package/World دون محاكاة تشغيل اللعبة**، وليس نجاح Cook أو Android AAB أو قياس الأداء.

الخطوة التالية: فحص تمهيدي محدود لـ Android Cook على نسخة M70، ومراجعة مسارات الخريطة والأصول وأوامر UAT والموارد؛ لا تغيير في M63 الأصلي، ولا نشر Google Play، ولا اعتماد StoreVersion=216 بينما أعلى versionCode في Play Console غير مؤكد وسجل سابق أشار إلى 217.


## M72 UI-literal copy error — screenshot 2026-10-16 09:25
- Screenshot shows user entered literal `{cmd}` at shell prompt, with response `{cmd}: command not found`. The assistant previously used a raw code block containing a dynamic binding instead of literal Bash, and the UI exposed raw placeholder. This is **assistant formatting error**, not a project or Unreal error.
- No M72 preflight ran in this screenshot; do not claim PASS or FAIL. The latest Unreal facts remain M70 compile exit=0, M71 Python executed successfully with assertions, M71 map integrity=PASS. The text-only gate in M71 was a false negative because `print` wasn't forwarded as expected, and the GitHub script was changed to use unreal.log in future.
- Future instructions: Provide all terminal commands literally in fenced code blocks, never use dynamic placeholders inside raw CodeBlock. Prefer one short auditable read-only command at a time when user is copying via Android phone. Do not run BuildCookRun until M72 environment/content gates checked and Play version/signing reviewed.


## M72 staged read-only preflight PASS — screenshot 2026-10-16 09:28
- From actual Cloud Shell screenshot on existing VM: LastFrontier.uproject, Content/Maps/TestMap.umap, Config/DefaultEngine.ini, Source/LastFrontier/LastFrontier.Build.cs: all PASS on M70 isolated stage.
- M72_MAP=PASS: original M63 TestMap and staged M70 TestMap are byte-for-byte identical at preflight time.
- M72_ASSET_COUNT=23 (.uasset files in M70 stage), not an invented content-size claim.
- Staged DefaultEngine.ini: PackageName=com.crownfall.stronghold, StoreVersion=216, TargetSDKVersion=36, bBuildForArm64=True, bEnableBundle=True.
- Disk: /dev/root ~243G total, ~110G used, 133G free, ~46% used. Capacity is indicative; memory/SDK were separately verified previously.
- Latest true compiler result M70_COMPILE_EXIT=0; M71 Python script successful with both asserted world/package checks and integrity PASS, but script's log-string gate false negative because print did not forward.
- **No Android Cook, Package, signed AAB, real phone performance, or Play Console highest version check** performed as of this capture. Previous Play history says 217 while staged StoreVersion=216. Do not attempt Play upload with 216.
- Next safe action: assess stage assets, configs and cooked-map list; inspect Android build readiness before making a deliberate controlled BuildCookRun. Avoid running CI or mutating the live M63 project.


## M72 to M73 controlled Android ASTC Cook — 2026-10-16
- Actual screenshot M72 PASS: 4 required file checks, M72_MAP=PASS, 23 .uasset files, package com.crownfall.stronghold, StoreVersion=216, TargetSDKVersion=36, bBuildForArm64=True, bEnableBundle=True; disk 243GB total/133GB available.
- Official Epic UE5.8 Cooking Content docs confirm independent -run=Cook with TargetPlatform; Android ASTC target appears in actual Epic Android cook logs. Cook creates platform-specific assets under staged project's Saved directory, NOT an AAB.
- Added Scripts/M73_Android_ASTC_Cook_Stage_Only.sh; source is guarded by map byte comparison, project/engine existence, minimum 60GiB free disk, time limit 45 minutes, original-vs-staged map SHA256 after execution, returns exact exit code and inspects log. Never calls signing, Android package, store upload, or gcloud API; no deletion of original.
- Command passed local bash -n syntax validation; not yet executed on user's VM. A zero exit by itself is not proof of full Play-ready Shipping binary. If any failure occurs, stop and inspect log rather than repeating blindly.
- Highest Play Console versionCode remains unverified, source 216 is under previously recorded Play line 217; cook-only may use version 216 as it cannot be uploaded. Production staged release must adopt code strictly above confirmed Play max.


## M73 Android_ASTC Cook result from VM screenshot — 2026-10-16 09:38
- Verified from user's real Cloud Shell screenshot on existing `crownfall-m62-build` VM: `M73_ANDROID_COOK=STARTED`, `M73_COOK_EXIT=0`, `M73_MAP_INTEGRITY=PASS`.
- Unreal reported `LogInit: Display: Success - 0 error(s), 5 warning(s)`. Output files shown under isolated stage `$HOME/crownfall/M70_ANDROID_STAGE_20261016T053500Z/Saved/Cooked/Android_ASTC/` include Engine GlobalShaderCache and Engine/Content/EditorResources. This verifies the Cook commandlet exited successfully and wrote platform-specific files, not necessarily that the user's project map `TestMap` and game .uasset packages were cooked.
- Exact VM cook log: `$HOME/crownfall/M73_ANDROID_ASTC_COOK.log`. Original M63 content remained map-hash equal to M70 stage after the run.
- **Required next read-only gate**: inspect cooked directory for actual `TestMap.umap` and cooked project assets, and correlate with saved log `TestMap`, `LogCook` and any warning or hidden errors; do not infer map/package completeness from GlobalShaderCache or EditorResources. Epic's 5.8 official cooking documentation distinguishes platform-specific Cook outputs from packaging (AAB).
- Shipping `AAB`, signed upload keystore verification, `versionCode > Play Console max`, API36, ELF/16KB, device gameplay FPS tests, and Google Play compliance remain UNVERIFIED. Current staged StoreVersion=216 is not usable for Play if historical 217 max still applies.
- No new cloud resources provisioned, no live-project modification, no Play publication.
