# S-1 results: does the model call `emit_finding`?

Written by `scripts/s1_tool_calling_probe.py` on 2026-09-17 18:27 UTC.
Endpoint `http://localhost:11434/v1`, temperature 0, 50 runs per model, one planted defect (a missing `await` inside `try/catch` in `src/user.ts`).

**No pass mark is set** (research R-21). The maintainer reads these figures and decides the default model and whether FR-5.6b's structured-output fallback is pulled forward.

## Summary

| Model | Runs | Errors | No call | Calls | Valid | Schema-rejected | Reference-rejected | Invalid JSON | Runs with ≥1 valid | Mean latency (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| `qwen2.5-coder:7b` | 50 | 0 | 50 | 0 | 0 | 0 | 0 | 0 | 0 | 11.73 |

## Per run

| # | Model | Completion | Calls | Valid | Schema-rej. | Ref.-rej. | Invalid JSON | Repair turns | Severities | Tokens in/out | Latency (s) | Error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 7.00 |  |
| 2 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 4.49 |  |
| 3 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 4.46 |  |
| 4 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 8.51 |  |
| 5 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 8.15 |  |
| 6 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 10.34 |  |
| 7 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 10.53 |  |
| 8 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 10.85 |  |
| 9 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 10.55 |  |
| 10 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.01 |  |
| 11 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.84 |  |
| 12 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 22.20 |  |
| 13 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 21.63 |  |
| 14 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 23.76 |  |
| 15 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 12.16 |  |
| 16 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 12.29 |  |
| 17 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 12.21 |  |
| 18 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 12.63 |  |
| 19 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 12.05 |  |
| 20 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 12.34 |  |
| 21 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.94 |  |
| 22 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.25 |  |
| 23 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.54 |  |
| 24 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.34 |  |
| 25 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.46 |  |
| 26 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.84 |  |
| 27 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.37 |  |
| 28 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.08 |  |
| 29 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.08 |  |
| 30 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.34 |  |
| 31 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 12.02 |  |
| 32 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.92 |  |
| 33 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.45 |  |
| 34 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.76 |  |
| 35 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.23 |  |
| 36 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.65 |  |
| 37 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.52 |  |
| 38 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.56 |  |
| 39 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.37 |  |
| 40 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.39 |  |
| 41 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.44 |  |
| 42 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.52 |  |
| 43 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.76 |  |
| 44 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.86 |  |
| 45 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 12.27 |  |
| 46 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.55 |  |
| 47 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.89 |  |
| 48 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.52 |  |
| 49 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.86 |  |
| 50 | `qwen2.5-coder:7b` | no-tool-call | 0 | 0 | 0 | 0 | 0 | 0 | - | 1769/101 | 11.46 |  |
