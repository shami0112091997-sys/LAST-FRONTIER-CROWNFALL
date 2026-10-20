# CROWNFALL M125 — فحص موحد ودقيق لانهيار النسخة 218

**تاريخ:** 20 أكتوبر 2026  
**الهدف:** تجهيز فحص ثابت للحزمة **الموجودة مسبقًا** على VM، للقراءة فقط، دون توقيع/طبخ/بناء/نشر أو نقل أي ملفات خاصة.

## النتيجة الصادقة حتى الآن

- التثبيت عبر Google Play Internal testing **ناجح**، بينما تشغيل اللعبة يفشل بعد إظهار شعار Unreal، في أقل من ثانية.
- اجتازت الحزمة 218 فحوص التوقيع وبنية AAB وABI و16KB، **لكن هذه الفحوص لا تختبر تشغيل المحرك**.
- يوجد `obbassets` داخل AAB، ومرجع GitHub يحتوي على `DisableEnginePluginsByDefault=true` و`bPackageDataInsideApk=True` دون GooglePAD صريح. **هذه قرائن على احتمال تناقض تهيئة الأصول، لا إثبات أنه سبب الانهيار**؛ يجب فحص M106 الفعلي.
- M119 استخدم `-skipbuild -skipcook` لإعادة استخدام مخرجات طبخ وتجميع سابقة؛ لا يثبت هذا وحده وجود خلل، لكنه يستوجب إعادة بناء وطبخ صحيحين إذا غُيّرت مكونات مؤثرة مستقبلًا.
- لا يحتوي سياق هذه الجلسة على ملف AAB الفعلي أو logcat أو Crash/ANR من الهاتف. لا يُعد تشغيل السكربت على عينات صناعية فحصًا للعبة.

## ما الذي أضفناه في M125؟

البرنامج `M125_CROWNFALL_218_ReadOnly_Diagnostic.py` يقرأ AAB من M106 دون استخراج الملفات، ثم يطبع فقط:

1. تطابق **حجم** الحزمة مع الحجم المقاس سابقًا `117411826` بايت (ليس مقارنة SHA256).
2. عدد وحدات AAB ووجود `obbassets`، وعدد/حجم OBB الداخلي وهل يبدو ZIP.
3. عدد ملفات `classes.dex` وعدد مكتبات `arm64-v8a/*.so`، ووجود سلاسل ثابتة متعلقة بواجهات JNI وGooglePAD في كلا النوعين. **مطابقة النصوص ليست دليلًا على أن الدوال مرتبطة فعليًا**.
4. علم تعطيل Plugins افتراضيًا وظهور GooglePAD في `.uproject` الفعلي، وقيمة `bPackageDataInsideApk`، دون قراءة أو طباعة حقول كلمة المرور.
5. عند وجود `bundletool-all-1.18.3.jar` المعتمد، والتحقق من SHA256، يقرأ Manifest الخاص بـ`obbassets` لتحديد `INSTALL_TIME` أو `FAST_FOLLOW` أو `ON_DEMAND`. إذا لم يجده يطبع `UNAVAILABLE` بدل التخمين.
6. مخرجات تشخيصية ثابتة وبلا مسارات سرية، وتنتهي دومًا بتذكير أن السبب يحتاج **سجل الجهاز**.

**الأمان:** يقرأ فقط، ولا يفتح ملفات التوقيع، ولا يرفع سجلًا، ولا يُشغّل بناء، ولا يزيل ملفات ولا ينشر عبر Google Play. لا تستبدل عليه برنامجًا غير موثوق.

## استخدامه بعد مراجعة الملف ونقله إلى VM

**مكان الحزمة:** `$HOME/crownfall/M106_RELEASE_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab`.

السكربت محفوظ في فرع GitHub المنفصل `m125-218-readonly-audit`. *لا يوجد دليل أنه نُقل إلى VM أو نُفذ عليها*. بعد نقل الملف إلى `$HOME/crownfall/M125_CROWNFALL_218_ReadOnly_Diagnostic.py` بوسيلة آمنة، يمكن تشغيل:

```bash
python3 -m py_compile "$HOME/crownfall/M125_CROWNFALL_218_ReadOnly_Diagnostic.py"
python3 "$HOME/crownfall/M125_CROWNFALL_218_ReadOnly_Diagnostic.py"
```

إن كانت أداة bundletool المعتمدة في مسار مختلف، استخدم فقط المسار الخاص بالملف الذي تم فحص بصمة SHA256 له:

```bash
python3 "$HOME/crownfall/M125_CROWNFALL_218_ReadOnly_Diagnostic.py" \
  --jar "$HOME/tools/bundletool-all-1.18.3.jar"
```

**فحص SHA256 المتوقعة للـJAR** يجري داخل البرنامج، ولا يلزم كشف JKS أو كلمة سر. إذا لم توجد الحزمة أو الـjar يعطي البرنامج نتائج تعبر عن ذلك ولا ينزل شيئًا.

## ماذا نفعل حسب نتيجة الفحص؟

- `M125_ASSET_DELIVERY_MODE=INSTALL_TIME` يعني أن وحدة الأصول مضبوطة للتسليم وقت التثبيت؛ **لا يثبت أن Unreal يستطيع فتحها على الجهاز**.
- `M125_ASSET_DELIVERY_MODE=FAST_FOLLOW/ON_DEMAND` يتطلب مقارنة وقت توفر الأصول مع وقت بداية التشغيل.
- `M125_PACKAGING_HYPOTHESIS=REVIEW_CONFIG_CONSISTENCY` يستحق مراجعة مصدر M106 وإعدادات GooglePAD، **ولا يبرر تعديلًا مباشرًا** دون دليل من Android.
- `M125_NATIVE_PAD_JNI_METHOD=SEEN` مع `M125_DEX_PAD_JNI_METHOD=NOT_SEEN`: راجع أثر `NoSuchMethodError` أو `Failed to find Method` قبل الحديث عن إصلاح. قد لا تكشف طريقة المطابقة النصية بعض الحالات المعقدة.
- لا يوجد سجل تشغيل بعد؟ الخطوة الأكثر مباشرة هي **Google Play Console → Test and release → Testing → Pre-launch report → Stability** أو **Monitor and improve → Android vitals → Crashes and ANRs** مع فلتر النسخة 218. التقرير قد لا يحتوي على crash للمختبر الوحيد، والتأخر لا يعني عدم حدوثه.

## محاذير

- لا تعِد استخدام الإصدار 218 لرفع AAB جديدة. عند ثبوت الإصلاح استخدم رقمًا أعلى وبعد التحقق من الرقم المتاح.
- لا تغير `Vulkan` و`GooglePAD` و`bPackageDataInsideApk` معًا؛ نتيجة إصلاح كهذا لن تكشف السبب الأساسي.
- لا ترسل bugreport/logcat الخام إلى GitHub أو في المحادثة، فقد يضم معلومات هوية وأجهزة وشبكات؛ راجع أول استثناء بعد حذف البيانات الشخصية.
- لا تصف `M125_SYNTHETIC_TESTS=PASS` بأنه نجاح للحزمة الفعلية. لم نصل إلى Android Vitals الخاصة أو VM عبر هذه الجلسة.

## مراجع

- Epic UE 5.8 Google Play Asset Delivery: https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine
- Android asset-pack delivery: https://developer.android.com/guide/playcore/asset-delivery
- Google Play pre-launch report: https://support.google.com/googleplay/android-developer/answer/9842757
- Google Play Android vitals crashes: https://support.google.com/googleplay/android-developer/answer/9859174
- Android logcat: https://developer.android.com/tools/logcat