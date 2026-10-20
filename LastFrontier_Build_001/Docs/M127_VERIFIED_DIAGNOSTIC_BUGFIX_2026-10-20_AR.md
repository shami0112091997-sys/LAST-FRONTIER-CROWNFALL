# CROWNFALL M127 — إصلاح مثبت في أداة تشخيص الانهيار (20 أكتوبر 2026)

## نطاق الفحص وما لم يتوفر
- الإصدار 218 `com.crownfall.stronghold` ثُبّت من Google Play Internal Testing، ثم خرج خلال أقل من ثانية بعد شعار Unreal.
- ليس هناك حتى الآن `logcat` أو استثناء موثق من هاتف المختبر، ولا نسخة AAB الأصلية داخل بيئة هذا الفحص. الحزمة الأصلية وفق سجل M119/M118 موجودة على VM `crownfall-m62-build` في مجلد `M106_RELEASE_SANDBOX_v218`.
- المراجعة شملت: سجلات مراحل M60، M85-M86، M116-M121 المحفوظة بالمستودع، مصدر C++ (GameMode/GameInstance/Character/Enemy/WorldDirector)، إعدادات Android/Unreal، والبرامج M121-M126، ووثائق Epic وAndroid الرسمية.
- **لا يوجد سبب ثابت لتوقف الإصدار 218 حتى الآن.** فشل بناء M60 القديم لا يساوي فشل تشغيل 218 على الهاتف.

## إصلاح برمجي مثبت: أداة M126 كانت تُنتج نتيجة سليمة مضلِّلة
قبل M127، حالة الاختبار المصطنعة:
1. المكتبة `libUnreal.so` تحتوي سلسلة `AndroidThunkJava_GooglePAD_Available`.
2. ملف DEX يحتوي تعريف دالة بهذا الاسم **في كلاس غير مرتبط** هو `Lcom/example/OtherClass;`، بينما `GameActivity` لا يعرّفها.
3. أداة M126 الأصلية أعادت **exit 0** و `STATIC_METHOD_DEFINITIONS_PRESENT_SIGNATURE_UNVERIFIED`، رغم أن `M126_DEX_GAME_ACTIVITY_METHOD_DEFINITIONS=0`.
هذه نتيجة ثابتة أُعيد إنتاجها محليًا بملف AAB مصطنع؛ **إنها خطأ في أداة التشخيص لا برهان على خطأ داخل اللعبة**.

## التعديل المعزول المطبق
فرع `m127-verified-dex-jni-triage-fix`:
- تحديث `Scripts/M126_GooglePAD_Dex_Method_Audit_ReadOnly.py` لتمييز تعريف الدالة في `GameActivity`/`GameApplication` عن تعريفها في كلاس آخر.
- في حال وجد الاسم معرفًا خارج الكلاسات المتوقعة فقط، صار يعطي `REVIEW_METHOD_NOT_DEFINED_IN_EXPECTED_ACTIVITY` مع exit 3 بدل نجاح مضلل.
- حين تطلب المكتبة اسم `AndroidThunkJava_GooglePAD_Available`، يفحص البرنامج أيضًا تعريف `()Z` داخل الكلاس المتوقع؛ إن لم يتطابق يطبع `REVIEW_AVAILABLE_JNI_SIGNATURE_MISMATCH` مع exit 3.
- الإخراج الجديد `M127_NATIVE_PAD_NAMES_NOT_IN_GAME_ACTIVITY` و`M127_AVAILABLE_REQUIRED_BY_NATIVE` و`M127_AVAILABLE_GAME_ACTIVITY_BOOL_SIGNATURE`.
- تحديث `Scripts/test_M126_synthetic_dex.py` بثلاث حالات انحدار تشمل **تعريفًا في كلاس مختلف، توقيعًا خاطئًا، وتوقيعًا صحيحًا**.
- **17/17 اختبارًا اصطناعيًا ناجحًا** على بيئة Python المحلية. لم يُنفّذ الفحص على AAB 218 الحقيقية؛ ولم يحدث Build أو Cook أو نشر.

## قيود دقيقة على الأداة الجديدة
- أسماء الدوال المستخرجة من `.so` مؤشرات نصية فقط؛ لا تثبت أن المسار البرمجي وصل إلى `GetMethodID`.
- قد يكون هناك `GameActivity` مشتق أو مُسمّى باسم مخصص أو تعريف موروث؛ لذلك `REVIEW` يعني فحصًا إضافيًا، **ولا يثبت خطأً في تشغيل Java**.
- أداة M127 تتحقق من توقيع `()Z` لهذا الاسم التاريخي فقط؛ بقية توقيعات JNI، ومسار ربط الكلاسات في وقت التشغيل، لا تُفحص بالكامل.
- قد تكون مشكلة فعلية في `GooglePAD`/تسليم `obbassets`، أو Vulkan، أو مكتبات C++، أو تحميل TestMap، أو عملية إغلاق من النظام. لا يُقبل اختيار أي إصلاح من هذه دون دليل.

## مراجعة دقيقة للسجل التاريخي
- GitHub Actions القديم M60: فشل `UnrealEditor-Cmd` مع `LogLinker Serialization error`: FName index 64 خارج [0,44) في `TestMap.umap`، و`RunUAT ExitCode=25`. هذا **خطأ سابق في خريطة مختلفة**.
- التحقق اللاحق M85: `Editor map load PASS`؛ M86: `Android_ASTC Cook EXIT=0` و`Packages Cooked: 220`. هذه الشواهد تُضعف ربط تلف M60 مباشرة بانهيار الإصدار 218، دون أن تثبت تشغيل TestMap على الهاتف.
- M119/M118: `Shipping Distribution` مع `UAT_EXIT=0`، `bundleRelease`، توقيع رفع صحيح، `bundletool validate`، package/versionCode/targetSdk، أربع مكتبات ARM64 و16KB كلها PASS.
- M121: التثبيت عبر Google Play PASS، التشغيل بعد شعار Unreal FAIL. هذه هي نقطة الفشل الحقيقية المتبقية.

## طريقة الاستئناف مع أكبر فائدة
**أفضل دليل حاسم:** من Play Console → `Test and release → Testing → Pre-launch report → Details → Stability` للإصدار 218؛ ثم `Monitor and improve → Android vitals → Crashes and ANRs`. قد لا تتوفر تقارير جهاز واحد. لا تشارك تقريرًا خامًا يحوي بيانات خاصة.

**فحص ثابت لاحق، قراءة فقط على خادم M106:** حمّل النسخة **المصححة على فرع M127** من السكربت، ثم بعد مراجعة نصها ونقلها إلى VM نفذ:
```bash
python3 -m py_compile "$HOME/crownfall/M126_GooglePAD_Dex_Method_Audit_ReadOnly.py"
python3 "$HOME/crownfall/M126_GooglePAD_Dex_Method_Audit_ReadOnly.py"
```
يتوقع السكربت المسار الأصلي للحزمة على M106 تلقائيًا، ويقتصر على قراءة AAB بدون كشف مفاتيح أو كلمة مرور. أرسل *سطرَي `M126_ASSESSMENT` و`M127_NATIVE_PAD_NAMES_NOT_IN_GAME_ACTIVITY` مع حالة التنفيذ*، ولا ترسل AAB الخاصة ولا أسرار التوقيع.

**لا تغّير أبدًا رقم 218 داخل إصدار مثبت.** بعد تحديد السبب وإصلاحه في بيئة مستقلة، اختبر إصدارًا جديدًا (code أعلى من 218) على الهاتف قبل تحديث قناة Internal Testing. لا تلمس production.

## المراجع الرسمية
- Epic UE5.8 Google Play Asset Delivery: https://dev.epicgames.com/documentation/en-us/unreal-engine/using-google-play-asset-delivery-in-unreal-engine
- Android DEX format: https://source.android.com/docs/core/runtime/dex-format
- Android JNI guidance: https://developer.android.com/ndk/guides/jni-tips
- Google Pre-launch report: https://support.google.com/googleplay/android-developer/answer/9842757
- Google Play Crashes and ANRs: https://support.google.com/googleplay/android-developer/answer/9859174
