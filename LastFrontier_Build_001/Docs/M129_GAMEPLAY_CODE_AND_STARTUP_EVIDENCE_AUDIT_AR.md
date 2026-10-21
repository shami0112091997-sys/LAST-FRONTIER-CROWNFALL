# CROWNFALL M129 — إصلاح محدد في كود اللعبة وفصل قاطع عن تحقيق انهيار الإصدار 218

**التاريخ:** 21 أكتوبر 2026  
**النطاق:** مراجعة مصدر Unreal 5.8.3 الفعلي في GitHub، وإصلاح خطأ قابل للاستدلال من الكود في حركة الأعداء، **دون بناء أو توقيع أو طبخ أو نشر**.

## 1. الدليل والفصل بين نوعَي الخطأ

**العطل الذي أبلغ عنه المختبر:** لعبة `com.crownfall.stronghold` الإصدار 218، تثبيت ناجح عبر Google Play Internal Testing؛ يظهر شعار Unreal ثم يغلق التطبيق خلال أقل من ثانية. هذا **لم يُصلَح بعد**. لا يوجد في المرفقات ملف AAB 218 الأصلي أو Android crash stack trace أو اتصال مباشر بـ M106 VM.

**خطأ اللعب المنفصل الذي أصلحناه:**
- `Source/LastFrontier/Private/World/LFWorldDirector.cpp`: `SpawnEnemies()` يستدعي `GetWorld()->SpawnActor<ALFEnemy>(...)` لإنشاء ستة أعداء؛ الكود المرجعي لا يمنحهم `AIController`.
- `Source/LastFrontier/Private/Enemy/LFEnemy.cpp`: `Tick()` يستعمل `AddMovementInput(Delta.GetSafeNormal(), 1.0f)` للمطاردة.
- مكوّن Unreal `UCharacterMovementComponent` لا يُجري حركة شخصية بلا `Controller` عادةً ما لم يُفعَّل `bRunPhysicsWithNoController`. مرجع Epic 5.8: https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UCharacterMovementComponent?lang=en-US .
- **الإصلاح المصدر الوحيد:** في باني `ALFEnemy` بعد `MaxWalkSpeed = ChaseSpeed` أضفنا `GetCharacterMovement()->bRunPhysicsWithNoController = true;`، مع تفسير أن هذا مسار المطاردة البسيط دون متحكم.
- هذا يجعل محاكاة الحركة بلا متحكم **مسموحة على مستوى إعداد المكوّن**؛ لم يُشغَّل Android أو UBT للتحقق من سلوك المطاردة عمليًا. لا ينبغي وصفه بأنه حل تعطل الشاشة الأولى.

## 2. العزل والتحقق

- فرع مستقل `m129-gameplay-movement-fix-isolated`، مُشتق من `m127-jni-forensic-audit-fixes`، **لا يحتوي على مرشح GooglePAD الموجود في M128**. هذه العزلة مهمة لفصل تأثير تغييرات المحرك والتغليف عن خطأ الحركة.
- أُضيف `Scripts/test_M129_controllerless_enemy_static.py`، وهو فحص مصدر من 6 شروط يحقق وجود الإصلاح، واستمرار سلوك المطاردة، وعدم إضافة `Plugins` إلى واصف المشروع. **Static فقط، ليس compile/runtime**.
- فحص مستقل عبر رابط GitHub لملفات الفرع حقق **7/7** شروط هي الشروط الستة ومراجعة سلامة نص الاختبار نفسه. لم يُشغَّل ملف اختبار M129 مباشرة داخل مشروع Unreal المحلي، لعدم وجود checkout مُنزّل في هذه البيئة.
- شغّلنا محليًا ملفات الاختبارات الاصطناعية السابقة `test_M121_local.py`, `test_M122_local.py`, `test_M123_exit_triage_local.py`, `test_M124_local.py`, `test_M125_local.py`, `test_M126_synthetic_dex.py`, `test_M127_critical_regressions.py`: **7 ملفات اختبار PASS** في بيئة Python مؤقتة (اختبارات منهج الفحص لا لعبة الإصدار 218).

## 3. نتائج سجلات المصدر والبناء

- سجل GitHub التاريخي `Saved/M47Logs/M47_Compile_20261003_192352.log` يقول `BLOCKED_OR_FAILED` بسبب غياب جذر Unreal Engine من بيئة أكتوبر 3؛ **لا يمثل نتيجة بناء M86/M119 الأحدث**.
- `Saved/M47Logs/M47_Static_Audit_20261003.log` يقول `PASS_WITH_WARNINGS` ومن تحذيراته غياب `TESTMAP` قديمًا وUE_ROOT من تلك البيئة؛ **لا يُستخدم لإثبات أن خريطة M106 تالفة حاليًا**، لأن Editor M85 وCook M86 نجحا لاحقًا في النسخة الفعلية على VM وفق سجلات المراحل السابقة.
- سكربت إنشاء AAB 218 الموثق في `M119_Secure_Release_218.py` استدعى `BuildCookRun` مع `-skipbuild -skipcook`، ولذلك لم يُثبت بهذا الإجراء إعادة ترجمة وتطبخ المصدر الحالي، رغم نجاح التغليف والتوقيع.
- لا تتوفر سجلات Android runtime الخاصة بجهاز المختبر؛ نتائج التثبيت والتوقيع لا تكفي لتحديد أول استثناء.

## 4. مسار تشخيص فشل الإقلاع بدون تخمين

1. **الدليل الحاسم**: Google Play Console > Pre-launch report > Stability أو Android vitals > Crashes and ANRs (فلتر الإصدار 218)، أو مقتطف `logcat -b crash` بعد إزالة بيانات الهاتف. يمكن أن يخلو Play Console من تقارير صالحة لحجم اختبار صغير.
2. **افحص M106 نفسه قبل اعتماد M128**: `LastFrontier.uproject` و`Config/DefaultEngine.ini` بعد استبعاد أسطر التوقيع، ثم AAB الأصلية و`obbassets` Manifest وتعريفات GooglePAD. GitHub القديم فيه `StoreVersion=215` بينما Play 218؛ لا تنسخ Config كله إلى M106.
3. **تصنيف السجل**: `NoSuchMethodError`/`Failed to find Method` ⇒ JNI/GooglePAD؛ `obb`/`pak`/`AssetPack` ⇒ الوصول إلى أصول Play؛ `Vulkan`/`VK_ERROR` ⇒ RHI؛ `dlopen failed`/`UnsatisfiedLinkError` ⇒ المكتبات الأصلية؛ `SIGSEGV` ⇒ تتبع native stack. لا تُطبّق تصحيح M128 إلا بعد دليل مناسب.
4. **إذا تقرر بناء مرشح مصحح**: أنشئ Sandbox جديدًا مع نسخ احتياطي، راجع أدوات الإصدار وإعدادات signing الخاصة خارج GitHub، ثم Build+Cook+Stage+Package كاملين (لا تستخدم `-skipbuild -skipcook` بعد تغيير الإضافة أو الإعدادات)، اختبر على Android حقيقي، ثم إصدار برقم versionCode أعلى من 218 وبعد التأكد من عدم استخدامه، و**Internal Testing فقط**.
5. اختبار الإصدار المصحح يشمل فتح `TestMap` وثبات 3 دقائق وحركة اللاعب والعدو، إطلاق النار، سجل ANR/crash، جودة تحميل الأصول، التوقيع، 16KB alignment، ARM64، SDK/Play policy.

## 5. ما لم يحدث

لم نعد بناء Unreal أو نطوّر VM، ولم نعدل `main` أو `m66-smart-recovery`، ولم نشغّل GitHub Actions أو نرفع AAB أو نلمس JKS. إصلاح M129 موجود فقط في فرع الاختبار، ولم يصل إلى الهاتف. لا يوجد أي ادعاء بزوال انهيار الإصدار 218.

مراجع: [Unreal CharacterMovement 5.8](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UCharacterMovementComponent?lang=en-US)، [Epic UE5.8 GooglePAD](https://dev.epicgames.com/documentation/unreal-engine/using-google-play-asset-delivery-in-unreal-engine)، [Google PAD delivery](https://developer.android.com/guide/playcore/asset-delivery)، [Android logcat](https://developer.android.com/tools/logcat).
