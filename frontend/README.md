# Chat UI (experimental)

A Next.js + [assistant-ui](https://www.assistant-ui.com/) front end for `agentic-review`. It talks to the chat graph
in `src/agentic_review/agents/chat_agent.py`, served by a local LangGraph dev server.

**Today it is a wire check**: the graph answers every message with one fixed line and reviews nothing.

How to run it, and what it needs, is in
[`Docs/operation_guidelines.md` §12](../Docs/operation_guidelines.md#12-run-the-chat-ui-experimental).

## Layout

| Path | What |
|---|---|
| `app/MyRuntimeProvider.tsx` | Binds assistant-ui to the LangGraph server and creates threads |
| `app/api/[..._path]/route.ts` | Same-origin proxy to the LangGraph server, so the browser never needs its URL or a key |
| `app/page.tsx` | The thread list and the thread |
| `components/` | assistant-ui and shadcn components, installed from their registries |

Scaffolded from assistant-ui's `with-langgraph` example, with its stockbroker demo tools removed.
