# CROWNFALL M123 — تحقيق العطل الفعلي بعد شاشة Unreal

**المصدر:** مشروع GitHub المرجعي وفرع M121/M122، شهادات فحوص الإصدار 218 السابقة، ووثائق Epic/Android.  
**الحالة:** أدوات تحقيق للقراءة فقط؛ لم يحصل فحص على سجل هاتف المستخدم، ولم يجرِ تعديل Unreal أو بناء أو نشر أي إصدار.

## الملخص التنفيذي
- الإصدار \`com.crownfall.stronghold\` / \`versionCode=218\` تم بناؤه Shipping وتوقيعه، ونجحت البنية و16KB وManifest، ووصل إلى قناة Google Play للاختبار الداخلي وثُبّت. **عند فتحه على الهاتف يظهر شعار Unreal ثم يغلق في أقل من ثانية**.
- هذه ليست شهادة بأن كود اللعبة أو الخرائط أو العرض يعمل؛ نجاح التوقيع و\`bundletool validate\` لا يشخص أعطال وقت التشغيل.
- **السبب الجذري غير مثبت؛ نحتاج على الأقل تصنيفًا موثوقًا لسبب خروج العملية وآخر stack trace.**
- لا تحذف اللعبة أو بياناتها ولا تعدّل أو تعيد تدوير مفاتيح التوقيع ولا تعِد البناء بالإصدار 218. الاختبار التالي، عند ثبوت حل، يحتاج إصدارًا أعلى (مثل 219 إذا لم يُستخدم).

## مقارنة الأدلة وأولويات الفحص

| الاحتمال | الدليل المحدد | ما يمكن استنتاجه الآن |
|---|---|---|
| تحميل Google Play assets / OBB | \`obbassets/assets/main.obb.png\` داخل 218؛ مرجع المشروع يضبط \`bPackageDataInsideApk=True\` و\`DisableEnginePluginsByDefault=true\` بلا إدراج GooglePAD | **أولوية مرتفعة للفحص**؛ لا دليل أن المحتوى غائب على الجهاز، ولا أن إعداد M106 يطابق المرجع حرفيًا |
| فشل Java/JNI أثناء بدء Unreal/GooglePAD | مثال موثق في مجتمع Epic: \`Failed to find Method\` بعد splash عند استعمال PAD | مؤشر قابل للبحث فقط؛ المثال قديم في UE4، لا يثبت خطأ UE5.8.3 |
| مكتبة أو C++ | \`FATAL EXCEPTION\`, \`dlopen failed\`, \`SIGSEGV\`, \`SIGABRT\` | يحتاج crash buffer أو stack trace من الجهاز |
| Vulkan/RHI | \`bSupportsVulkan=True\` في المرجع | لا نوقف Vulkan حتى يتوفر \`VK_ERROR\` أو أثر RHI |
| TestMap / pak/shader | وجود TestMap المطبوخ مثبت، ولكن لم تظهر اللعبة بعد splash | Cook ناجح لا يثبت فتح TestMap أو تركيب pak على الهاتف |
| إنهاء نظام/ذاكرة بدل استثناء | التطبيق يعود إلى Android بسرعة | لا نميز هذه الحالة دون \`ApplicationExitInfo\` أو سجلات النظام |

### ملاحظة مهمة بشأن المصدر
هناك مساران Android في المستودع: **مشروع Unreal \`LastFrontier_Build_001\`** وتطبيق Android WebView منفصل \`CROWNFALL_Stronghold_Android\`. النسخة 218 التي رأينا شاشة Unreal لها جاءت من BuildCookRun ضمن M106؛ **لا نعزو عطلها إلى MainActivity الخاص بمشروع WebView**. يجب ألا نخلط بينهما في أي إصلاح.

## التحقق من أصول الحزمة دون تعديل

استخدم \`M122_AssetPack_Delivery_Audit_ReadOnly.py\` الموجود في فرع التشخيص على **VM** الذي يحتفظ بحزمة M106 الأصلية (ليس AAB محلية أخرى). يفحص:
- manifest الفعلي لوحدة \`obbassets\`: \`INSTALL_TIME\` أم \`FAST_FOLLOW\` أم \`ON_DEMAND\`.
- وجود حزمة أصول OBB داخل AAB.
- إعداد Android/\`.uproject\` المرجعي في M106، ولا يطبع أسرار التوقيع.

**تفسير النتائج:** \`INSTALL_TIME\` يثبت *نمط التوزيع* فقط ولا يثبت قدرة محرك Unreal على العثور على الأصول أو فتحها. \`FAST_FOLLOW\` أو \`ON_DEMAND\` يجعل توفر الأصول في أول ثانية بحاجة إلى فحص إضافي. أي تعارض بين الإضافة و\`bPackageDataInsideApk\` يستحق الإصلاح **فقط بعد مقارنة إعدادات M106 والسجل**.

## الخطوة الحاسمة: دليل التعطل من الجهاز

**أولًا (بدون ADB):** Google Play Console → CROWNFALL → Monitor and improve → Android vitals → Crashes and ANRs → فلتر الإصدار \`218\` → View details. إن توفر Pre-launch report → Stability فافتح تفاصيل أي فشل. عدم وجود تقرير قد يعني أن بيانات المختبر قليلة أو لم تصل بعد، ولا يعني أن اللعبة تعمل.

**ثانيًا (إذا لم تتوفر بيانات Play):** على Android 11+ يمكن استخدام جهاز/بيئة ADB موثوقة لقراءة مخزن الأعطال:
\`\`\`bash
adb logcat -b crash -d -v threadtime
\`\`\`
وقد تحتاج أيضًا إلى \`adb logcat -b main,system -d -v threadtime\` إذا خرج التطبيق دون crash مسجّل. **لا ترفع السجل الخام ولا bugreport كاملًا**؛ فكلاهما قد يحتوي تفاصيل شخصية أو رموزًا حساسة. أبقِه محليًا، وأدخل مقتطفًا منفصلًا في أداة M123 دون نشره.

**أداة M123**: \`M123_Private_Android_Exit_Triage_ReadOnly.py --input=/path/to/private-relevant-log.txt\`؛ تتطلب ملفًا خاصًا (مثل mode 600)، تقرأ النص ولا تغيّره، وتطبع *عدد علامات* JNI/Java/Native/PAD/Graphics/Memory فقط، **دون الأسطر أو المسارات أو المعرفات**. لا تستخدم نتيجة عد الكلمات وحدها كدليل سبب. اختبارها الاصطناعي لا يختبر التطبيق نفسه.

**قراءة أول stack:** إذا أشار الاستثناء إلى \`Failed to find Method\` أو \`NoSuchMethodError\`، راجع دمج Java/UPL لإضافة GooglePAD والـGradle الناتج داخل M106 مع المحافظة على سرية الملفات. إذا أشار إلى \`No OBB found\` أو \`PakFile\`، راجع وقت/طريقة توفر الأصول وفتحها. إذا أشار إلى \`SIGSEGV\`، افحص الرموز المطابقة لبناء 218 قبل إصلاح C++؛ إن كان \`VK_ERROR\` راجع دعم الهاتف وبدائل RHI. لا تُجر تعديلات متزامنة لهذه الأسباب المحتملة.

## سلامة الحساب والمشروع
- فرع العمل الجديد \`m123-evidence-first-diagnostics\` منفصل عن \`main\` وعن \`m66-smart-recovery\` ونسخة VM M106. الملفات الجديدة تشخيصية فقط.
- لا تشغيل GitHub Actions أو Gradle/UAT، ولا تغيير TestMap أو بيانات المتجر أو إضافة مختبرين، ولا نسخ JKS/كلمة المرور إلى GitHub.
- إذا تأكدت مشكلة محددة، أنشئ نسخة **تشخيصية منفصلة** بتعديل واحد قابل للتراجع؛ نفّذ Build/Cook كاملين عند تغيير الأصول أو إعدادات تؤثر على الطبخ، ولا تعتمد على \`skipcook\` بلا دليل. افحص AAB جديدة وجرّب تشغيلها محليًا قبل رفع نسخة أعلى من 218.

## مراجع
1. Epic UE 5.8 GooglePAD: https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine
2. Android install-time and fast-follow: https://developer.android.com/guide/playcore/asset-delivery/integrate-native
3. Google Play crash reports: https://support.google.com/googleplay/android-developer/answer/9859174
4. Android logcat buffers: https://developer.android.com/tools/logcat
5. Community case (context, not evidence for current crash): https://forums.unrealengine.com/t/google-play-asset-delivery-crash-after-splash-screen/210162
6. Android application exit reasons: https://developer.android.com/about/versions/11/features

**نقطة الاستئناف:** اطلب صورة Android vitals لقسم Crashes and ANRs أو نتيجة فحص M122 على VM. **لا يمكن الجزم بالسبب دون سجل الجهاز**.
