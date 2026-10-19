# CROWNFALL — M122 تحقيق أعمق في إغلاق الإصدار 218 مباشرة بعد شعار Unreal

**التاريخ:** 19 أكتوبر 2026 · **الحالة:** تجهيز تشخيصي دون الوصول المباشر إلى الهاتف أو خادم Google Cloud، دون تعديل للعبة أو تشغيل Build أو النشر.

## نتيجة التحقيق الحالية

الإصدار 218 تم تنزيله وتثبيته عبر Google Play Internal Testing. بعد ظهور شعار Unreal لأقل من ثانية تعود الواجهة إلى Android. لا توجد حتى الآن رسالة استثناء أو أثر استدعاءات (stack trace) من الجهاز. لذلك لا يمكن التمييز بعد بين خطأ Java، فشل تحميل مكتبة أو موارد، عطل C++، مشكلة RHI/Vulkan أو إنهاء النظام للتطبيق.

تثبت سجلات M119/M118 إنشاء AAB وتوقيعه وصحة Manifest ومستوى API 36 و16KB، لكنها **ليست اختبارًا للتحميل على الجهاز**.

## تصنيف أسباب العطل — ما الذي يميّز كل حالة؟

| فئة محتملة | الدليل المطلوب | التصرف بعد التأكيد |
|---|---|---|
| Java/JNI / native library load | `FATAL EXCEPTION`, `UnsatisfiedLinkError`, `dlopen failed` | فحص اسم المكتبة، ABI، التبعيات، وإعدادات النشاط JNI. |
| تعطل native C++ | `SIGSEGV`, `SIGABRT`, `Fatal signal`, backtrace مع `libUnreal.so` أو مكتبة اللعبة | استخدم رموز بناء تطابق الإصدار 218، وحدد الدالة قبل تغيير الكود. |
| Google Play Asset Delivery | رسائل `GooglePAD`, `AssetPack`, `obbassets`, `OBB not found`, `LogPakFile` | تحقق من آلية التسليم الفعلية وإعدادات الإضافة/التغليف في M106. |
| Vulkan / RHI | `VK_ERROR`, `Vulkan`, `RHIInit`, رسائل جهاز رسومي | جرّب خيار عرض بديل فقط على نسخة تشخيصية لاحقة. |
| Content / Map | `Failed to load`, `Can't find file`, `TestMap`, `ShaderCodeLibrary`, `PakFile` | قارن ملفات cook والأرشيفات، وأعد cook معزولًا فقط عند الحاجة. |
| خروج مقصود أو قتل بسبب الموارد | `Process ... has died`, `lowmemorykiller`, `am_kill`, `OutOfMemoryError` | راجع سبب إنهاء العملية والذاكرة قبل افتراض crash. |

**الاحتمال الراجح للفحص المبكر، لا سبب مُثبت:** وجود وحدة `obbassets` في AAB مع `DisableEnginePluginsByDefault=True` دون `GooglePAD` صريح في مصدر المشروع، و`bPackageDataInsideApk=True` في إعداداته المرجعية. يجب فحص نسخة M106 المبنية فعلًا، ومحتوى AAB والوضع `install-time` مقابل `fast-follow/on-demand`. وثائق Epic تقول إن GooglePAD يمكن تفعيله في Project Settings، وإن استخدامه لتسليم OBB وقت التثبيت يستلزم تعطيل Package Data inside APK. **لكن وجود `obbassets` وحده لا يثبت أن الملف غير متاح على الهاتف.**

## M122: مراجعة تشخيص بنية تسليم الأصول دون تعديل

البرنامج `M122_AssetPack_Delivery_Audit_ReadOnly.py` يقرأ AAB الأصلي و`DefaultEngine.ini` و`.uproject` داخل M106 ويستخدم `bundletool-all-1.18.3.jar` مع التحقق من بصمة SHA-256 المعروفة، ثم يفحص Manifest لوحدة `obbassets` فعليًا ويصنّف **INSTALL_TIME / FAST_FOLLOW / ON_DEMAND / UNKNOWN**. لا يعدّل AAB ولا يفتح أسرار المفتاح، ويكتب نتائج مختصرة فقط. `PASS` في اختبار البرنامج الاصطناعي لا يثبت أنه اختبر AAB الحقيقي.

النتائج المطلوبة عند تنفيذه مستقبلاً على خادم `crownfall-m62-build`:

- `M122_ASSET_PACK_DELIVERY=INSTALL_TIME` إذا كانت الحزمة install-time، أو قيمة أخرى تستلزم التحقيق.
- `M122_ENGINE_PLUGINS_DISABLED_BY_DEFAULT=...`
- `M122_GOOGLEPAD_PLUGIN_ENTRY=...`
- `M122_PACKAGE_DATA_INSIDE_APK=...`
- `M122_CRASH_CAUSE=UNCONFIRMED_NEED_DEVICE_STACK_TRACE`

لأن M119 نجح و218 مستخدم بالفعل في Play، **ممنوع استخدام رقم 218 مجددًا** لإصلاح. الإصدار المرشح التالي 219 بعد التحقق من عدم رفع إصدار أحدث.

## أحسن مسار لجمع دليل العطل لاحقًا

**المسار 1 — بلا إعداد إضافي:** Google Play Console → CROWNFALL → Android vitals → Crashes and ANRs، أو Pre-launch report → Stability، وفلترة الإصدار 218. البيانات قد تتأخر وقد لا تتضمن تعطلًا تم على هاتف واحد فورًا. اطلب لقطة **للخطأ نفسه** بعد إخفاء بيانات الحساب والجهاز؛ لا تنقل السجل الخام.

**المسار 2 — من هاتف Android، عند توفر المستخدم:** الإعدادات → خيارات المطور → **Take bug report** بعد إعادة إنتاج عطل فتح CROWNFALL. التقرير قد يتضمن معلومات شديدة الحساسية عن الجهاز والشبكات والتطبيقات؛ لا ترفعه إلى GitHub أو المحادثة بصيغته الخام. استخرج أولًا الأسطر المتعلقة بالتطبيق فقط واحذف أي معرفات أو رموز/معلومات شخصية.

**المسار 3 — ADB لجهاز موثوق (اختياري):** على Android 11+ تدعم Google pairing عبر **Wireless debugging**. عند توفر بيئة موثوقة فيها `adb` (جهاز كمبيوتر أو Termux مدعوم)، شغّل `adb logcat -b crash -d -v threadtime` بعد تشغيل اللعبة مباشرة. وأيضًا قد تحتاج main/system لمعرفة أخطاء تحميل assets أو قتل العملية. **لا ترسل سجل الجهاز كله ولا تمنح أذونات تصحيح لأجهزة غير موثوقة.** بدلاً من ذلك راجع تقرير Play.

## معايير السماح ببناء التصحيح

1. تحديد فئة العطل بمقتطف سجل قابل للتحقق أو إعادة إنتاج فعلي مع دليل واضح.
2. عزل تعديل واحد فقط في نسخة خاصة، وتسجيل طريقة التراجع. لا تبدّل Vulkan/GooglePAD/Cook دفعة واحدة.
3. إن كان تعديل أصول Unreal أو الإضافات، يتطلب الأمر Cook/Build جديدين بالأوضاع الصحيحة، ولا يجوز اعتبار `skipcook` صالحًا بعد تغيير أصل مؤثر في cook.
4. اختبار نسخة تصحيحية على جهاز فعلي وتأكيد دخول TestMap وتشغيل التحكم قبل إرسالها إلى مجموعة المختبرين.
5. اختر versionCode أعلى من 218؛ طابق شهادة الرفع، packageName، API، الفحوص الأصلية و16KB، ثم ارفع **Internal Testing** فقط، وتحقق من Play Console قبل النشر.
6. الاحتفاظ بنسخة احتياطية من M63/M84/M106، ومفتاح JKS في مكان محمي، وعدم وضع كلمة المرور أو ملفات Gradle الخاصة في GitHub أو التقرير.

## المصادر الرسمية

- Epic GooglePAD (UE 5.8): https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine
- Android Play Asset Delivery (Native): https://developer.android.com/guide/playcore/asset-delivery/integrate-native
- Android PAD delivery modes: https://developer.android.com/guide/playcore/asset-delivery
- Android crash diagnosis: https://developer.android.com/topic/performance/vitals/crash
- Android Logcat: https://developer.android.com/tools/logcat
- Android ADB wireless pairing: https://developer.android.com/tools/adb
- Android Bug report: https://developer.android.com/studio/debug/bug-report
- Play Console Pre-launch Stability: https://support.google.com/googleplay/android-developer/answer/9844487
- Native symbolication: https://developer.android.com/ndk/guides/ndk-stack
