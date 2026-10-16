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


## M74 verified complete Android_ASTC project cook — 2026-10-16 09:45
- Actual user's VM screenshot shows M73_COOK_EXIT=0, M73_MAP_INTEGRITY=PASS, LogCook final "Done!" / commandlet result 0 and "Success - 0 error(s), 5 warning(s)".
- M74 read-only verification of $HOME/crownfall/M70_ANDROID_STAGE_20261016T053500Z/Saved/Cooked/Android_ASTC confirmed cooked LastFrontier/Content/Maps/TestMap.umap + TestMap_M63_Atomic.umap and corresponding .uexp, plus cooked real wooden crate, large castle door and street lamp .uasset objects.
- Final cook statistics visible: Packages Cooked: 220, Packages Incrementally Skipped: 0, Packages Skipped by Platform: 1, Total Packages: 221; zero packages remain. M73_COOKED_FILE_COUNT=552 on disk.
- This supersedes the previous M73 checkpoint's concern that only engine global cache and editor assets had been observed: GAME CONTENT AND MAPS NOW VERIFIED in Android_ASTC cook outputs. Do not confuse game cook PASS with android native ARM64 build/package/signature/AAB/device runtime PASS.
- User's live staged DefaultEngine.ini still reads StoreVersion=216 with historical Play line 217. Confirm highest actual version via Play Console and stage a strictly higher version before any actual Play release. UnrealEngine 5.8 targetSdk 36 actual manifest must be verified on built package.
- Reviewed Epic 5.8 Android Settings, Packaging and Distribution Signing docs. Signed Shipping AAB needs unique app ID, matching upload keystore/alias, correct StoreVersion, Shipping+Distribution, valid actual Android target; never ask for keystore passwords or dump signing config into logs.
- Reviewed dormant Scripts/M68_Staged_Android_Build.sh and corrected its invalid headless get_editor_subsystem/print map probe to package=unreal.load_package, unreal.find_object(package,"TestMap",unreal.World) and unreal.log marker, aligned with M71's actually successful Python script. This is a source code fix committed to GitHub, not an executed M68 build.
- Next gate M75: read-only staged packaging/signing/version readiness audit. No GPU/device testing has taken place; no AAB has been built or uploaded.


## M75 actual VM Shipping preflight — 2026-10-16 09:55
- Screenshot confirms `COOKED_MAP=PASS`, `MAP_INTEGRITY=PASS`, `M75_CHECK_COMPLETE`, `REAL_GAME_ASSETS=23`. Cooked M70 Android_ASTC assets are actually present.
- Staged DefaultEngine.ini reports PackageName=com.crownfall.stronghold, StoreVersion=216, TargetSDKVersion=36, bBuildForArm64=True, bEnableBundle=True.
- Signing fields checked in staged DefaultEngine.ini: `KeyStore=NOT_CONFIRMED` and `KeyAlias=NOT_CONFIRMED`. This is an incomplete-scope search, **not proof that signing files/keys do not exist elsewhere**. Protect all signing passwords, alias secrets, upload keystores; do not request them in chat or commit them.
- Official Google Play requirements checked: same package as existing app, strictly greater versionCode, correct matching upload signature (Play App Signing). Epic UE 5.8 Android settings say keystore should be in <Project>/Build/Android and signing configuration under Distribution Signing.
- The historical highest Play versionCode reference is 217, while M70 is 216; must confirm latest from Play Console before making a new staged release (218 is only a conditional candidate, not verified).
- **No Android Shipping AAB actually built, signed, tested on device or uploaded yet.** Do not claim release readiness from M75 PASS.
- Next action: small read-only check for existing local upload keystore files and field presence (without exposing values or searching secrets globally), then user checks Play Console version maximum and upload certificate. Do not generate a new upload key arbitrarily or alter M63.


## M76 signing key file presence check — 2026-10-16 09:58
- User screenshot confirms count `0` *.jks / *.keystore files in both original M63 and staged M70 `Build/Android` (each searched maxdepth 2), and `M76_READONLY_COMPLETE`.
- This proves only absence in those two specific Build/Android folders, not loss of the upload key globally or that Play App Signing is not enrolled. Prior M75 found no explicit KeyStore/KeyAlias in staged DefaultEngine.ini, again not definitive beyond that file.
- **Do not generate a replacement key now.** Consult the app's Play Console Play app signing status and Upload key certificate, confirm current highest versionCode on Latest releases and bundles, and check user's securely held original upload keystore or backup. Do not paste password, private keystore, tokens, key material or sensitive account data into chat/GitHub.
- Verified current official Google Play docs https://support.google.com/googleplay/android-developer/answer/9842756 describe two keys (Upload key user-owned, App signing key Google-managed); if Play App Signing enabled and upload key truly lost, supported official upload-key reset via Play Console exists. Reference https://support.google.com/googleplay/android-developer/answer/9859350 states updates require same package, greater versionCode and correct signing. Historical code 217 remains unverified, current stage 216.
- Actual CROWNFALL Android ASTC Cook completed with 0 errors and map/assets verified, but no correctly signed shipping AAB has been established yet.
- Next user action: open Google Play Console for the CROWNFALL app and locate Play App Signing's Upload key certificate status; screenshot screen with private data hidden if possible. Only after that decide whether original key retrieval, reset flow, or package/sign testing is appropriate.


## M76 historical signing key recovered in Library — 2026-10-16
- CORRECTION to M76: only two VM project folders had no .jks; **the original upload keystore was not lost**. The persistent ChatGPT file Library was directly inspected and contains the binary `CROWNFALL_v0.8_upload_key.jks` (3,836 bytes each) in two separate backup folders: `/CROWNFALL_Signing_Backup/` and `/CROWNFALL_Signing_Backup_Secondary/`. Both listings are current and complete. The backups are PRIVATE; never commit or share their bytes, signing recovery passwords, or any secrets to GitHub or logs.
- Backup_Verification.txt created 2026-10-05 records expected keystore SHA256 `b4822980977b29f6106187f5f5e1c6480075fdfe08c210897a202ccf2da11b8b`. This is a HISTORICAL recorded checksum; identical current file contents are NOT YET verified by hashing both backups. Verify locally/privately before use, not by transmitting key contents or passwords.
- Old signed AAB backup files v0.8 and v0.9 are present. v0.9 readiness record says old `com.crownfall.stronghold`, versionCode 9, targetSDK 36, signing verification SUCCESS. These are historical *old Android app packages*, not the M70 UE5.8 real game Shipping AAB.
- Past conversation records from Oct 8 report that v215 was initially signed with Debug then corrected using an upload key and re-signed; v216 was built, then v217 after removing an old billing permission, and v217 was accepted on internal test. M66 recovery report independently records Play upload line reaching 217 and debuggable=false. However, no LIVE Play Console API state read in this session; current top versionCode, upload certificate identity and Play App Signing enrollment need verification before a new production-ready release.
- User's next safe actions: (1) determine current highest versionCode and current upload key certificate in Google Play Console for com.crownfall.stronghold, (2) securely verify existing backup's hash/fingerprint without sharing the keystore or passwords, (3) if signing needed, transfer only over user's secure permitted channel (never GitHub), (4) update only a staging build version to strictly exceed confirmed highest Play code, (5) build and validate the true UE Shipping AAB.
- Do NOT reset or generate a new signing key solely because VM Build/Android directories returned zero. Do not claim production readiness: Unreal M70 Editor compile and Cook are verified, M70 signed AAB and phone tests remain pending.


## M77 Signing backup SHA256 verified and release staging prepared — 2026-10-16
- User requested continued Android First CROWNFALL settings; all changes remain in private GitHub branch `m66-smart-recovery`. NO VM or Play Console actions performed in this session. Latest actual VM results: M70 Editor compile PASS; M71 package/world Python asserts completed successfully and both TestMap hashes unchanged; M73 Android_ASTC Cook exit 0 with 220 packages cooked, 1 platform-skipped; M74 contains real cooked maps/assets; M75 cooked map/23 assets PASS; M76 found zero *.jks/*.keystore in TWO project/Build/Android folder locations (does NOT mean key lost).
- Private ChatGPT Library was inspected for `CROWNFALL_v0.8_upload_key.jks` in `/CROWNFALL_Signing_Backup/` and `/CROWNFALL_Signing_Backup_Secondary/`. Two binary files were temporarily materialized into isolated model workspace ONLY to calculate SHA-256, both 3,836 bytes; each SHA256 **matched the recorded historical SHA256 exactly**, `b4822980977b29f6106187f5f5e1c6480075fdfe08c210897a202ccf2da11b8b`. The temporary working copies were deleted immediately after verification; both Library originals remain untouched. No private key content or password was viewed, committed or copied to VM.
- This confirms that the two saved keystore binaries are byte-identical and match the 2026-10-05 backup report, **NOT that their upload certificate fingerprint matches the currently registered Play Console key**, and NOT that the password is known/accessible. Do not reset/create a replacement key until the registered Play Console upload certificate is checked.
- Previously saved Library release readiness v0.9 report confirms old WebView-era application `com.crownfall.stronghold` versionCode 9 signed AAB; DO NOT confuse with UE real Shipping AAB. M66 recovery report says Play-upload line reached 217, but live highest versionCode still requires current Play Console confirmation; the current M70 staged Unreal config StoreVersion is 216.
- Newly authored Scripts/M77_Prepare_Isolated_Android_Release.sh commits code-only staging support. Default AUDIT mode is read-only; STAGE mode requires `M77_MODE=STAGE`, `M77_APPROVED=YES`, `PLAY_MAX_CONFIRMED` and `NEXT_VERSION_CODE` greater than both source and Play maximum. It stages a timestamped copy from M70 with no Saved/Intermediate/Binaries and explicitly excludes .jks/.keystore/.p12/.pem; checks original/stage TestMap hashes; changes version ONLY in the new release stage. NO actual M77 stage created on VM; no signing secrets handled; no AAB built/published.
- Official documentation checked: Epic UE5.8 Signing/Android and Play App Signing support keystore in Build/Android, alias and passwords configured privately; Google Play new/updates require target API 36 from 2026-08-31; 16KB ELF/zip compatibility needs proof via built AAB and device. Do not blindly alter UE5.8 Android Gradle toolchain merely because official Epic recommends SDK35.
- NEXT decisive external dependency: obtain the current highest versionCode in app `com.crownfall.stronghold` from Google Play Console and registered Upload key certificate SHA-256 (PUBLIC CERT fingerprint, not a password/private key). Only then approve candidate next version and securely use existing signing key for a fully isolated Shipping AAB build, and validate actual AAB signature/manifest/16KB/device behavior.


## M77 Google Play Console latest-release evidence — 2026-10-16 10:23 local
- Screenshot of the signed-in Play Console for CROWNFALL, page in Arabic "أحدث الإصدارات والحزم" (Latest releases and bundles), visibly shows top entry: release/version `217 (2.2.0)` and release track `الاختبار الداخلي` (Internal testing), with "أحدث إصدار" value 217.
- This is fresh in-account UI evidence, much stronger than the prior M66 historical note. It **confirms 217 as the latest visible release on this screen**, NOT an exhaustive proof that no higher unused/draft version code has ever been uploaded (consult all app bundles to confirm uniqueness before upload).
- `218` becomes the tentative NEXT_VERSION_CODE, subject to checking complete app-bundle history and that it is available; DO NOT change M63 original project or M70 stage, upload to Play, or sign without independent certificate confirmation.
- Next user action: inside the same app: hamburger menu > "الاختبار والإصدار" > "سلامة التطبيق" (App integrity) > "توقيع التطبيق من Play" > "شهادة مفتاح التحميل" (Upload key certificate), capture public SHA-256 fingerprint with private account identifiers obscured.
- Keystore `CROWNFALL_v0.8_upload_key.jks` backed up twice in private Library; both binaries previously SHA256 verified against Oct 5 checksum. The checksum of the **file** is not the upload-key **certificate** fingerprint: compare the proper certificate fingerprint securely, not a password or JKS bytes.
- App's Unreal M70 staged config is versionCode 216; M70 Editor Compile, M71 package/world, M73 ASTC Cook, M74 asset audit all PASS. Shipping Android AAB not built, signed, runtime-tested or published.


## M77 Google Play complete bundle ledger verified — 2026-10-16 10:25 local
- Screenshot from authenticated Google Play Console app "جميع حزم التطبيقات" (All app bundles) shows **5 app versions in total, 1-5 of 5**. The complete visible version code history is: 217 (versionName 2.2.0), 216 (2.2.0), 215 (2.2.0), 214 (2.1.2), 212 (2.1.2).
- Highest Play uploaded bundle versionCode CONFIRMED = 217 based on complete visible all-bundles page. No code 218 in this ledger as of screenshot.
- Next **release-stage** candidate versionCode = 218, valid as long as no competing new upload is made before stage/submission. Recheck current ledger just before upload.
- New Unreal M70 stage configuration currently StoreVersion=216; NEVER upload 216/217 again. Only adjust StoreVersion in a fresh isolated M77 stage, AFTER upload certificate equivalence is verified and explicit approval for staging.
- Next urgent blocker: Play Console -> "الاختبار والإصدار" -> "سلامة التطبيق" (Test and release -> App integrity) -> "شهادة مفتاح التحميل" (Upload key certificate): obtain publicly displayable SHA-256 certificate fingerprint and compare to private backup JKS certificate via keytool, never share password, private key or JKS. The JKS file SHA256 is different from certificate fingerprint; previous backup-file hash match does NOT establish upload certificate equality.
- Last proof for Unreal remains M70 Editor Compile=PASS; M71 package/world load assertions=PASS; M73 Android_ASTC Cook=PASS 220 cooked packages/1 skipped; M74 cooked maps/assets verified; M75 project content verified; signed UE Shipping AAB and device tests PENDING. No Google Play submission, GCP changes, or VM commands executed at this checkpoint.


## Signing certificate comparison — user-supplied fingerprint 2026-10-16
- The user supplied a 32-byte SHA-256 certificate fingerprint beginning BF:5E:99:BD and ending 8C:44:8E:CC:8C:F2, after navigating Google Play Console's "توقيع التطبيق" page. It is **not equal** to the public X.509 certificate fingerprint embedded in the two private Library JKS backup files.
- JKS (standard JKS v2 0xFEEDFEED) public certificate chain extracted from both backups, without password or private-key decryption. Both backups have **one identical X.509 certificate** with certificate SHA256 fingerprint `40:C0:DB:40:40:BE:0B:F9:B2:50:BD:4D:64:F9:7E:34:05:33:06:C2:C0:25:DC:3F:86:EC:48:BC:2A:DE:A1:B8`.
- Independently inspected **signature-certificate metadata** of old signed AAB `CROWNFALL_Stronghold_v0.9_Release_Signed.aab` held in the user's private Library. Its PKCS#7 certificate SHA256 is **exactly the same 40:C0:...:A1:B8** as the JKS certificate. The user-supplied BF:5E:...:8C:F2 is different.
- This mismatch does not on its own mean the key is wrong: the user likely copied the first **App signing key certificate**, which Google Play manages, rather than the separate **Upload key certificate**. DO NOT claim a mismatch with registered Play upload key until the specific Upload key certificate section is verified. Do not upload or reset keys.
- All temporary materialized JKS and signed-AAB work copies were removed from the model's working directory after computation. Private Library originals remain. No password was requested/used and no key uploaded to GitHub, VM or Play.
- NEXT: in Play Console's App signing page, scroll below `مفتاح توقيع التطبيق` to `مفتاح التحميل` or `شهادة مفتاح التحميل`, copy the **SHA-256 certificate fingerprint of the upload key** and compare to exact fingerprint above. If equal, move to explicit approval of M77 staging code 218. If different, stop signing and investigate Play upload key reset/rollover history, but do not reset without owner approval.


## Historical signing recovery report confirmed — 2026-10-16
- Directly read the 2026-10-05 original **CROWNFALL_v0.8_Signing_Recovery.txt** in private Library (not merely a summary). It explicitly identifies `CROWNFALL_v0.8_upload_key.jks` as the intended Google Play upload key, and records **Certificate SHA-1** `60:15:C8:63:D5:84:BF:FB:71:1B:4F:B1:65:A6:31:C7:43:70:93:5C` and **Certificate SHA-256** `40:C0:DB:40:40:BE:0B:F9:B2:50:BD:4D:64:F9:7E:34:05:33:06:C2:C0:25:DC:3F:86:EC:48:BC:2A:DE:A1:B8`. The record includes confidential recovery metadata, which was not copied to GitHub.
- The old v0.9 Play Upload Readiness report records `com.crownfall.stronghold`, code 9, target SDK36, signed AAB with the existing upload key and successful signature verification. Old version AAB inspection likewise matched the local JKS certificate. Strong proof of **historical use**, not proof of current Play Console registration.
- Personal history retrieval did **not** find a prior screenshot/text explicitly identifying the **Google Play Upload key certificate** SHA-256. The user-supplied `BF:5E:99:BD:...:8C:F2` was copied after the screenshot of the App signing key section (Google-managed); it is not the old local JKS certificate.
- Conclusion: the expected original Upload key certificate SHA-256 is **40:C0:...:A1:B8**, and the key backups exist and match historical checksums. The only external condition still unresolved is the *actual currently enrolled Play upload certificate* fingerprint; do not declare it matched, reset key, or attempt signed AAB release until the correct section is read.
- Complete app bundle ledger in current Play Console confirms max versionCode 217; M77 planned next=218, but actual Shipping AAB, matching signing, ARM64, 16KB and phone tests still pending.


## M77 Upload key certificate DER independently matched — 2026-10-16
- The user uploaded `upload_cert.der` after navigating CROWNFALL's Play Console App signing screen and was asked to provide the Upload key certificate. The binary public X.509 DER certificate (1,318 bytes) was parsed locally with `openssl x509 -inform DER` without any password, JKS extraction, private key, or Play Console write.
- DER X.509 certificate SHA-256 fingerprint: `40:C0:DB:40:40:BE:0B:F9:B2:50:BD:4D:64:F9:7E:34:05:33:06:C2:C0:25:DC:3F:86:EC:48:BC:2A:DE:A1:B8` — **exact match** to both original private JKS backups and signed old AAB public certificate verified earlier.
- DER certificate SHA-1 fingerprint: `60:15:C8:63:D5:84:BF:FB:71:1B:4F:B1:65:A6:31:C7:43:70:93:5C` — exact match to historical `CROWNFALL_v0.8_Signing_Recovery.txt`.
- Public X.509 subject: `O=CROWNFALL, CN=CROWNFALL Stronghold Upload Key`; issuer identical (self-signed). Certificate validity from 2026-10-05T07:35:57Z until 2054-02-20T07:35:57Z.
- This removes the certificate mismatch risk **provided the uploaded DER indeed originated in Play Console's Upload key certificate section**, which is user-provided provenance. Old `BF:5E:...` appears to be a different Google app-signing certificate. No private key, secret, password, certificate binary or DER was committed.
- Remaining gates: M77 staged code 218 based on Play all-bundles 5-row ledger max 217; verify private JKS signing alias/password available solely in user's secure environment (never in chat or GitHub); controlled UE Android Shipping distribution BuildCookRun; inspect AAB signature, AAB manifest package/targetSdk36/versionCode218, native ARM64 ELF 16KiB and bundletool delivered APK ZIP/page checks, phone launch/crash/performance; only then Play internal test upload. **No AAB or remote build performed in this step.**


## M77 isolated release stage 218 PASS — VM screenshot 2026-10-16 10:53
- Actual screenshot shows shell on existing `crownfall-m62-build` completed M77 bash stage creation, not merely planned.
- `M77_RELEASE_STAGE=PASS`, `M77_VERSION_CODE=218`, `M77_ORIGINAL_MAP=UNCHANGED`.
- Exact new staged project directory shown: `/home/shami0112091997/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z`. Copied from previously cooked/compiled M70 stage, excluding `Saved`, `Intermediate`, `Binaries`, `DerivedDataCache`, `.git`, `*.jks`, `*.keystore`, `*.p12`, `*.pem`. Only staged `Config/DefaultEngine.ini` StoreVersion updated 216->218.
- Both M63 original map and M70 stage map passed binary `cmp -s` against new M77 stage map at command exit, but this does not establish full source tree parity or game content quality.
- Proof of bundle ledger Play Console on 2026-10-16: five total bundles, max 217, so M77 candidate 218 is not already present.
- `upload_cert.der` user supplied after App Signing page has SHA256 `40:C0:DB:...:2A:DE:A1:B8`, matching the user's two JKS backup certificates and old signed AAB. This resolves certificate identity at the public-certificate level. Credentials/password access for actual signing remains private and unverified.
- The next work is to compile **LastFrontier Android Shipping** on the stage (without -package, -distribution or upload), preserving map checks and capturing an authoritative UBT log. Should start only if staged project + source target + Engine/Build/BatchFiles/Linux/Build.sh and resource preconditions pass. Follow up with signed AAB build only after Android Shipping compile genuinely PASS and signing is configured privately.
- No claims of a compiled Android Shipping binary, signed AAB, successful device test or Play upload yet.


## M78 Android Shipping native compile begun — screenshot 2026-10-16 10:59 local
- Actual Cloud Shell screenshot on existing VM `crownfall-m62-build` shows successful M77 stage creation: `M77_RELEASE_STAGE=PASS`, `M77_VERSION_CODE=218`, `M77_ORIGINAL_MAP=UNCHANGED`; M77 stage path `$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z`.
- A new `bash <<'M78'` compile command was issued against the isolated M77 stage and the last visible line is `M78_PREFLIGHT=PASS`. The bottom of the screenshot shows no completed shell prompt.
- This is an **in-progress** `Build.sh LastFrontier Android Shipping <M77>/LastFrontier.uproject -NoHotReloadFromIDE -Progress` with 2400-second timeout and log `$HOME/crownfall/M78_ANDROID_SHIPPING_COMPILE.log`. **Neither `M78_COMPILE_EXIT` nor `M78_MAP_INTEGRITY` is visible**; do NOT claim Shipping build PASSED.
- Next step: wait for completion, don't restart, and inspect exit code, error summaries and map integrity. Only after a real build result should M79 packaging/signing proceed. The Play upload cert DER and local JKS certs matched previously; keystore and secret material have NOT been placed on VM or GitHub.


## M78 Android Shipping compile PASS from Cloud Shell screenshot 2026-10-16 11:01
- **Real on-VM user screenshot, not simulation**: M77 isolated stage at `/home/shami0112091997/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z`, with StoreVersion 218, original TestMap unchanged.
- M78 `Build.sh LastFrontier Android Shipping <M77>/LastFrontier.uproject -NoHotReloadFromIDE -Progress` concluded successfully: `M78_PREFLIGHT=PASS`; `M78_COMPILE_EXIT=0`; `Result: Succeeded`; `M78_MAP_INTEGRITY=PASS`; terminal prompt returned.
- Output log exact path `$HOME/crownfall/M78_ANDROID_SHIPPING_COMPILE.log`. This passes native Android Shipping **compile** stage. Still need independently inspect presence of staged arm64 binaries and log to establish exact output and readiness.
- Earlier M73 Android_ASTC Cook on M70 passed with 220 packages cooked, but M77 intentionally excludes `Saved/`; therefore M77 stage needs its own cook/package sequence, even if cache reuse possible.
- Remaining: check Android game binary, DefaultGameMap/packaging maps, Shipping configuration; configure original verified upload JKS securely (never through chat/GitHub), then UAT controlled build/cook/package/distribution to produce signed real AAB, confirm versionCode218/package and actual targetSDK36, source signature, 16KB ELF/page support, device install/play/crash/perf, Play upload internal testing. No M79, AAB, device or Play publish success claimed.
- **Do not rerun M78**. Next step is M79 low-cost **read-only** artifact and packaging/map check in current SSH session; do not introduce new VM/cloud resources.


## M79 Shipping output audit: unexpected AAB exists — user VM screenshot 2026-10-16 11:05
- On the user's real connected VM `crownfall-m62-build`, M79 read-only audit of `$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z` confirmed the M78 Build.sh result `Succeeded` and staged Android Shipping output.
- Files visible under `Binaries/Android`: `packageInfo.txt` (93 bytes), `LastFrontier_Symbols-v218/LastFrontierarm64/libUnreal.so` (~180,137,976 bytes), `LastFrontier-Android-Shipping.target` (~81,920 bytes), `LastFrontier-Android-Shipping-arm64.so` (~180,137,976 bytes), and — IMPORTANT — **`LastFrontier-Android-Shipping.aab` (41,916,003 bytes)**. The AAB filename EXISTS even though we have not independently verified ZIP/App Bundle structure, embedded manifest/version/target API, signing certificate, or validity. DO NOT call it finished or signed because only its path/size are known. The build command was pure Build.sh (not UAT -package), so investigate why/how the AAB was produced before trusting it.
- `GameDefaultMap=/Game/Maps/TestMap`; maps `TestMap.umap` and `TestMap_M63_Atomic.umap` are present; `M79_MAP_INTEGRITY=PASS`.
- Staged ini: `PackageName=com.crownfall.stronghold`, `StoreVersion=218`, `TargetSDKVersion=36`, `bBuildForArm64=True`, `bEnableBundle=True`. This confirms config text only, not real AAB manifest.
- `M79_STAGE_COOK=NOT_YET_GENERATED` because current M77 Saved/Cooked/Android_ASTC folder absent. Earlier Android Cook PASS was on **M70**, which M77 staging explicitly excluded Saved from copying. Do not assume AAB contains cooked real game assets.
- Next action: read-only M80 audit of the *existing* 41.9 MB AAB to confirm ZIP integrity, Android App Bundle structure (`BundleConfig.pb`, `base/manifest/AndroidManifest.xml`, dex and arm64 library), signing state/certificate public fingerprint (no keystore passwords), and perhaps bundletool validate if already available; no rerun build or upload.
- A valid AAB is not yet proven. M77 original map and signing backup/Play public upload certificate identity are known; Play all-bundles max 217, M77 code 218. The user wants Google Play shipping AAB but **no publication before successful Android device and bundle tests**.


## M80 existing AAB ZIP valid but signer differs and jarsigner inconsistencies — screenshot 2026-10-16 11:10
- Read actual user Cloud Shell screenshot 11:10 from `crownfall-m62-build`, AAB path `$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z/Binaries/Android/LastFrontier-Android-Shipping.aab`, size **41,916,003 bytes**.
- `M80_ZIP=PASS`; `M80_BUNDLE_CONFIG=PRESENT`; `M80_BASE_MANIFEST=PRESENT`; `M80_ARM64_LIB=PRESENT`; `M80_DEX=PRESENT`; `M80_ASSETS=1`; `M80_SIGNER_ENTRIES=1`.
- keytool `-printcert -jarfile` gave current AAB's embedded certificate **SHA256: 6C:74:9E:D8:29:72:52:80:03:9C:F5:4C:E8:B2:9E:0B:05:B3:49:16:9B:36:55:AD:24:D7:D8:B0:C0:55:C9:E6**. It does **NOT** match registered Play **UPLOAD certificate** SHA256 `40:C0:DB:40:40:BE:0B:F9:B2:50:BD:4D:64:F9:7E:34:05:33:06:C2:C0:25:DC:3F:86:EC:48:BC:2A:DE:A1:B8`, independently matched to user's upload_cert.der and both JKS backups. (NB: verify exact hex digit groups if full precision needed, read screenshot).
- `jarsigner -verify` output has repeated `Entry base/root/play-services-*.properties is signed in JarFile but is not signed in JarInputStream`, also `META-INF/MANIFEST.MF` same message; screenshot does NOT show `jar verified`. Need get actual jarsigner exit code with `-strict` and targeted log forensic; don't declare signed bundle valid based on signature entry count. Oracle jarsigner docs classify JarFile vs JarInputStream discrepancies as internal inconsistencies. Per Android developer docs, Android App Bundles must be signed using jarsigner (not apksigner); bundletool tests delivery. refs https://docs.oracle.com/en/java/javase/25/docs/specs/man/jarsigner.html and https://developer.android.com/tools/bundletool .
- `M80_ASSETS=1` is a count of ZIP entries under base/assets, not a count of Unreal game .uasset; can still be a single .pak/.ucas/.utoc. Inspect actual asset name and uncompressed size. M77 Saved/Cooked/Android_ASTC missing while M70 had 220 cooked packages; do not assume this bundle contains those actual maps/meshes.
- Release status: **NOT ready** for Play internal testing. Do not upload or re-sign possibly invalid bundle. M81 read-only audit should collect strict jarsigner return code, jar signing cert owner, and base/assets archive entries. Investigate origin/rebuild after diagnosing. Preserve M63/M70 and private keys.


## M81 strict jarsigner verification and Python copy error — screenshot 2026-10-16 11:14
- Actual user screenshot shows that M81 audited existing Android Shipping AAB under `$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z/Binaries/Android/LastFrontier-Android-Shipping.aab`.
- `keytool -printcert -jarfile`: `Owner: C=US, O=Android, CN=Android Debug`, `Issuer: C=US, O=Android, CN=Android Debug`, **SHA256: 6C:74:9E:D8:29:72:52:80:03:9C:F5:4C:E8:B2:9E:0B:05:B3:49:16:9B:36:55:AD:24:D7:D8:B0:C0:55:C9:E6**. Therefore AAB currently signed by **Android Debug** key, NOT the user's verified Google Play upload certificate SHA256 40:C0:DB:40:...:2A:DE:A1:B8.
- `M81_JARSIGNER_EXIT=4` under `jarsigner -verify -strict -verbose`; screenshot contains multiple `signed in JarFile but not signed in JarInputStream` warnings. **Nuance confirmed via Oracle jarsigner official docs:** strict code 4 denotes one or more severe warnings, e.g. a *self-signed certificate* or unvalidated chain. `JarFile/JarInputStream` internal inconsistency is separately classified an informational warning; do **not** infer cryptographic signature failure or archive corruption solely from exit code 4. Actual DEBUG certificate mismatch is the definite Play upload blocker.
- M81 Python block intended to inventory `base/assets/` and ARM64 failed before running: `File "<stdin>", line 16 ... SyntaxError: '(' was never closed`; thus **no M81 content count or asset archive proof** was produced. M80 showed `M80_ASSETS=1` but that counted ZIP *entries* below base/assets, not cooked assets; M77 Saved/Cooked was absent. Further inspection of actual assets must precede deciding to repackage or overwrite.
- Next recommended step is a read-only, Python-free command using `unzip -l`/`unzip -Z -1` to reveal actual `base/assets/` payload paths and uncompressed lengths; inspect `jarsigner` log selectively for fatal versus warning details. No signing or upload until confirmed game payload and correct certificate. Do not repeat M78 native Shipping compile without evidence of code change.
- Private JKS backups remain in Library, not on VM; do not paste JKS or passwords, or commit to GitHub. Play Console all bundles max 217, proposed next 218 on isolated M77 stage; registered public upload cert matched user DER 40:C0:...:A1:B8.


## M82 verified ZIP but no game payload in base/assets — 2026-10-16 11:20
- User screenshot of `M82_READONLY_COMPLETE` on existing VM confirms: `unzip -t` showed **"No errors detected in compressed data"** for `$HOME/crownfall/M77_RELEASE_STAGES/M77_v218_20261016T075330Z/Binaries/Android/LastFrontier-Android-Shipping.aab`.
- `unzip -l` when filtered to `base/assets/`, `base/lib/arm64-v8a/`, and `base/manifest/`, found **only one base/assets payload**: `base/assets/vkqualitydata.vkq` (**23,275 bytes**). Native libs include `base/lib/arm64-v8a/libUnreal.so` (**99,678,952 bytes uncompressed**), `libpsoservice.so`, `libswappy.so`, `libvkquality.so`. Manifest exists.
- No CROWNFALL Unreal game `.pak`/`.ucas`/`.utoc` was visible in inspected `base/assets`; **this is insufficient to conclusively prove the absence of other AAB asset-pack modules**, so do not falsely claim a complete archive-wide scan. However, `M79_STAGE_COOK=NOT_YET_GENERATED` is independent proof that M77 Stage Cook has not occurred.
- `jarsigner -verify -strict` earlier exit 4, due to Android Debug self-signed certificate and informational JarFile/JarInputStream inconsistencies; M82 log excerpt says `jar verified, with signer errors`, `This jar contains entries whose signer certificate is self-signed`. Do not call ZIP corrupted merely from those warnings. The **certified signer is Android Debug** with SHA256 6C:74:...:C9:E6, not the Play-approved public Upload key cert 40:C0:...:A1:B8; so the current 41.9 MB bundle MUST NOT be uploaded as a Play release.
- Reviewed official Epic 5.8 Android Packaging docs (https://dev.epicgames.com/documentation/unreal-engine/packaging-android-projects-in-unreal-engine) and Build Operations BuildCookRun docs (https://dev.epicgames.com/documentation/unreal-engine/build-operations-cooking-packaging-deploying-and-running-projects-in-unreal-engine): packaging requires Cook and staging of game data; Build.sh compilation alone does not establish release package content. M77 stage excluded `Binaries` and `Saved` initially; M78 generated Android Shipping binary but no Editor target, so M83 may need UAT `-build` for editor host tools.
- Authored `Scripts/M83_UAT_Build_Cook_Stage_Android_ASTC_Only.sh` in GitHub. Bounded 3600s UAT `BuildCookRun -project=<M77> -noP4 -platform=Android -cookflavor=ASTC -clientconfig=Shipping -build -cook -stage -pak -unattended -utf8output`, **without** `-package`, `-archive`, `-distribution`, `-deploy`, `-run`, signing or secret reads. Guard original TestMap equality, config StoreVersion218, package, target SDK36, arm64, AAB, symlinks, free >=50GiB, no log clobber. Output `$HOME/crownfall/M83_ANDROID_ASTC_UAT_STAGE.log`, source stage only, no signing. Script locally bash -n checked; **NOT YET executed on VM**.
- Next gate: run M83 on same VM, wait for `M83_UAT_EXIT=0`, `M83_MAP_INTEGRITY=PASS`, verify `Saved` cooked map and nonempty staged `.pak/.ucas/.utoc` before next real AAB packaging. If UAT fails inspect log once; no blind retry or re-sign until content valid.


## Deep risk review before M83 — 2026-10-16 11:21 local
- User explicitly requested maximum-depth cross-check of project records and official sources before proceeding to reduce repeated failed builds. We **HOLD execution of prior M83 UAT** until a low-cost read-only audit completes. Existing M83 script was modified to reject direct running without `M83_REVIEW_APPROVED=YES` (old pasted shell command is external and not modified; do not use it).
- The verified latest checkpoint M82: M77 debug-signed 41.9MB AAB ZIP structure PASS; `base/assets/vkqualitydata.vkq` is sole visible base/assets payload, no cooked Unreal .pak/.ucas/.utoc in base assets, but custom Android Asset Pack modules weren't fully excluded. `M77/Saved/Cooked/Android_ASTC` absent, unlike M70 which had 220 cooked game packages; so the M77 Cook/Stage pipeline remains necessary.
- M78 Android native Shipping compile 0 is genuine; **UAT -build may recompile / generate another debug-signed AAB as an incidental build effect** even without an explicit `-package` flag. Therefore former M83 "NO SIGNING" assertion was overstated. Correct interpretation: explicit distribution-signing step is not requested. Preserve M77 binaries separately if needed before more UAT.
- M77 stage currently contains no confirmed Linux editor module binaries because it was cloned excluding Binaries, and M78 only built Android game. UAT -cook may require host editor binaries and compilation. `-build` may be needed; don't remove without checking the VM and UAT's specific build behavior.
- Reviewed actual GitHub config: `GameDefaultMap=/Game/Maps/TestMap`, `TargetSDKVersion=36`, `bEnableBundle=True`, `bBuildForArm64=True`, `bPackageDataInsideApk=True`; `DefaultGame.ini` packaging `bUseZenStore=False`, but `ProjectVersion=2.2.0.215` is stale vs staged StoreVersion218 and VersionDisplayName2.2.0. Inspect final manifest; do not infer manifest details solely from config text.
- Official sources checked Oct 16: Epic 5.8 [build operations](https://dev.epicgames.com/documentation/unreal-engine/build-operations-cooking-packaging-deploying-and-running-projects-in-unreal-engine?lang=en-US), [packaging cooking](https://dev.epicgames.com/documentation/unreal-engine/packaging-your-project), [Android 5.8 prerequisites](https://dev.epicgames.com/documentation/unreal-engine/android-development-requirements-for-unreal-engine?lang=en-US), [5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes), and Google Play [API36 Aug31 2026](https://support.google.com/googleplay/android-developer/answer/11926878?hl=ar). Epic recommended SDK35 for its tested UE5.8 toolchain while Play currently requires targetSDK36; package compatibility and final manifest must be tested, not assumed from a text setting.
- Created `Scripts/M83A_ReadOnly_Gate_Before_UAT.sh`: validates M63/M77 TestMap byte-identical, project/Engine UAT/Editor Cmd presence, prints public-only release/map config and stages, checks existing Linux Editor binaries, disk/memory. It does no build, network call, signing, secret access, or file mutation. **bash -n locally PASSED**, engine/VM run NOT yet done. The locally executed synthetic empty-home run correctly BLOCKED with `M83A_PROJECT=BLOCKED`.
- **NEXT:** user executes M83A read-only audit on same VM and shares results; interpret Editor binaries, cooked status, stage preflight and disk. Then choose corrected UAT invocation on a PROTECTED separate stage / protect M77 compiled assets before any costly process. Do not repeat M78, regenerate keystores, log secrets, or upload to Play until proper game content, manifest, signed cert and device testing PASS.
