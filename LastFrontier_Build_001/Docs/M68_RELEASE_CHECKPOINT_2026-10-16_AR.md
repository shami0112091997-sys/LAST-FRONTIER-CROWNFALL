# CROWNFALL M68 — سجل التحكم في الإصدار النهائي (16 أكتوبر 2026)

الحالة الحالية: **غير جاهزة للرفع بوصفها النسخة النهائية الحقيقية من Unreal**. هذا المرجع يحفظ قرارات العمل ويكمل M66، دون الكتابة فوق المشروع الأصلي أو تعديل main.

## مصدر الحقيقة
- المستودع الخاص: shami0112091997-sys/LAST-FRONTIER-CROWNFALL
- فرع الاستعادة: m66-smart-recovery
- الخادم الحالي: crownfall-m62-build
- المحرك: $HOME/UE_5.8.3
- أحدث أصول وخريطة M63 مرجعها: $HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001
- ليست كل أصول M63 الثنائية موجودة في GitHub؛ لا تستبدلها بنسخة M60/M65 الأقدم.

## الأخطاء الحقيقية وأولوية حلها

1. **خريطة M60**: في Actions run 37645589203 توقف Cook. السجل يتضمن خطأ Unreal LogLinker Serialization error في Content/Maps/TestMap.umap، FName index 64 خارج المدى [0,44)؛ خرج UnrealEditor-Cmd بالكود 139 ثم UAT بالكود 25. نجاح التجميع لا يلغي ذلك. يجب اختبار تحميل خريطة M63 المستقلة دون تعديل الأصل.
2. **Android**: فشل M60 Android workflow run 37645589208؛ ليس دليلًا على إنشاء AAB حقيقي نهائي.
3. **StreetLamp LOD**: 30,610 مثلثًا، SET_LODS_RESULT=-1، وROLLBACK=PASS. لا تعاد المحاولة قبل تحليل سجلات الاختزال والمكتبة الفعلية. لا تفترض أن تحذير deprecation هو سبب الفشل.
4. **رقم الإصدار**: نسخة إعدادات Unreal في GitHub تستخدم StoreVersion 215، بينما سجل M66 يشير إلى نسخة Google Play سابقة برقم 217. يجب معرفة أعلى رقم موجود في Play Console قبل اعتماد التالي، وأن يكون أكبر منه، مثل 218 فقط إذا كان أعلى رقم بالفعل 217.
5. **توافق الأجهزة**: سجل M66 يشير إلى تحذير Google Play لتوافق الأجهزة بعد v217. لم يحسم.
6. **الأمان والتوقيع**: لا تحفظ ملفات jks أو أسرار GitHub أو Google Cloud أو كلمات المرور أو حسابات الخدمة في المستودع أو المحادثة. تحقق من مطابقة شهادة الرفع المسجلة في Play Console.
7. **قابلية الاستخدام**: يتطلب Android الهاتف الحقيقي (تشغيل، حركة، لمس، إطلاق نار، تصادم، واجهة، معدل إطارات، عدم انهيار) قبل الإصدار. M65 الفحوص النصية ليست تجميعًا فعليًا.

## السياسة الرسمية للتحقق
- API 36 للتطبيقات العادية الجديدة وتحديثاتها منذ 31 أغسطس 2026: https://support.google.com/googleplay/android-developer/answer/11926878
- Unreal Engine 5.8: NDK r27c، Build-tools 35.0.1 وJDK 21.0.3، التوافق مع API 36 يجب إثباته عمليًا لأن توثيق Epic يذكر SDK 35 موصى به: https://dev.epicgames.com/documentation/unreal-engine/android-development-requirements-for-unreal-engine
- اختبار توافق مكتبات الأجهزة مع صفحات 16KB: https://developer.android.com/guide/practices/page-sizes
- توقيع Google Play المعتمد: https://developer.android.com/studio/publish/app-signing
- سياسة الخصوصية وData Safety: https://support.google.com/googleplay/android-developer/answer/10787469
- قد يلزم للحساب الشخصي الجديد 12 مختبرًا لمدة 14 يومًا متصلة للاستخدام الإنتاجي: https://support.google.com/googleplay/android-developer/answer/14151465
- حدود الاستخدام المسموح لـ GitHub Actions وعدم إساءة استخدام الموارد: https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features

## ملفات M68 التي أضيفت إلى الفرع
- Scripts/M68_Release_Preflight_ReadOnly.sh: فحص للموارد والإعدادات وبصمة الخريطة والمحتوى دون تغيير ملفات اللعبة.
- Scripts/M68_Staged_Android_Build.sh: يتطلب موافقة صريحة، ونسخة كاملة في مجلد معزول، ونسخة الإصدار من Play Console، وتوقيعًا محليًا آمنًا، واختبار تحميل الخريطة، ثم Build/Cook/Package حقيقي وفحص AAB و16KB ELF. **لا يرفع إلى Google Play تلقائيًا.**
- Scripts/M67_StreetLampLOD_ReadOnly_Diagnostic.sh: فحص سبب فشل LOD دون تعديل الأصل.

## شروط الترقية إلى نسخة قابلة للرفع
1. نفّذ فحص M68 على الخادم الحقيقي وأكّد سلامة الأصول.
2. حدد السبب الداخلي لـ StreetLamp ثم أصلحه على نسخة اختبار مع نسخ احتياطية فقط، وليس على الأصل قبل التحقق.
3. تأكد من أعلى versionCode في Play Console ومطابقة شهادة الرفع.
4. شغّل فحص تحميل الخريطة بنجاح ثم Compile/Cook/Package على نسخة staging عبر محرك UE المثبت؛ لا تشترِ موارد إضافية أو تكرر عمليات CI الثقيلة بلا ضرورة أو إذن.
5. افحص AAB الناتج بـ bundletool: الحزمة، الإصدار، API 36، Arm64، المكتبات المتوافقة مع 16KB، الصلاحيات غير المقصودة، والتوقيع ومحتوى اللعبة الحقيقي.
6. اجتياز اختبار هاتف Android، وحل تحذيرات توافق Google Play، وسياسة الخصوصية HTTPS وبيانات التواصل وData safety والتصنيف العمري والمختبرين وهوية المطور.
7. لا تنشر إلا بعد اجتياز كل الشروط، وبموافقة صريحة من صاحب المشروع.

**لا يوجد دليل في هذه الجلسة على AAB Shipping Unreal جاهز للرفع.** السجلات السابقة محفوظة كأدلة تاريخية، وهذا المستند نقطة الاستئناف الجديدة.
