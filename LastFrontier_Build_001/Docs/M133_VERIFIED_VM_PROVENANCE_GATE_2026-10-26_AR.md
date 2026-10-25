# M133 — CROWNFALL: بوابة تشخيص أصل الخريطة وحزمة Android 218
**26 أكتوبر 2026 بتوقيت قطر**  
**الفرع الآمن:** `m133-v218-provenance-readonly` ← `m132-ci-source-audit-only`.

## النتيجة الفعلية المتحققة الآن
- أنشئت أداة قراءة فقط `Scripts/M133_VM_Map_AAB_Provenance_ReadOnly.py` تقارن خرائط M63/M84/M106، وتحدد تطابق بصمتها مع الخريطة التي فشل Cook فيها في تشغيل GitHub **37645589203** (7 أكتوبر).
- تفحص الأداة أيضًا **فهرس ZIP** لملف AAB الأصلي في M106 دون استخراج المحتوى: `BundleConfig.pb`، `base`، `obbassets`، `classes.dex`، `arm64-v8a/*.so` وملفات `.obb/.obb.png`.
- أُضيفت **13 حالة اختبار اصطناعية** لأداة M133، إضافة إلى **7 اختبارات M131**.
- **GitHub Actions run 40240803373: SUCCESS — 20/20 tests PASS**، بجانب فحص Python syntax. تمت مراجعة سجلات خطوات Workflow، وليس الاكتفاء بواجهة النجاح.
- رابط الاختبار: https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/40240803373
- في الفرع الموروث من M132 لا تزال بوابة المصدر تظهر **0 أخطاء بنيوية قاطعة و5 تنبيهات مراجعة**، بينها مشكلة خريطة GitHub القديمة، عدم مطابقة رقم الإصدار، ووجود مسار WebView القديم.
- **لم يتم تشغيل الأداة على خادم Google Cloud الأصلي**، لأن موصل GitHub لا يمنح اتصالاً إلى VM، ولم تكن أصول AAB 218 الأصلية أو الخرائط M84/M106 متاحة في المستودع أو ملفات مكتبة المحادثة. لا يوجد تكامل Google Cloud Compute Engine صالح لتشغيل أوامر على VM من هذه الجلسة. لا تُسجّل مقارنة حقيقية بين M84/M106/GitHub بغير تشغيل الأداة على VM.

## البصمة التاريخية المستقلة
- التشغيل الأصلي: https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/37645589203
- خطأ Unreal: `FName index 64 outside the valid range [0, 44)` في `Content/Maps/TestMap.umap`، وانتهى الأمر بـ `Error_UnknownCookFailure (25)`.
- بصمة Git blob للملف نفسه في commit ذلك التشغيل وفي M132/M133: `965b78fc071c21412f966b70712eb30724799c20`.
- سجلات M85/M86 في المصدر المرجعي المحفوظ توثق أن **البيئة المنفصلة M84** استطاعت لاحقًا تحميل خريطتها وCook نحو 220 حزمة بدون أخطاء. لذلك لا يجوز استبدال خريطة M84 بملف GitHub الفاشل أو الادعاء أنها مطابقة له بلا مقارنة على VM.

## فرضيات العطل 218 التي لا تزال مفتوحة
1. تكامل Java/GooglePAD/JNI والاختلاف بين `GameActivity` ودوال C++ بعد `DisableEnginePluginsByDefault`.
2. طريقة وصول Unreal للمحتوى داخل `obbassets` في تثبيت `install-time` (الوحدة ظاهرة في Play لا يعني نجاح mount/asset read).
3. تحميل الـ `.so` أو shader/RHI/Vulkan.
4. الاستدعاءات الأصلية وCrash في كود المحرك أو الذاكرة.
5. اختلاف الحزمة الفعلية المُثبّتة عن الإصدار 218 الذي فُحص في App Bundle Explorer.
6. مطابقة خريطة `TestMap` والأصول المطبوخة بين M106 وM84 وGitHub.

**كل هذه فرضيات.** تحتاج دليل من AAB الأصلية وسجل فشل تشغيل Native/Java قبل نسب السبب.

## تشغيل M133 قراءة فقط على VM الأصلية — إذا أصبحت متاحة

مهم: يجب أن يكون ملف `M133_VM_Map_AAB_Provenance_ReadOnly.py` من الفرع M133 موجودًا في مجلد مؤقت على VM. لا تعدل `M63_REAL_MOBILE` أو `M84_EDITOR_SANDBOX_v218` أو `M106_RELEASE_SANDBOX_v218`. يعمل Python 3 بدون بناء أو توقيع أو امتيازات إدارة.

```bash
python3 /path/to/M133_VM_Map_AAB_Provenance_ReadOnly.py
```

للتحليل العميق الاختياري لـ JNI: انسخ أيضًا سكربت `M126_GooglePAD_Dex_Method_Audit_ReadOnly.py` إلى نفس مجلد البرنامج المؤقت، ثم:

```bash
python3 /path/to/M133_VM_Map_AAB_Provenance_ReadOnly.py --scan-jni
```

سيقرأ افتراضيًا:
- `$HOME/crownfall/M63_REAL_MOBILE/LastFrontier_Build_001/Content/Maps/TestMap.umap`
- `$HOME/crownfall/M84_EDITOR_SANDBOX_v218/Content/Maps/TestMap.umap`
- `$HOME/crownfall/M106_RELEASE_SANDBOX_v218/Content/Maps/TestMap.umap`
- `$HOME/crownfall/M106_RELEASE_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab`

**شكل النتيجة:** رموز `M133_*` ومقارنة EQUAL/DIFFERENT وتحذير `HISTORIC_BAD_GITHUB_BLOB=YES/NO`، ووحدة `obbassets` والعدادات. لن يطبع محتوى الخريطة، أو مفاتيح JKS، أو كلمات المرور، أو المسارات المطلقة؛ لا يقرأ أصلًا الملفات السرية.

**تمييز مهم:** نجاح `M133_RESULT=STRUCTURAL_AUDIT_COMPLETE` هو نجاح مراجعة البنْية فقط، **ليس** إثبات Compile/Run، ولا شهادة سلامة كاملة للـAAB، ولا دليل معرفة سبب الانهيار.

## بوابة القرار
- لو `M84_HISTORIC_BAD_GITHUB_BLOB=NO` و`M106_MAP` مساوية لـM84: استمر بالاعتماد على خريطة VM، وتحقق من أصل AAB 218 ومحتويات `obbassets`.
- لو `M84_HISTORIC_BAD_GITHUB_BLOB=YES`: لا تستخدمها في بناء جديد قبل اختبار تحميل/Cook على نسخة منفصلة؛ لا تمس النسخة الأصلية.
- لو `M106_MAP` تختلف عن M84: راجع أصل الملفات وأزمنة التجميع (بدون نسخ أو استبدال تلقائي).
- لو `AAB_OBBASSETS_MODULE=NO` أو `AAB_INSTALL_PACK_OBB_COUNT=0`: أوقف اعتماد الحزمة حتى تفسير الفرق عن لقطة Play.
- لو تحليل JNI أعطى REVIEW: قارنه بالـDEX الفعلي و`GameActivity`؛ لا تنشر ترقيعًا مبنيًا على تطابق أسماء فقط.

## إجراءات لم تحدث
- لم أصل إلى Google Cloud VM، ولا Google Play Console، ولا هاتف المستخدم.
- لم يجر أي بناء Unreal أو Android، ولا فحص تشغيل فعلي للإصدار 218.
- لم أعدّل `main`, `m66`, `m128`, `m131`, `m132`، ولم أقرأ JKS أو كلمات مرور أو أرفع تطبيقًا.
- كُتبت أدوات/اختبارات/Workflow توثيقية وتشخيصية فقط على فرع M133.

## المراجع
- Epic Unreal Engine 5.8 GooglePAD: https://dev.epicgames.com/documentation/unreal-engine/using-google-play-asset-delivery-in-unreal-engine
- Android PAD native install-time assets: https://developer.android.com/guide/playcore/asset-delivery/integrate-native
- Epic Unreal Engine 5.8 Android toolchain: https://dev.epicgames.com/documentation/unreal-engine/android-development-requirements-for-unreal-engine
