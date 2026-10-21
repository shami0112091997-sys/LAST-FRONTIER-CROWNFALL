# CROWNFALL M130 — خطة فحص النسخة الأصلية قبل إعادة البناء والنشر الداخلي

**21 أكتوبر 2026. الحالة:** خطة وفحوص قراءة فقط، وليست نسخة Android مبنية أو إصلاحًا مثبتًا.

## 1. نقاط الحسم الفعلية
- Google Play Internal Testing: الإصدار 217 هو المتاح للمختبرين، والإصدار 218 مسودة. الهاتف يعرض versionName 2.2.0 فقط ولا يميز versionCode 217 من 218.
- Android vitals خلال آخر 28 يومًا لا يظهر أخطاء، لكن عدم ظهور التقارير لا يثبت عدم وجود عطل. تقرير Pre-launch غير مولّد في الصور.
- حزمة Unreal Shipping AAB 218 التاريخية حجمها 117411826 بايت في M106 وعلى Cloud Shell، ولم يفحصها هذا الفرع فعليًا.
- المرجع القديم في GitHub لمشروع Unreal يحتوي على DisableEnginePluginsByDefault=true وbPackageDataInsideApk=True، وكانت حزمة 218 تحتوي obbassets؛ لكن إعدادات M106 النهائية قد تختلف، لأنها بلغت StoreVersion=218 بينما مرجع GitHub الأقدم كان StoreVersion=215.
- مجلد CROWNFALL_Stronghold_Android/ مشروع WebView قديم يستخدم **package نفسه** لكنه ليس لعبة Unreal التي نريد إصلاحها، فلا يُستخدم لبناء إصدار حديث.

## 2. أداة M130 المستقلة
تم تجهيز ملف تنزيل مستقل `M130_Actual_AAB_And_VM_Config_ReadOnly.py` مع 20 اختبارًا صناعيًا ناجحًا، وتقرير `M130_PLAN_FOR_WORKING_INTERNAL_TEST_AR.md`. الملف متاح في محادثة ChatGPT كحزمة تنزيل مستقلة؛ **لا تدّعِ أنه نفّذ على VM** ولا أنه مُضمّن في GitHub. يقرأ بنية AAB وملفات المشروع الفعلية، دون قراءة كلمات مرور أو توقيع أو تشغيل بناء.

خطوة تشغيل من Google Cloud Shell بعد رفع ملف Python إلى مجلد HOME:

```bash
gcloud compute ssh crownfall-m62-build \
  --project=project-f1aa4101-551b-4dbe-981 \
  --zone=us-central1-a \
  --command='python3 -' \
  < "$HOME/M130_Actual_AAB_And_VM_Config_ReadOnly.py"
```

النتائج الأساسية: M130_AAB_STATUS، M130_AAB_SHA256، M130_SOURCE_VERSION_CODE، M130_GOOGLEPAD_PROJECT_PLUGIN، M130_PACKAGE_DATA_INSIDE_APK، M130_GOOGLEPAD_SETTING_ENABLED، M130_OBBASSETS_MODULE، M130_OBB_ASSET_BYTES، M130_REVIEW_CODE.

يمكن مقارنة بصمة AAB الموجودة أصلًا على Cloud Shell بتشغيل أداة M130 هناك باستخدام `--aab "$HOME/CROWNFALL_218_Release_Signed.aab"`. لا تُكتب أي نسخة على VM عند استخدام stdin.

## 3. إصلاح مرشح بحسب نتيجة الفحص، لا قبلها
A: عند إثبات تعارض GooglePAD مع obbassets، استخدم مرشح GitHub المنفصل `m128-googlepad-delivery-candidate-only`: فعل GooglePAD في .uproject، bEnablePlugin=True، bPackageDataInsideApk=False. وثائق Epic 5.8: https://dev.epicgames.com/documentation/unreal-engine/using-google-play-asset-delivery-in-unreal-engine

B: إذا تقرر التغليف الداخلي دون PAD بعد فحص الحجم والتوافق، فهذه تجربة ثانية مستقلة، ولا يُخلط التعديلان. وإذا أشار سجل الإقلاع إلى Vulkan/RHI أو native linker أو SIGSEGV فحلّل الاستثناء أولًا بدل تعديل PAD افتراضًا.

C: M129 إصلاح حركة الأعداء المستقل؛ لا تدمجه أثناء تجربة علاج الإقلاع إلا بعد اختبار العطل.

## 4. شروط إعداد إصدار تجريبي صالح
1. افحص حقيقة M106 وAAB الأصلية وقارن SHA مع نسخة Cloud Shell وحدد سبب الانهيار بأقرب دليل من logcat أو Play.
2. احتفظ بـM63 وM84 وM106 وTestMap الأصلية وJKS الخاصة. لا تُنسخ أي Config من GitHub مباشرة إلى M106 لوجود StoreVersion أقدم وحقول توقيع خاصة.
3. جهز Sandbox جديدًا وطبّق تعديلًا واحدًا فقط، ثم Build + Cook + Stage + Package كامل (UE 5.8.3، Android ASTC، arm64، Shipping/Distribution) دون الاعتماد على `-skipbuild -skipcook` بعد تغييرات الملحقات أو الإعدادات.
4. اختر versionCode جديدًا أعلى من آخر رقم مستخدم أو مرفوع؛ 219 مجرد مثال ويجب التحقق من توفره. التوقيع بمفتاح رفع Play نفسه دون إفشاء JKS أو كلمات المرور.
5. تحقق باستخدام bundletool من package/versionCode/ABI/SDK/assets/16KB alignment ومن وجود TestMap، ثم اختبر تشغيل اللعبة على Android حقيقي أو بيئة اختبار موثوقة وصولًا إلى اللعب مدة 3 دقائق على الأقل.
6. **Google Play Internal Testing فقط** بعد نجاح الشروط. لا نشر إنتاجي ولا اختبار مفتوح تلقائيًا.

## 5. الحدود
هذه الخطة لم تُعد بناء اللعبة أو تتصل بـVM/Play Console/هاتف المستخدم، ولم تفحص الـAAB الحقيقية. لا سبب انهيار مثبت حتى وصول السجل أو فحص الحزمة. لا تغيّر `main` أو `m66-smart-recovery` ولا تستخدم GitHub Actions دون إذن مستقل.

مصادر: https://support.google.com/googleplay/android-developer/answer/9842757 و https://support.google.com/googleplay/android-developer/answer/9859174 و https://support.google.com/googleplay/android-developer/answer/9845334 .
