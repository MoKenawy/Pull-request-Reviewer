<#
.SYNOPSIS
  Run a review on a demo repository, write the JSON and HTML reports, and screen-record the whole thing.

.DESCRIPTION
  Automates the demonstration end to end. Every step is mechanical: nothing here judges the review's
  output, and nothing waits for a person. The script

    1. checks its prerequisites (git, uv, ffmpeg, the demo repository, the provider key),
    2. optionally fast-forwards the project and runs `uv sync`,
    3. starts an ffmpeg desktop capture,
    4. re-invokes itself with -Inner inside a maximized console, which walks the demonstration:
       the commit under test, the demo repository's state, its PLANTED_DEFECTS.md, the review itself,
       the report files, and an offline re-render whose hash must match,
    5. stops ffmpeg GRACEFULLY by writing "q" to its stdin, so the MP4 is finalised and nothing is
       truncated, and
    6. writes summary.json beside the reports.

  Comparing the findings against the planted defects is deliberately NOT part of this script: deciding
  whether a finding answers a planted defect is a judgement, not a mechanical check. PLANTED_DEFECTS.md
  is displayed so a viewer can make that call themselves.

  All paths handed to uv are normalised to forward slashes: uv strips backslashes from path arguments
  on Windows, and its exit code 2 is indistinguishable from the review tool's own "no judgement" exit 2.

.PARAMETER Project
  The agentic-review checkout. Defaults to the parent of this script's directory.

.PARAMETER Repo
  The repository to review. Defaults to ../review-demo next to the project, as scripts/make_review_demo.py builds it.

.PARAMETER OutDir
  Where the reports and the video go. Defaults to <Project>/dist/demo-run-<yyyy-MM-dd-HHmmss>.

.PARAMETER Pull
  Fast-forward the project and run `uv sync` before recording.

.PARAMETER OpenHtml
  Open the HTML report in the default browser during the recording and page through it. Off by default:
  it drives another application's window, which is the one fragile step.

.PARAMETER SkipRecording
  Run the demonstration without capturing video. Produces the reports and summary.json only.

.PARAMETER PassThruReviewExit
  Exit with the review's own exit code (0 findings / 1 blocking / 2 no judgement / 3 could not start)
  instead of 0. Without it the script exits 0 when the demonstration ran, whatever the review decided,
  and 1 only when the review was never reached. summary.json carries the review's code either way.

.EXAMPLE
  .\scripts\record_demo_run.ps1

.EXAMPLE
  .\scripts\record_demo_run.ps1 -Pull -OpenHtml
#>
[CmdletBinding()]
param(
  [string] $Project,
  [string] $Repo,
  [string] $OutDir,
  [switch] $Pull,
  [switch] $OpenHtml,
  [switch] $SkipRecording,
  [switch] $PassThruReviewExit,
  [int]    $Framerate = 12,
  [int]    $MaxSeconds = 1800,
  [switch] $Inner            # internal: run the on-camera sequence, not the orchestration
)

$ErrorActionPreference = 'Stop'

# uv strips backslashes from path arguments on Windows; forward slashes are valid there too.
function Convert-ToForwardSlash([string] $p) { return ($p -replace '\\', '/') }

function Resolve-Defaults {
  if (-not $script:Project) { $script:Project = Split-Path -Parent $PSScriptRoot }
  $script:Project = Convert-ToForwardSlash ((Resolve-Path $script:Project).Path)

  if (-not $script:Repo) { $script:Repo = "$script:Project/../review-demo" }
  if (-not (Test-Path $script:Repo)) {
    throw ("Demo repository not found: {0}`nBuild one with: uv run --project `"{1}`" python scripts/make_review_demo.py" -f $script:Repo, $script:Project)
  }
  $script:Repo = Convert-ToForwardSlash ((Resolve-Path $script:Repo).Path)

  if (-not $script:OutDir) {
    $script:OutDir = "$script:Project/dist/demo-run-$(Get-Date -Format 'yyyy-MM-dd-HHmmss')"
  }
  $script:OutDir = Convert-ToForwardSlash $script:OutDir
}

# ======================================================================================================
#  INNER: the sequence that appears on camera.
# ======================================================================================================
if ($Inner) {
  $ErrorActionPreference = 'Continue'

  Add-Type -Namespace DemoWin -Name U -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
[DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
'@
  $hwnd = [DemoWin.U]::GetConsoleWindow()
  [void][DemoWin.U]::ShowWindow($hwnd, 3)      # SW_MAXIMIZE
  [void][DemoWin.U]::SetForegroundWindow($hwnd)
  Start-Sleep -Milliseconds 800
  Clear-Host

  function Banner($n, $text) {
    Write-Host ""
    Write-Host ("=" * 104) -ForegroundColor DarkCyan
    Write-Host ("  [$n]  $text") -ForegroundColor Cyan
    Write-Host ("=" * 104) -ForegroundColor DarkCyan
    Write-Host ""
    Start-Sleep -Seconds 2
  }
  function Cmd($c) { Write-Host "PS> $c" -ForegroundColor Yellow; Start-Sleep -Milliseconds 900 }

  $jsonPath  = "$OutDir/review.json"
  $htmlPath  = "$OutDir/review.html"
  $againPath = "$OutDir/review-rerendered.html"

  Write-Host ""
  Write-Host "  agentic-review : JSON + HTML report demonstration" -ForegroundColor White
  Write-Host "  reviewing : $Repo" -ForegroundColor Gray
  Write-Host "  date      : $(Get-Date -Format 'yyyy-MM-dd HH:mm')" -ForegroundColor Gray
  Start-Sleep -Seconds 4

  Banner 1 "The tool: the commit under test, and the report flags"
  Set-Location $Project
  Cmd "git log --oneline -3"
  git log --oneline -3
  Start-Sleep -Seconds 3
  Cmd "agentic-review review --help   (note --json and --html)"
  uv run --project $Project agentic-review review --help
  Start-Sleep -Seconds 7

  Banner 2 "The change under review"
  Set-Location $Repo
  Cmd "git log --oneline -1"
  git log --oneline -1
  Start-Sleep -Seconds 2
  Cmd "git status --short"
  git status --short
  Start-Sleep -Seconds 5
  Cmd "git diff --stat"
  git diff --stat
  Start-Sleep -Seconds 5

  if (Test-Path "$Repo/PLANTED_DEFECTS.md") {
    Banner 3 "GROUND TRUTH: the defects planted in that change, shown before the tool runs"
    Cmd "cat PLANTED_DEFECTS.md"
    Get-Content "$Repo/PLANTED_DEFECTS.md" | ForEach-Object { Write-Host $_ }
    Start-Sleep -Seconds 22
  }

  Banner 4 "The review: one model pass, writing a JSON report and an HTML report"
  Cmd "agentic-review review --json review.json --html review.html"
  uv run --project $Project --env-file "$Project/.env" agentic-review review --json $jsonPath --html $htmlPath
  $code = $LASTEXITCODE
  Write-Host ""
  Write-Host "  exit code: $code" -ForegroundColor Magenta
  Set-Content -Path "$OutDir/.review-exit" -Value "$code" -Encoding ascii
  Start-Sleep -Seconds 14

  if (Test-Path $jsonPath) {
    Banner 5 "The report files that one run produced"
    Cmd "Get-ChildItem"
    Get-ChildItem $OutDir | Where-Object { -not $_.Name.StartsWith('.') } |
      Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
    Start-Sleep -Seconds 4

    Cmd "the JSON report is the authoritative surface:"
    $r = Get-Content $jsonPath -Raw | ConvertFrom-Json
    Write-Host ("verdict      : {0}" -f $r.verdict)
    Write-Host ("findings     : {0}" -f @($r.findings).Count)
    Write-Host ("degradations : {0}" -f @($r.degradations).Count)
    Write-Host ""
    foreach ($f in $r.findings) {
      Write-Host ("  {0}:{1}-{2}  {3}/{4}" -f $f.file, $f.startLine, $f.endLine, $f.severity, $f.category)
    }
    Start-Sleep -Seconds 12

    Banner 6 "Re-render the saved JSON offline: no key, no network, no model call"
    Cmd "agentic-review render review.json --html review-rerendered.html"
    uv run --project $Project agentic-review render $jsonPath --html $againPath
    Write-Host "  render exit code: $LASTEXITCODE" -ForegroundColor Magenta
    Start-Sleep -Seconds 4
    Cmd "Get-FileHash review.html, review-rerendered.html   (must match)"
    Get-FileHash $htmlPath, $againPath | Select-Object Hash, Path | Format-List
    $h1 = (Get-FileHash $htmlPath).Hash
    $h2 = (Get-FileHash $againPath).Hash
    if ($h1 -eq $h2) {
      Write-Host "  BYTE-IDENTICAL: the HTML regenerates from the JSON alone." -ForegroundColor Green
    } else {
      Write-Host "  DIFFERENT - the re-render did not reproduce the original." -ForegroundColor Red
    }
    Start-Sleep -Seconds 12

    # Deliberately last: a browser window cannot reliably be pushed behind this console again
    # (Windows refuses SetForegroundWindow to a background process), so nothing that matters may
    # follow it. Ending on the rendered report is also the better closing shot.
    if ($OpenHtml) {
      Banner 7 "The HTML report: one self-contained file, opened in a browser"
      Cmd "Start-Process review.html"
      Start-Process $htmlPath
      Start-Sleep -Seconds 8
      Add-Type -AssemblyName System.Windows.Forms
      1..9 | ForEach-Object {
        [System.Windows.Forms.SendKeys]::SendWait("{PGDN}")
        Start-Sleep -Seconds 3
      }
      Start-Sleep -Seconds 4
      [void][DemoWin.U]::SetForegroundWindow($hwnd)   # best effort; nothing depends on it
      Start-Sleep -Seconds 2
    }
  } else {
    Write-Host ""
    Write-Host "  No report was written. The review did not reach the model - see the message above." -ForegroundColor Red
    Start-Sleep -Seconds 12
  }

  Write-Host ""
  Write-Host ("=" * 104) -ForegroundColor DarkCyan
  Write-Host "  Done. The reports are in $OutDir" -ForegroundColor White
  Write-Host ("=" * 104) -ForegroundColor DarkCyan
  Start-Sleep -Seconds 7
  exit 0
}

# ======================================================================================================
#  OUTER: checks, recording, orchestration, summary.
# ======================================================================================================
function Assert-Command($name, $hint) {
  $c = Get-Command $name -ErrorAction SilentlyContinue
  if (-not $c) { throw "$name was not found on PATH. $hint" }
}

Resolve-Defaults

Write-Host "Checking prerequisites..." -ForegroundColor Cyan
Assert-Command git 'Install git.'
Assert-Command uv  'See https://docs.astral.sh/uv/.'
if (-not $SkipRecording) {
  Assert-Command ffmpeg 'Install it, for example: winget install Gyan.FFmpeg'
}

$envFile = "$Project/.env"
if (-not (Test-Path $envFile)) {
  throw "$envFile is missing; the inner run passes it to uv with --env-file. See Docs/operation_guidelines.md section 3."
}
$haveKey = [bool]$env:AGENTIC_REVIEW_API_KEY
if (-not $haveKey) {
  $haveKey = Select-String -Path $envFile -Pattern '^AGENTIC_REVIEW_API_KEY=.+' -Quiet
}
if (-not $haveKey) {
  throw "No provider credential. Set AGENTIC_REVIEW_API_KEY in the environment or in $envFile."
}

if ($Pull) {
  Write-Host "Pulling and syncing..." -ForegroundColor Cyan
  Push-Location $Project
  try {
    git pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw "git pull --ff-only failed; resolve it by hand before recording." }
    uv sync
    if ($LASTEXITCODE -ne 0) { throw "uv sync failed." }
  } finally { Pop-Location }
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$video = "$OutDir/review-run.mp4"
Remove-Item "$OutDir/.review-exit" -ErrorAction SilentlyContinue

# --- start the capture -------------------------------------------------------------------------------
$ff = $null
if (-not $SkipRecording) {
  Write-Host "Recording to $video" -ForegroundColor Cyan
  # ffmpeg keeps its stdin: the graceful stop below writes "q" to it, which makes ffmpeg flush and
  # finalise the MP4. Killing it instead truncates the tail of the recording.
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName              = 'ffmpeg'
  $psi.Arguments             = "-y -loglevel error -nostats -f gdigrab -framerate $Framerate -draw_mouse 1 " +
                               "-i desktop -c:v libx264 -preset veryfast -crf 26 -pix_fmt yuv420p " +
                               "-t $MaxSeconds `"$video`""
  $psi.UseShellExecute       = $false
  $psi.CreateNoWindow        = $true
  $psi.RedirectStandardInput = $true
  $psi.RedirectStandardError = $true
  $ff = [System.Diagnostics.Process]::Start($psi)
  Start-Sleep -Seconds 4
  if ($ff.HasExited) { throw "ffmpeg exited immediately: $($ff.StandardError.ReadToEnd())" }
}

# --- run the demonstration in its own maximized console ----------------------------------------------
$started = Get-Date
$innerArgs = @(
  '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath,
  '-Inner', '-Project', $Project, '-Repo', $Repo, '-OutDir', $OutDir
)
if ($OpenHtml) { $innerArgs += '-OpenHtml' }
Start-Process -FilePath 'powershell' -ArgumentList $innerArgs -WindowStyle Maximized -Wait
$elapsed = ((Get-Date) - $started).TotalSeconds

# --- stop the capture gracefully ---------------------------------------------------------------------
if ($ff -and -not $ff.HasExited) {
  Start-Sleep -Seconds 2
  try {
    $ff.StandardInput.Write('q')
    $ff.StandardInput.Flush()
    $ff.StandardInput.Close()
  } catch { }
  if (-not $ff.WaitForExit(30000)) {
    Write-Warning "ffmpeg did not stop on its own; killing it. The last seconds of video may be lost."
    $ff.Kill()
    [void]$ff.WaitForExit(10000)
  }
  $ffErr = $ff.StandardError.ReadToEnd()
  if ($ffErr.Trim()) { Write-Host $ffErr -ForegroundColor DarkGray }
}

# --- summarise ---------------------------------------------------------------------------------------
$reviewExit = $null
if (Test-Path "$OutDir/.review-exit") {
  $reviewExit = [int](Get-Content "$OutDir/.review-exit" -Raw).Trim()
  Remove-Item "$OutDir/.review-exit" -ErrorAction SilentlyContinue
}

$summary = [ordered]@{
  startedAt  = $started.ToString('s')
  elapsedSec = [math]::Round($elapsed, 1)
  project    = $Project
  repository = $Repo
  outDir     = $OutDir
  reviewExit = $reviewExit
}

$jsonPath = "$OutDir/review.json"
if (Test-Path $jsonPath) {
  $r = Get-Content $jsonPath -Raw | ConvertFrom-Json
  $summary.verdict      = $r.verdict
  $summary.findings     = @($r.findings).Count
  $summary.blocking     = @($r.findings | Where-Object { $_.severity -eq 'blocking'  }).Count
  $summary.important    = @($r.findings | Where-Object { $_.severity -eq 'important' }).Count
  $summary.nit          = @($r.findings | Where-Object { $_.severity -eq 'nit'       }).Count
  $summary.degradations = @($r.degradations | ForEach-Object { "$($_.source)/$($_.code)" })
  $summary.findingsList = @($r.findings | ForEach-Object {
    "{0}:{1}-{2} {3}/{4}" -f $_.file, $_.startLine, $_.endLine, $_.severity, $_.category
  })
} else {
  $summary.verdict = 'no report written'
}

$htmlPath  = "$OutDir/review.html"
$againPath = "$OutDir/review-rerendered.html"
if ((Test-Path $htmlPath) -and (Test-Path $againPath)) {
  $h1 = (Get-FileHash $htmlPath).Hash
  $h2 = (Get-FileHash $againPath).Hash
  $summary.htmlSha256        = $h1
  $summary.rerenderIdentical = ($h1 -eq $h2)
}
if (Test-Path $video) {
  $summary.video      = $video
  $summary.videoBytes = (Get-Item $video).Length
}

$summary | ConvertTo-Json -Depth 5 | Set-Content "$OutDir/summary.json" -Encoding utf8

Write-Host ""
Write-Host "================ run summary ================" -ForegroundColor Cyan
foreach ($kv in $summary.GetEnumerator()) {
  $v = $kv.Value
  if ($v -is [System.Array]) { $v = ($v -join '; ') }
  "{0,-18} {1}" -f $kv.Key, $v
}
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Written to $OutDir" -ForegroundColor Green

# The script's own exit code answers "did the demonstration run", not "did the review find bugs":
# a review that correctly reports a blocking finding exits 1, which would otherwise look like a
# failed recording. The review's own code is in summary.json, and -PassThruReviewExit forwards it
# for a caller that wants the review's verdict as its contract.
if ($PassThruReviewExit -and $null -ne $reviewExit) { exit $reviewExit }
if ($null -eq $reviewExit) { exit 1 }   # the inner run never reached the review
exit 0
