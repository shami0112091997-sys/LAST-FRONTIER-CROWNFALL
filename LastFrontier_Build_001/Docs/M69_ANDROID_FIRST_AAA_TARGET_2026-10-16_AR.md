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
