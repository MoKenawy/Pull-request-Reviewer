(function () {
  "use strict";
  const { $, $$, showNotice, hideNotice, setTab, setBusy, setIdleResults, setModeBadge, renderResults, setFilter, setEditorStats, setSelectedFile, showPRValidation } = window.ReviewerUI;
  const sampleCode = `function calculateTotal(items) {\n  let total = 0;\n  for (let i = 0; i < items.length; i++) {\n    total += items[i];\n  }\n  return total;\n}\n\nconsole.log(calculateTotal([1, 2, 3]));`;
  let selectedFile = null;

  function validGitHubPRUrl(value) {
    try { const url = new URL(value); return url.protocol === "https:" && url.hostname === "github.com" && /^\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/pull\/\d+\/?$/.test(url.pathname); }
    catch { return false; }
  }
  async function readFile(file) {
    if (!file) return;
    if (file.size > window.REVIEWER_CONFIG.MAX_FILE_BYTES) throw new Error("This file is larger than 1 MB. Please choose a smaller source file.");
    const extension = file.name.split(".").pop().toLowerCase();
    if (!/^(js|jsx|ts|tsx|py|java|c|h|cpp|cs|go|rs|php|rb|swift|kt|html|css|json|md|txt|sql|sh|yaml|yml|xml|vue|svelte)$/.test(extension)) throw new Error("This file type is not supported. Choose a text-based source file.");
    const text = await file.text();
    if (text.includes("\u0000")) throw new Error("This does not look like a text source file.");
    selectedFile = file; $("#code-input").value = text; $("#editor-filename").textContent = file.name; setSelectedFile(file); setEditorStats(); setTab("paste"); hideNotice();
  }
  function loadExample() { $("#code-input").value = sampleCode; selectedFile = null; setSelectedFile(null); setEditorStats(); setTab("paste"); hideNotice(); showNotice("Example code loaded. Results will be marked as demo data until the Python API is connected.", "info"); }
  function getLanguage() { return $("#language-select").value; }
  async function runReview() {
    hideNotice(); const activeTab = $(".tab.is-active")?.dataset.tab || "paste";
    try {
      let result;
      if (activeTab === "pr") {
        const url = $("#pr-url-input").value.trim();
        if (!validGitHubPRUrl(url)) { showPRValidation("Enter a valid URL like https://github.com/owner/repository/pull/123", false); showNotice("Please fix the GitHub PR URL before starting the review.", "error"); return; }
        setBusy(true, window.REVIEWER_CONFIG.USE_MOCK_API ? "Validating PR input in demo mode…" : "Sending PR URL to the Python API…");
        result = await window.ReviewerAPI.reviewPullRequest({ url, language: getLanguage() });
      } else {
        const code = $("#code-input").value;
        if (!code.trim()) { showNotice("Paste code or choose a source file before starting a review.", "error"); $("#code-input").focus(); return; }
        setBusy(true, window.REVIEWER_CONFIG.USE_MOCK_API ? "Running the demo review…" : "Sending source code to the Python API…");
        result = await window.ReviewerAPI.reviewCode({ code, filename: selectedFile?.name || $("#editor-filename").textContent || "snippet.js", language: getLanguage() });
      }
      renderResults(result);
      if (result.source === "demo") showNotice("Demo results shown. They are examples, not findings from your code or a real GitHub PR.", "warning");
    } catch (error) { setIdleResults(); showNotice(error.message || "Something went wrong while reviewing the input.", "error"); }
    finally { $("#run-review").disabled = false; $("#run-label").textContent = "Start AI review"; $("#run-icon").textContent = "✦"; }
  }
  async function copyText(text, successMessage) {
    try { await navigator.clipboard.writeText(text); showNotice(successMessage, "success"); }
    catch { showNotice("Clipboard access was blocked by the browser. Select and copy the text manually.", "error"); }
  }

  $$(".tab").forEach(button => button.addEventListener("click", () => { setTab(button.dataset.tab); hideNotice(); }));
  $("#code-input").addEventListener("input", setEditorStats);
  $("#load-example").addEventListener("click", loadExample);
  $("#clear-code").addEventListener("click", () => { $("#code-input").value = ""; selectedFile = null; setSelectedFile(null); setEditorStats(); $("#code-input").focus(); hideNotice(); });
  $("#file-input").addEventListener("change", async event => { try { await readFile(event.target.files[0]); } catch (error) { showNotice(error.message, "error"); event.target.value = ""; } });
  $("#dropzone").addEventListener("dragover", event => { event.preventDefault(); $("#dropzone").classList.add("is-dragging"); });
  $("#dropzone").addEventListener("dragleave", () => $("#dropzone").classList.remove("is-dragging"));
  $("#dropzone").addEventListener("drop", async event => { event.preventDefault(); $("#dropzone").classList.remove("is-dragging"); try { await readFile(event.dataTransfer.files[0]); } catch (error) { showNotice(error.message, "error"); } });
  $("#validate-pr").addEventListener("click", () => { const valid = validGitHubPRUrl($("#pr-url-input").value.trim()); showPRValidation(valid ? "URL format looks valid. A real fetch still requires the backend." : "Invalid URL. Use the format https://github.com/owner/repository/pull/123", valid); });
  $("#pr-url-input").addEventListener("input", () => { $("#pr-validation").hidden = true; });
  $("#run-review").addEventListener("click", runReview);
  $$("[data-filter]").forEach(button => button.addEventListener("click", () => setFilter(button.dataset.filter)));
  $("#reset-filter").addEventListener("click", () => setFilter("all"));
  $("#findings-list").addEventListener("click", event => { const button = event.target.closest(".copy-fix"); if (!button) return; const code = button.parentElement.querySelector("code")?.textContent || ""; copyText(code, "Suggested fix copied."); });
  $("#copy-report").addEventListener("click", () => { const report = ["Pull Request Reviewer report", $("#summary-text").textContent, ...$$(".finding-card").map(card => `${$(".severity-label", card).textContent.toUpperCase()}: ${$("h4", card).textContent}\n${$(".finding-message", card).textContent}${$("pre code", card) ? `\nSuggested fix:\n${$("pre code", card).textContent}` : ""}`)].join("\n\n"); copyText(report, "Review report copied."); });

  setModeBadge(); setEditorStats(); setIdleResults();
})();
