# Pull Request Reviewer — Frontend Starter

A lightweight, modular HTML/CSS/JavaScript frontend based on the previously shared UI. It can be hosted as static files and is intentionally kept framework-free to avoid adding setup complexity before the Python API contract is known.

## Run locally

Because JavaScript modules are loaded as regular deferred scripts, you can open `index.html` directly for the demo. For a more realistic local web origin, run one of these from this folder:

```bash
python -m http.server 5500
```

Then open `http://127.0.0.1:5500`.

## Demo mode vs live API

Open `assets/js/config.js`.

- `USE_MOCK_API: true` (default): runs local UI flow and shows clearly labelled illustrative demo findings. It does **not** call the Python agent or fetch GitHub PR data.
- `USE_MOCK_API: false`: sends requests to the API URL and endpoints configured in the same file. The proposed endpoints are placeholders until checked against the real Python backend.

Current proposed request bodies:

```json
{ "code": "...", "filename": "snippet.py", "language": "Python" }
```

```json
{ "url": "https://github.com/owner/repository/pull/123", "language": "auto" }
```

Current proposed response shape:

```json
{
  "summary": "Short overall review summary",
  "findings": [
    {
      "id": "finding-1",
      "severity": "critical",
      "title": "Missing validation",
      "message": "Explain the problem and its impact.",
      "file": "src/example.py",
      "line": 12,
      "suggestion": "Optional suggested code fix"
    }
  ]
}
```

`assets/js/api.js` contains the only response-normalization layer. When the actual Python API schema is available, update the two endpoint paths, request fields, and `normalizeResult()` there. The UI should not need to change if the adapter returns the normalized shape above.

## File map

- `index.html` — page structure and accessible input tabs.
- `assets/css/style.css` — responsive visual styles.
- `assets/js/config.js` — demo/live mode, base URL, endpoint paths, timeout, upload limit.
- `assets/js/api.js` — demo adapter, HTTP calls, API response normalization.
- `assets/js/ui.js` — UI state and rendering of findings, counts, loading and messages.
- `assets/js/app.js` — events, code input, local file reading, PR URL validation and review flow.

## Important limitations before backend integration

1. Real code review is not possible until the Python endpoint and response contract are confirmed.
2. Real GitHub PR retrieval requires backend support and possibly GitHub authentication/permissions. The browser must not contain a GitHub secret or model API key.
3. The Python API must allow the deployed frontend origin through CORS.
4. The current frontend sends JSON POST requests. If the backend expects multipart uploads, a different field name, authentication, or another schema, update `api.js` to match.
5. Only text-based source files up to 1 MB are accepted by the UI. Files are read locally and their content is sent only after the user starts a review in live mode.

## Quick manual test checklist

- [ ] Load example, edit code, clear code.
- [ ] Try starting a review with empty input (should show validation).
- [ ] Run a demo review and confirm the demo warning/source label is visible.
- [ ] Filter findings by Critical, Warnings, Suggestions, and Total.
- [ ] Expand a suggested fix and copy it.
- [ ] Copy the review report.
- [ ] Upload a small source file; try an unsupported extension and a file over 1 MB.
- [ ] Validate a correct and incorrect GitHub PR URL.
- [ ] In live mode, test backend-offline, API error, timeout, and successful response cases.


////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////


مراجع طلبات السحب (Pull Request Reviewer) — واجهة الفرونت إند الأساسية

واجهة أمامية خفيفة ومنظمة مبنية باستخدام (HTML / CSS / JavaScript) ومستوحاة من التصميم المعتمد مسبقاً. يمكن استضافتها كملفات ثابتة (Static Files)، وتم بناؤها عن قصد بدون أي إطار عمل (Framework-free) لتجنب التعقيد قبل معرفة شكل الاتصال النهائي مع الـ Python API.

التشغيل محلياً

بما أن ملفات الجافاسكريبت يتم تحميلها كـ Scripts عادية مع خاصية defer، يمكنك فتح ملف index.html مباشرة لتجربة العرض التوضيحي (Demo). ولمحاكاة خادم ويب حقيقي، يمكنك تشغيل هذا الأمر من داخل المجلد:

python -m http.server 5500


ثم افتح الرابط في المتصفح: http://127.0.0.1:5500.

وضع التجربة (Demo) مقابل الربط الحقيقي (Live API)

افتح الملف assets/js/config.js:

USE_MOCK_API: true (الوضع الافتراضي): يشغل الواجهة محلياً ويعرض نتائج تجريبية توضيحية. في هذا الوضع لا يتم الاتصال بسيرفر البايثون ولا يتم جلب بيانات حقيقية من GitHub.

USE_MOCK_API: false: يرسل طلبات حقيقية لرابط السيرفر والمسارات المحددة في نفس الملف. المسارات الحالية هي قيم تجريبية مؤقتة حتى يتم مطابقتها مع الـ Backend الفعلي.

شكل البيانات المقترح إرسالها (Request Bodies):

{ "code": "...", "filename": "snippet.py", "language": "Python" }


{ "url": "https://github.com/owner/repository/pull/123", "language": "auto" }


شكل الاستجابة المقترح من السيرفر (Response Shape):

{
  "summary": "ملخص عام وموجز لعملية المراجعة",
  "findings": [
    {
      "id": "finding-1",
      "severity": "critical",
      "title": "التحقق من المدخلات مفقود",
      "message": "شرح للمشكلة وتأثيرها البرمجي.",
      "file": "src/example.py",
      "line": 12,
      "suggestion": "كود التصحيح المقترح اختياري هنا"
    }
  ]
}


يحتوي ملف assets/js/api.js على طبقة توحيد وتنسيق الاستجابة الوحيدة (normalizeResult()). عندما يتم تسليم الـ API الحقيقي من الباك إند، ستقوم فقط بتعديل مسارات الـ Endpoints وأسماء الحقول ودالة normalizeResult() داخل هذا الملف، دون الحاجة لتعديل كود الـ UI إطلاقاً طالما أن المهايئ يُرجع الشكل الموحد أعلاه.

خريطة الملفات (File Map)

index.html — هيكل الصفحة وألسنة التبويب لإدخال الكود.

assets/css/style.css — التنسيقات البصرية وتجاوب الواجهة مع مختلف الشاشات.

assets/js/config.js — التبديل بين الـ Demo والـ Live، عنوان السيرفر (Base URL)، المسارات، وقت الانتظار (Timeout)، والحد الأقصى للملفات.

assets/js/api.js — محاكي التجارب، استدعاءات HTTP، وتوحيد شكل الاستجابة.

assets/js/ui.js — التحكم في عناصر الصفحة وعرض المشاكل والعدادات وتأثيرات التحميل والرسائل.

assets/js/app.js — إدارة الأحداث (Events)، قراءة الكود والملفات المرفوعة، والتحقق من صحة رابط الـ PR وإدارة تدفق الفحص.

قيود وتنبيهات مهمة قبل ربط الباك إند

المراجعة الحقيقية للكود لن تعمل إلا بعد تأكيد مسار الـ Python Endpoint وشكل البيانات المتوقع.

سحب بيانات الـ PR من GitHub يتطلب دعماً من السيرفر وقد يحتاج صلاحيات/مفاتيح (Tokens). يُمنع منعاً باتاً وضع أي مفاتيح سرية لـ GitHub أو الذكاء الاصطناعي داخل المتصفح (Frontend).

يجب ضبط إعدادات الـ CORS في سيرفر البايثون ليسمح باستقبال الطلبات من رابط الفرونت إند.

الواجهة الحالية ترسل البيانات بصيغة JSON POST. إذا كان الباك إند يتطلب multipart/form-data أو أسماء حقول مختلفة، يجب تعديل api.js ليتوافق معه.

الواجهة تقبل فقط الملفات النصية بحد أقصى 1 ميجابايت (1 MB). يتم قراءة الملف داخل المتصفح أولاً، ولا يُرسل محتواه إلا عند بدء المراجعة في الوضع الحي (Live Mode).

قائمة الاختبارات السريعة (Manual Test Checklist)

[ ] تحميل المثال التجريبي، تعديل الكود، ومسح الكود.

[ ] محاولة بدء الفحص مع حقل فارغ (للتأكد من ظهور رسالة التنبيه).

[ ] تشغيل فحص تجريبي (Demo) والتأكد من وضوح علامة أن النتائج تجريبية.

[ ] فلترة المشاكل حسب التصنيف: حرجة (Critical)، تحذيرات (Warnings)، اقتراحات (Suggestions)، والكل (Total).

[ ] فتح الكود المقترح ونسخه.

[ ] نسخ تقرير المراجعة بالكامل.

[ ] تجربة رفع ملف نصي صغير، وتجربة رفع ملف بامتداد غير مدعوم أو حجمه أكبر من 1 ميجابايت.

[ ] التحقق من إدخال رابط GitHub PR صحيح مقابل رابط غير صحيح.

[ ] في الوضع الحي (Live Mode): تجربة حالات انقطاع السيرفر، حدوث خطأ من الـ API، انتهاء وقت الانتظار، واستلام رد ناجح.