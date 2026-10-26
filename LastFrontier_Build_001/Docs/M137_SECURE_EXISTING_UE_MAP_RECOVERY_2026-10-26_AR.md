# M137 — استعادة خريطة CROWNFALL بطريقة آمنة ومتحقق منها آليًا

**التاريخ:** 26 أكتوبر 2026 (قطر)  
**فرع العمل المعزول:** `m137-secure-map-recovery` ← `m136-isolated-unreal-map-recovery`.  
**نتيجة الاختبار:** [GitHub Actions 40282881624](https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/40282881624) — **SUCCESS، 53/53 اختبارات Python**، وخطوات الأمان وكشف الخريطة الفاشلة ناجحة.

## نتيجة المراجعة العميقة

- **الملف المعيب:** `LastFrontier_Build_001/Content/Maps/TestMap.umap` داخل GitHub ما زال يحمل Git blob SHA-1 `965b78fc071c21412f966b70712eb30724799c20`. فشل سابقًا في تشغيل Unreal 5.8 الحقيقي [37645589203](https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/37645589203)، خطأ `FName index 64 out of [0,44)`، `ExitCode 25`.
- **مراجعة أرشيف M65 المحفوظ بالمكتبة:** `CROWNFALL_M65_UNREAL_SOURCE_RELEASE_CANDIDATE.zip` يحتوي مصدر C++ وسكربت `create_testmap_in_unreal.py` و`prepare_testmap_ue58.sh`، لكنه **لا يحتوي على خريطة ثنائية جاهزة**. بل يحتوي `Content/Maps/README_MAP_NOT_INCLUDED_AR.txt` الذي يوضح غياب الخريطة. وأكد فحص ملفات M62 السابقة في المكتبة غياب `.umap` كذلك.
- **ثغرة في أداة M136 قبل الإصلاح:** كان `shutil.copytree` ينسخ المشروع كاملًا مع استثناء امتدادات بسيطة؛ هذا قد يسحب ملفًا خاصًا باسم غير متوقع، أو يتبع روابط رمزية خارج مساحة المشروع، أو ينسخ أسرارًا في ملفات INI.
- **خطوة M65 التاريخية كانت تعتبر أي ملف خريطة غير فارغ قابلًا للحفظ دون اختباره**؛ لذلك لا يمكن استخدامها على نسخة GitHub المعروفة بالفشل من دون فحص OID صريح.
- **لا توجد في المكتبة المتاحة حزمة Unreal AAB 218 الأصلية بحجم 117,411,826 بايت، أو خريطة M84/M106 الثنائية الموثوقة**. ملفات AAB القديمة الصغيرة هي إصدار WebView، وليس إثبات صلاحية Unreal. الخادم الحقيقي غير متصل بهذا الحوار.

## تعديلات مطبقة ومحفوظة على M137 فقط

1. **`Scripts/M136_Isolated_Map_Sandbox.py`**: ألغيت نسخ المشروع على إطلاقه وأضفت قائمة تسمح فقط بكود المصدر `.cpp/.h/.cs/.inl/.ush/.usf`، ملفات إعدادات محددة بعد رفض مفاتيح التوقيع/كلمات المرور الحساسة، تعريف المشروع، الخريطة المعروفة الفاشلة وسكربت الإنشاء. تُرفض الروابط الرمزية أو الملفات الثنائية غير المتوقعة داخل Source. كل العمليات داخل Sandbox جديد مستقل؛ تبقى الخريطة الأصلية محفوظة حرفيًا.
2. **`Scripts/M136_Create_TestMap_In_Unreal.py`**: بعد الإنشاء والحفظ داخل Unreal Editor يجب الآن نجاح `LevelEditorSubsystem.load_level` وإظهار علامتي `CROWNFALL_M137_UE_TESTMAP_EDITOR_RELOAD=PASS` و`CROWNFALL_M136_UE_LEVEL_GENERATED=PASS`. هذه العلامات لم تظهر بعد من Editor حقيقي.
3. **`Scripts/M136_Isolated_Map_Sandbox.py finalize`**: يرفض استكمال الإجراءات إن لم توجد علامتا الحفظ وإعادة التحميل، أو ظهر خطأ Fatal/Assertion. ثم يعيد إعدادات المشروع المؤقتة فقط، مع بقاء شرط Cook الفعلي مطلوبًا. سجلات نصية فقط ليست برهانًا تشفيريًا على التنفيذ؛ لا تعتبر النتيجة الجاهزة إفادة تشغيل.
4. **`Scripts/M137_Run_UE58_Map_ExistingEngine_Only.sh`**: مشغّل Linux لبيئة تحتوي مسبقًا على محرر Unreal 5.8. يتحقق من `Engine/Build/Build.version` ووجود `UnrealEditor` و`Build.sh` ومساحة Sandbox جديدة، ويمنع التشغيل دون واجهة Xvfb/Display. ينفذ `-ExecutePythonScript` داخل Sandbox بمهلة 900 ثانية ثم يفحص مخرجات Editor ويستدعي finalize. **لا ينزّل المحرك ولا يطبخ Android ولا يستخدم JKS ولا يرفع شيئًا إلى Play.** لم يُشغّل هذا المشغّل مع Unreal حقيقي بعد.
5. **الاختبارات:** وسعت `test_M136_isolated_unreal_map.py` بحالات أمنية إضافية (روابط رمزية، ملفات سرية، ملفات Source غير متوقعة، غياب علامة إعادة التحميل، ووجود fatal). أضفت `test_M137_mock_unreal_editor.py` الذي ينفذ **7 حالات محاكاة فعلية لواجهات Python في Unreal** في بيئة وهمية، بما فيها فشل إنشاء خريطة أو لاعب أو الحفظ أو إعادة التحميل.
6. **`.github/workflows/m137-secure-map-preflight.yml`**: فحص مجاني قصير تلقائي عند كل Push على M137؛ `contents: read` فقط، دون محرك Unreal أو بيانات خاصة.

## أدلة الاختبار المقاسة

- أول محاولة M137 للـCI [40282575822](https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/40282575822): فشل في تفسير YAML بسبب `:` غير مقتبسة في عنوان خطوة؛ **أصلحتها**.
- المحاولة الثانية [40282677449](https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/40282677449): **46/46 اختبارًا ناجحًا**، وفحص نسخ القائمة البيضاء ناجح.
- **آخر تشغيل [40282881624](https://github.com/shami0112091997-sys/LAST-FRONTIER-CROWNFALL/actions/runs/40282881624): SUCCESS، 53/53 اختبارًا ناجحًا**، مع نجاح:
  - `M137_PYTHON_AND_BASH_SYNTAX=PASS`
  - `M137_ISOLATED_ALLOWLIST_AND_ORIGINAL_PROTECTION=PASS`
  - `M137_ENGINE_MISSING_NO_DOWNLOAD_OR_SANDBOX_MODIFICATION=PASS`
  - `M137_HISTORIC_BAD_MAP_BLOCK=PASS`

## ما لم يتم ويمنع إصدار APK/AAB

- لا يوجد Unreal Engine 5.8 مثبّت داخل هذه الجلسة، ولا وصول موصل إلى خادم Google Cloud القائم الذي يحمل M84/M106؛ لذلك **لم يحدث UE Editor load فعلي أو Compile أو Cook أو Package**.
- لم تحصل تجربة إقلاع Android أو تثبيت حزمة asset-pack أو تحليل stack trace للنسخة 218. **سبب انهيار 218 غير مثبت، ولا نزعم أنه أصلح.**
- حتى نجاح محرر Unreal في توليد وإعادة تحميل خريطة جديدة ليس إثباتًا لكفاية خريطة الأصل M84 أو توافق اللعبة مع Android؛ يتطلب Cook/تجربة تشغيل.
- تشغيل M60 سابقًا دام قرابة ساعة وانتهى بفشل الخريطة. GitHub Actions للمستودعات الخاصة له حصص مجانية، والفائض قد يكون مدفوعًا؛ لم يتم تشغيل تنزيل/بناء Unreal ثقيل جديد من غير معرفة الرصيد.

## المسار الواقعي عندما تتوفر بيئة UE5.8 موجودة بالفعل

```bash
bash LastFrontier_Build_001/Scripts/M137_Run_UE58_Map_ExistingEngine_Only.sh \
    /path/to/cloned/repo \
    /path/to/EXISTING/UnrealEngine-5.8 \
    /path/to/NEW/isolated-sandbox
```

هذا **لا يستبدل خريطة M84 الأصلية**، ولا يستخدم نسخة GitHub الفاشلة في إنتاج الإصدار. الخطوة التالية بعد النجاح يجب أن تكون Editor load ثم Cook لأصول Android وحزمة جديدة ورقم إصدار Play غير مستخدم، وبعد ذلك اختبار فعلي مستقل.

## المصادر الرسمية
- Epic UE5.8 Python Editor scripting و`-ExecutePythonScript`: https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python
- Epic `LevelEditorSubsystem.new_level/load_level`: https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/LevelEditorSubsystem
- GitHub Actions billing: https://docs.github.com/en/billing/concepts/product-billing/github-actions

**حالة الأمان:** `main`، `m66`، `m128`، بيئات M84/M106، التوقيع وجوجل بلاي بلا تغييرات؛ كل التصحيحات على M137 المعزول فقط.
