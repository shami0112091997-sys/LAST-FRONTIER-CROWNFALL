# CROWNFALL M127 — تصحيح أخطاء مؤكدة في أداة فحص JNI الخاصة بالإصدار 218

**التاريخ:** 21 أكتوبر 2026. **النطاق:** تحسين أداة التحليل في فرع GitHub مستقل؛ لا تعديل للعبة أو حزمة 218، ولا تنفيذ على VM، ولا دخول إلى Google Play Console أو الهاتف.

## 1. ماذا ثبت فعليًا؟

حزمة CROWNFALL: Stronghold الإصدار `com.crownfall.stronghold` / versionCode `218` بُنيت ووقعت وثُبّتت من مسار Google Play Internal Testing. على هاتف المختبر ظهر شعار Unreal Engine ثم أُغلق التطبيق في أقل من ثانية. هذه ملاحظة **فشل تشغيل فعلية** لكنها لا تفصل بعد بين Java/JNI وملفات الأصول والرسومات وnative أو إنهاء النظام للعملية.

سجلات بناء M86/M88/M119/M118 القديمة تثبت نجاح cook/stage/packaging/ZIP والتوقيع ومحاذاة مكتبات ARM64، لا نجاح تهيئة Unreal على الهاتف. المحادثة لا تتيح AAB الأصلية أو logcat أو Crash & ANR من الجهاز؛ لا يجوز إعلان سبب العطل النهائي.

## 2. أخطاء مثبتة في الفاحص M126 (وقد أصلحت في نسخة M127)

**الخطأ A: تفويت الدالة المعرفة داخل كلاس غير مناسب.** كان فاحص M126 يقارن *اسم الدالة فقط* بتعريف `class_data` في أي كلاس من DEX. إذا كان `AndroidThunkJava_GooglePAD_Available` معرّفًا داخل `Lcom/example/OtherClass;` بدل `GameActivity`، يصدر `exit=0` وتقييمًا مطمئنًا رغم أن الاستدعاء المتوقع قد يبحث في `GameActivity`. أعدت إنتاج ذلك على DEX اصطناعي ثم عدلت الفاحص ليرجع `exit=3` و`REVIEW_METHOD_OWNER_OR_INHERITANCE`. وجود الدالة في كلاس أساسي موروث قد يكون **صحيحًا** وفق JNI؛ لذلك النتيجة تطلب مراجعة ولا تثبت تعطلًا.

**الخطأ B: عدم التنبيه إلى التوقيع الخاطئ للدالة Available().** كان بإمكان دالة بنفس الاسم لكن عائدة بقيمة خاطئة أو بمعاملات أن تنتج `exit=0`. أعدت إنتاجه على DEX اصطناعي ثم أصلحت التقييم: عندما توجد إشارة native إلى `AndroidThunkJava_GooglePAD_Available` دون تعريف `GameActivity` من النوع `()Z`، يعيد `exit=3` و`REVIEW_AVAILABLE_JNI_SIGNATURE`. يحتاج بقية توقيعات GooglePAD إلى تدقيق لاحق؛ لا نزعم أن أداة M127 تتحقق من جميع التواقيع.

**الاختبارات الفعلية هنا:** 14 حالة صناعية من M126 اجتازت مجددًا، وست حالات تراجع صناعية جديدة M127 اجتازت، مع `python3 -m compileall`. **0 فحص على AAB الحقيقية، 0 تشغيل على هاتف، 0 Build أو Publish.**

## 3. دلائل أخرى تحتاج تحققًا (ليست أخطاء مثبتة في التطبيق)

- المصدر المرجعي `.uproject` يحتوي `DisableEnginePluginsByDefault=true` دون إدخال صريح لـ`GooglePAD`، و`DefaultEngine.ini` المرجعي يحتوي `bPackageDataInsideApk=True`، بينما AAB 218 حسب سجل M118 يحوي `obbassets/assets/main.obb.png`. توضح Epic أن تسليم main OBB وقت التثبيت باستخدام GooglePAD يتطلب تفعيل الإضافة وإيقاف `Package Data inside APK`. **يجب قراءة ملفات M106 الفعلية وManifest وحدة obbassets والتأكد من كيفية وصولها للهاتف؛ لا نبدل إعدادات المشروع بالتخمين.**
- تحديث مصدر Unreal أو Android SDK أو Java أو Vulkan دون معرفة الاستثناء قد ينقل العطل أو يصنع عطلًا جديدًا. مطلوب أول فشل من logcat أو Android Vitals.
- GooglePAD ليس وحده المشتبه به: `dlopen failed`, `NoSuchMethodError`, `SIGSEGV`, `SIGABRT`, `VK_ERROR`, `PakFile` مؤشرات فئات مختلفة، لا يبرر أي منها إعادة بناء 219 قبل الحصول على الأثر.

## 4. طريقة التشغيل الآمنة بعد نقل الملف من هذا الفرع إلى VM

مسار أداة الفحص في GitHub:
`LastFrontier_Build_001/Scripts/M126_GooglePAD_Dex_Method_Audit_ReadOnly.py` ضمن الفرع `m127-jni-forensic-audit-fixes`.

لأن المستودع خاص، ينبغي نقل السكربت إلى VM بإجراء موثوق **بعد مراجعة SHA256** بدل الاعتماد على رابط raw عام. على VM حيث يتوفر الملف بصيغته المصححة في `$HOME/crownfall/M126_GooglePAD_Dex_Method_Audit_ReadOnly.py`:

```bash
python3 -m py_compile "$HOME/crownfall/M126_GooglePAD_Dex_Method_Audit_ReadOnly.py"
python3 "$HOME/crownfall/M126_GooglePAD_Dex_Method_Audit_ReadOnly.py" --aab "$HOME/crownfall/M106_RELEASE_SANDBOX_v218/Binaries/Android/LastFrontier-Android-Shipping.aab"
```

إذا ظهر `REVIEW_METHOD_OWNER_OR_INHERITANCE` أو `REVIEW_AVAILABLE_JNI_SIGNATURE` فافتح سجلات **Android** للبحث عن استثناء JNI/FindMethod بالتزامن. إذا ظهرت حالة `STATIC_ACTIVITY_METHODS_FOUND_OTHER_SIGNATURES_UNVERIFIED` فهذا مجرد تحقق جزئي للبنية الثابتة؛ لا يعني نجاح تشغيل اللعبة.

**قبل أي تعديل لمحرك اللعبة أو AndroidRuntimeSettings:** اطلب Screenshot من Play Console → Test and release → Testing → Pre-launch report → Stability، أو Monitor and improve → Android vitals → Crashes and ANRs (الإصدار 218). في حال عدم وجود تقارير، اجمع logcat محليًا على جهاز موثوق وشارك الاستثناء بعد تنقيح البيانات الخاصة فقط.

## 5. الأمان والنسخ

الفرع `m127-jni-forensic-audit-fixes` معزول عن `main` وعن `m66-smart-recovery`، ولم تُغير Config/DefaultEngine.ini ولا `LastFrontier.uproject` ولا AAB/خوادم Google Cloud. لا ينبغي وضع كلمات مرور JKS أو مفاتيحها أو سجلات الجهاز الخام في GitHub. الإصدار 218 مستخدم لدى Google Play ولا يجوز استخدامه لرفع نسخة أخرى؛ ينتظر التصحيح رقم versionCode أعلى بعد الفحوص.

## المصادر الرسمية

- Epic 5.8 GooglePAD: https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine
- Android DEX format: https://source.android.com/docs/core/runtime/dex-format
- Oracle JNI GetMethodID (الاسم والتوقيع وإمكان الإرث): https://docs.oracle.com/en/java/javase/25/docs/specs/jni/functions.html
- Android Logcat: https://developer.android.com/tools/logcat
- Android debugging crashes: https://developer.android.com/topic/performance/issues/crash