# Project infographic

One presentation slide summarising the whole project, built to the DEPI infographic template
(16:9, 2560 × 1440, a single left-to-right roadmap). Track: **AI Software Professional**.

| File | What it is |
|---|---|
| [`agentic-code-review-depi-slide.html`](./agentic-code-review-depi-slide.html) | The source. One file — no scripts, no network references, system fonts, hand-written inline SVG icons. The same self-containment rule the tool's own HTML report follows. |
| `agentic-code-review-depi-slide.png` | The 2560 × 1440 render. Drop it straight into a widescreen PowerPoint, Google Slides or Keynote slide; it fills the frame with no letterboxing. |

## Re-rendering after an edit

Edit the HTML, then shoot it with headless Chrome. From the repository root, on Windows:

```powershell
Start-Process -FilePath "C:\Program Files\Google\Chrome\Application\chrome.exe" -NoNewWindow -Wait -ArgumentList @("--headless","--disable-gpu","--hide-scrollbars","--force-device-scale-factor=1","--window-size=2560,1440","--virtual-time-budget=3000","--screenshot=$($PWD.Path)\Docs\assets\infographic\agentic-code-review-depi-slide.png","file:///$($PWD.Path -replace '\\','/')/Docs/assets/infographic/agentic-code-review-depi-slide.html")
```

Three traps, all of which cost an afternoon once:

- **Use `Start-Process -ArgumentList`, not the `&` call operator.** Under Windows PowerShell
  5.1 the `&` form mangles these arguments and Chrome writes nothing.
- **Both paths must be absolute**, which is what the `$PWD` expansions build. Given a
  relative `--screenshot` path Chrome resolves it against its own working directory and
  fails.
- **Chrome exits 0 either way.** A failed render reports only `Failed to write file` on
  stderr, so an exit code tells you nothing. Confirm the bytes actually changed:

```powershell
(Get-FileHash Docs\assets\infographic\agentic-code-review-depi-slide.png).Hash
```

`--force-device-scale-factor=1` is what makes the output exactly 2560 × 1440; without it the
host display's device pixel ratio leaks into the image size.

`--force-device-scale-factor=1` is what makes the output exactly 2560 × 1440; without it the
device pixel ratio of the host display leaks into the image size.

The page has fixed band heights, so after changing any text, check that nothing has outgrown
its card. Open the file in a browser and run this in the console — it prints the headroom
left in every card and stage, and any negative number is an overflow:

```js
document.querySelectorAll('.card, .st').forEach(el => {
  const pad = parseFloat(getComputedStyle(el).paddingBottom);
  const inner = el.getBoundingClientRect().bottom - pad;
  let low = -1e9;
  el.querySelectorAll('*').forEach(c => {
    if (c.tagName === 'svg' || c.closest('svg')) return;
    low = Math.max(low, c.getBoundingClientRect().bottom);
  });
  console.log((el.className.split(' ').find(c => c !== 'card') || 'card'), (inner - low).toFixed(1) + 'px');
});
```

## Sourcing rule

Every claim on the slide is taken from a document in this repository — the template forbids
inventing technologies, architecture or figures. The sources are
[`agentic-code-review-srs-v1.md`](../../agentic-code-review-srs-v1.md) (v1.8),
[`technical_stack.md`](../../technical_stack.md),
[`operation_guidelines.md`](../../operation_guidelines.md),
[`Draft/enterpenuership/000-problem-and-audience.md`](../../Draft/enterpenuership/000-problem-and-audience.md),
[`CAI5_IND5_G1-agentic-pr-review-documentation.md`](../../CAI5_IND5_G1-agentic-pr-review-documentation.md),
the root [`README.md`](../../../README.md), and ADR-0006, 0009, 0010 and 0011.

Deliberately absent, because no document supports them: any latency figure (SRS §2.4 withdrew
the earlier estimate; TBD-1 is still open), any catch rate (the regression harness is not
built), and any cost per review.

The slide presents v1 and the later releases as one whole and does not mark which parts run
today. When demonstrating it, SRS §9 asks for R-1 and R-5 to be restated aloud: at context
depth 1 the thesis is not yet proven, and v1 serves the author before they push rather than a
reviewer clearing a queue.

This folder is **not** `assets/screenshots/` on purpose — `documentation/scripts/sync-docs.mjs`
copies everything in that directory onto the documentation site. Nothing here needs a sync
entry.
