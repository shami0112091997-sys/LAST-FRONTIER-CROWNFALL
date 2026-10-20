# CROWNFALL — M126: فحص تعاريف Java الفعلية مقابل طلبات GooglePAD في Unreal

**التاريخ:** 20 أكتوبر 2026 — **حالة البحث:** تحديث تشخيصي مستقل، لا إعادة بناء ولا نشر ولا تعديل التطبيق.

## لماذا M126 أهم من البحث النصي في M124/M125؟

الفحوص السابقة كانت تكتفي بالعثور على نصوص مثل `AndroidThunkJava_GooglePAD_Available` داخل `libUnreal.so` و`classes.dex`. مجرد ظهور النص داخل ملف DEX **ليس دليلًا** أن الدالة معرّفة فعلًا في كلاس Java؛ فقد يكون اسمًا في جدول strings أو مرجعًا إلى دالة خارجية. كذلك ظهورها في مكتبة Native لا يثبت تنفيذ `FindMethod` في هذا المسار.

بنيت أداة مستقلة **M126_GooglePAD_Dex_Method_Audit_ReadOnly.py** تفحص داخل حزمة AAB الأصلية:

1. تسحب أسماء دوال `AndroidThunkJava_GooglePAD_*` المرجعية من مكتبات Android `arm64-v8a` الأصلية، دون استخراج ملفات القرص أو تعديلها.
2. تتحقق من تنسيق DEX و`string_ids`, `type_ids`, `method_ids`, `class_defs` و`class_data_item` باستخدام قارئ حدود آمن، بدل قبول النص الظاهر فقط.
3. تميّز بين عدد أسماء دوال GooglePAD المطلوبة في المكتبات، وعدد الأسماء المقابلة في جدول `method_ids`، وعدد **تعريفات الدوال في class_data**، وعدد التعريفات التابعة لكلاسات `GameActivity` أو `GameApplication`، وفحصًا خاصًا لتوقيع `AndroidThunkJava_GooglePAD_Available()Z` التاريخي (دون معاملات، وقيمة منطقية) داخل هذه الكلاسات إن كان الاسم موجودًا.
4. تصنف الفروق بحسب الدرجة: إذا وجدت مكتبة أصلية تطلب اسم دالة GooglePAD لا يظهر تعريفها في DEX، فهذه **قرينة قوية على تعارض واجهة JNI**، لكنها ليست دليلًا قطعيًا على أن التطبيق انهار بسببها: قد يكون الاسم غير مستخدم فعليًا، أو قد تكون الدالة ديناميكية أو في كلاس آخر أو هناك فرق في توقيع الدالة.
5. **لا تتأكد الأداة من تطابق توقيع JNI (`(…)Z` مثلًا)** ولا تطبق ABI/Play policy validation؛ حتى تطابق الأسماء والتعاريف أو توقيع `()Z` المحدد لا يغني عن `logcat`، ولا يثبت مسار التنفيذ.

تُطبع عدادات وحالات ثابتة فقط، بلا كلمات سر ولا مسارات ملف المستخدم ولا بيانات هاتفه؛ لا تُفتح JKS أو ملفات تكوين سرية أو `logcat`.

## مخرجات الفحص إذا شغّل على حزمة 218 الفعلية

- `M126_NATIVE_PAD_METHOD_REFERENCES`: أسماء دوال GooglePAD الظاهرة في المكتبات الأصلية.
- `M126_DEX_MATCHED_METHOD_IDS`: عدد أسماء الطلب الموجودة في جدول DEX.
- `M126_DEX_MATCHED_CLASS_METHOD_DEFINITIONS`: عدد الأسماء التي لديها **تعريف class_data فعلي**، وليس اسمًا عائمًا.
- `M126_DEX_GAME_ACTIVITY_METHOD_DEFINITIONS`: عدد الأسماء نفسها المعرفة ضمن `GameActivity` أو `GameApplication`، بعد قراءة نوع الكلاس من `type_ids`.
- `M126_DEX_AVAILABLE_NOARGS_BOOL_DEFINITION`: فحص محدد لتوقيع `()Z` المعروف من عطل قديم؛ لا يعني تطابق بقية تواقيع JNI.
- `M126_MISSING_CLASS_METHOD_DEFINITIONS`: عدد أسماء الطلب في native التي لم يُعثر لها على تعريف مقابل في DEX المضمّن.
- `M126_ASSESSMENT`: تحذير مراجعة، أو وجود تعريفات ثابتة مع توقيع غير متحقق، أو عدم وجود إشارات GooglePAD مرجعية.
- `M126_CRASH_CAUSE=UNCONFIRMED_REQUIRES_DEVICE_STACK_TRACE`: ثابت دائمًا؛ لا تختلط النتيجة الثابتة مع خطأ التشغيل الحقيقي.

**كل هذه المتغيرات لم تُقَس على لعبة CROWNFALL الفعلية بعد.** اختبارات الوحدة استخدمت 14 حالة DEX مصطنعة ناجحة، من بينها اسم موجود في `string_ids` دون تعريف Java، ومرجع في `method_ids` دون `class_data`، وحزمة DEX سليمة ظاهريًا لكنها غير قابلة للتحليل. وهي اختبار منطق الأداة، وليست شهادة نجاح للعبة.

## النقل الآمن إلى خادم M106 لاحقًا

المشروع الفعلي والحزمة محفوظان على VM `crownfall-m62-build`؛ عندما تتاح جلسة Google Cloud Shell خاصة وموثوقة، انقل **ملف Python فقط** من فرع التشخيص أو من حزمة ZIP المرفقة إلى VM (لا حاجة لنقل AAB أو JKS). بعد المراجعة نفذ داخل VM:

```bash
python3 -m py_compile "$HOME/crownfall/M126_GooglePAD_Dex_Method_Audit_ReadOnly.py"
python3 "$HOME/crownfall/M126_GooglePAD_Dex_Method_Audit_ReadOnly.py"
```

البرنامج يستخدم تلقائيًا مسار AAB الخاص بـM106؛ إن غابت يوقف الفحص، ولا يبحث عن إصدار آخر عشوائيًا. رمز الخروج 0 يعني انتهاء الفحص دون قرائن عدم تطابق أسماء، **لا** نجاح التشغيل؛ 3 يشير إلى احتمال تعارض أو ملفات مفقودة، و2 إلى ملف غير صالح أو قراءة غير مكتملة. لا تنفذ build أو `gradle` أو `gcloud compute scp` للحزمة الخاصة لأغراض هذه المرحلة؛ لا يوجد مبرر لذلك.

## ترتيب الأهمية عند توفر البيانات

1. **الأكثر حسمًا:** Google Play Console → Test and release → Testing → Pre-launch report → Details → Stability، ثم استثناء/stack trace الإصدار 218. إذا لم يُنتج التقرير نتيجة، Android vitals → Crashes and ANRs، أو سجل crash من الجهاز بعد تنقيح البيانات الخاصة.
2. **أفضل تدقيق ثابت متاح الآن على VM:** M125 ثم M126 على **الحزمة الأصلية فقط**. افحص `obbassets` وهل التسليم `INSTALL_TIME`، ومطابقة تعريفات GooglePAD/Dex.
3. إذا ظهر `NoSuchMethodError` أو `Failed to find Method` في سجل الجهاز، تحقق من اسم الكلاس وتوقيع الدالة وأسلوب دمج GooglePAD ومخرجات Gradle داخل النسخة المعزولة. لا تغير plugin/settings بلا دليل.
4. إذا ظهر `PakFile`, `OBB not found` أو خطأ قراءة الأرشيف، تحقق من توفر install-time pack على الجهاز ومرحلة mount.
5. إذا ظهر `VK_ERROR` أو `RHI`، حلل رسومات GPU والـAPI المدعوم، ولا تغير Vulkan قبل التأكد.
6. إذا ظهر `SIGSEGV`/`SIGABRT`، اربط `backtrace` بنسخة الـ `.so` المطابقة للإصدار 218، مع مراعاة `strip` ورموز C++؛ لا تغيّر اللعبة دون معرفة موقع التعطل.

## نقاط يجب عدم إساءة تفسيرها

- الملف المرجعي `LastFrontier.uproject` يضبط `DisableEnginePluginsByDefault=true` ولا يتضمن إضافة GooglePAD صريحة؛ هذا **لا يكفي** للحكم على تفعيلها داخل حزمة M106 النهائية، فقد تختلف النسخة أو إعدادات المحرك.
- `bPackageDataInsideApk=True` في مرجع GitHub بينما توجد `obbassets` في AAB، لذلك يجب قراءة إعداد M106 الفعلي وتفاصيل asset-pack Manifest. وجود الاثنين وحده ليس إثباتًا أن الحزمة تسلّمت بشكل خاطئ.
- نجاح Cook لخريطة TestMap في M86 ونجاح Editor load في M85 يمنعنا من إعادة إحياء خطأ M60 القديم على أنه تشخيص حاضر؛ لا يعني نجاح الإقلاع على الهاتف.
- لا ينبغي بناء رقم 218 جديدًا؛ استخدم رقمًا أكبر عند ثبوت علاج وبعد تحقق عدم وجود إصدار أحدث، مع استمرار Internal Testing فقط.

## مراجع موثوقة

- [تنسيق DEX الرسمي: method_id_item وclass_data_item](https://source.android.com/docs/core/runtime/dex-format)
- [نصائح Android NDK لتشخيص GetMethodID/NoSuchMethodError](https://developer.android.com/ndk/guides/jni-tips)
- [Epic UE5.8: Google Play Asset Delivery](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine)
- [Google Play Pre-launch report](https://support.google.com/googleplay/android-developer/answer/9842757)
- [Google Play Android Vitals](https://support.google.com/googleplay/android-developer/answer/9859174)
- [Epic forum historical similar splash crash — not proof for this case](https://forums.unrealengine.com/t/google-play-asset-delivery-crash-after-splash-screen/210162)

**قرار:** لم يُحدَّد السبب الجذري، ولم تُفحص الحزمة الأصلية ببرنامج M126. متابعة العمل تتطلب أحد دليلين: نتيجة الفحص على M106 أو سجل الانهيار الحقيقي، مع أفضلية واضحة للسجل الحقيقي.