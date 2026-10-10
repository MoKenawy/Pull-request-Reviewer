(function () {
  "use strict";
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  let currentFindings = [];
  let activeFilter = "all";

  function escapeHTML(value) { return String(value).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch]); }
  function showNotice(message, type = "info") {
    const el = $("#notice"); el.textContent = message; el.className = `notice notice-${type}`; el.hidden = false;
  }
  function hideNotice() { $("#notice").hidden = true; }
  function setTab(name) {
    $$(".tab").forEach(tab => { const active = tab.dataset.tab === name; tab.classList.toggle("is-active", active); tab.setAttribute("aria-selected", String(active)); });
    $$(".tab-panel").forEach(panel => { panel.hidden = panel.id !== `${name}-panel`; });
  }
  function setBusy(busy, message = "Preparing your code…") {
    $("#run-review").disabled = busy; $("#run-label").textContent = busy ? "Reviewing…" : "Start AI review"; $("#run-icon").textContent = busy ? "" : "✦";
    $("#results-empty").hidden = true; $("#results-content").hidden = true; $("#results-loading").hidden = !busy;
    $("#loading-message").textContent = message;
    $("#result-state").textContent = busy ? "In progress" : "Waiting for input"; $("#result-state").className = `status-pill ${busy ? "status-loading" : "status-idle"}`;
  }
  function setIdleResults() { $("#results-loading").hidden = true; $("#results-content").hidden = true; $("#results-empty").hidden = false; $("#result-state").textContent = "Waiting for input"; $("#result-state").className = "status-pill status-idle"; }
  function setModeBadge() { const mock = window.REVIEWER_CONFIG.USE_MOCK_API; $("#mode-badge").textContent = mock ? "DEMO MODE" : "LIVE API"; $("#mode-badge").className = `mode-badge ${mock ? "mode-demo" : "mode-live"}`; }
  function renderResults(result) {
    currentFindings = result.findings || []; activeFilter = "all";
    const counts = { critical: 0, warning: 0, suggestion: 0 }; currentFindings.forEach(item => counts[item.severity]++);
    $("#count-critical").textContent = counts.critical; $("#count-warning").textContent = counts.warning; $("#count-suggestion").textContent = counts.suggestion; $("#count-total").textContent = currentFindings.length;
    $("#summary-text").textContent = result.summary || "Review completed.";
    $("#result-source").textContent = result.source === "api" ? "Live Python API result" : "Demo data — not AI-generated";
    $("#results-empty").hidden = true; $("#results-loading").hidden = true; $("#results-content").hidden = false;
    $("#result-state").textContent = "Review complete"; $("#result-state").className = "status-pill status-success";
    renderFindings();
  }
  function renderFindings() {
    const list = $("#findings-list"); const filtered = activeFilter === "all" ? currentFindings : currentFindings.filter(item => item.severity === activeFilter);
    $$("[data-filter]").forEach(button => button.classList.toggle("is-selected", button.dataset.filter === activeFilter));
    $("#reset-filter").textContent = activeFilter === "all" ? "Show all" : "Clear filter";
    if (!filtered.length) { list.innerHTML = '<div class="no-findings">No findings match this filter.</div>'; return; }
    list.innerHTML = filtered.map((item, index) => `<article class="finding-card severity-${escapeHTML(item.severity)}"><div class="finding-top"><span class="severity-dot"></span><span class="severity-label">${escapeHTML(item.severity)}</span><span class="finding-number">#${index + 1}</span></div><h4>${escapeHTML(item.title)}</h4><p class="finding-message">${escapeHTML(item.message)}</p>${item.file || item.line ? `<div class="finding-location">${escapeHTML(item.file || "Source file")}${item.line ? ` · Line ${escapeHTML(item.line)}` : ""}</div>` : ""}${item.suggestion ? `<details class="suggestion-details"><summary>View suggested fix</summary><pre><code>${escapeHTML(item.suggestion)}</code></pre><button class="text-button copy-fix" type="button">Copy fix</button></details>` : ""}</article>`).join("");
  }
  function setFilter(filter) { activeFilter = filter; renderFindings(); }
  function setEditorStats() { const code = $("#code-input").value; $("#char-count").textContent = `${code.length.toLocaleString()} characters`; $("#line-count").textContent = `${code ? code.split("\n").length : 0} lines`; }
  function setSelectedFile(file) { const el = $("#selected-file"); el.hidden = !file; el.textContent = file ? `${file.name} · ${(file.size / 1024).toFixed(1)} KB` : ""; $("#editor-filename").textContent = file ? file.name : "snippet.js"; }
  function showPRValidation(message, valid) { const el = $("#pr-validation"); el.hidden = false; el.className = `inline-status ${valid ? "inline-success" : "inline-error"}`; el.textContent = message; }

  window.ReviewerUI = { $, $$, escapeHTML, showNotice, hideNotice, setTab, setBusy, setIdleResults, setModeBadge, renderResults, setFilter, setEditorStats, setSelectedFile, showPRValidation };
})();
