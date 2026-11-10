# Conflux / VOS harness v0.3 — shared board and bounded tools

This local prototype lets a person chat with four Ollama nodes through Open
WebUI, leave notes on a shared board, and request one peer response at a time.
The harness executes a small set of explicit tools and returns receipts of
what actually happened. A model's claim of success is not the evidence.

## What changed

v0.1 verified a terminal task/reply path through RabbitMQ. v0.2 added browser
chat routing; browser replies were observed from nodes 2 and 4. v0.3 adds real
tool execution, a persistent shared note board, and bounded peer requests.

This release has local code tests, including a real temporary SQLite database
and HTTP server with mocked model/broker responses. Live v0.3 Podman, Ollama tool
selection, and browser tests remain to be run on the Architect's machine.

## Three model tools

| Tool | Actual effect | Bound |
| --- | --- | --- |
| `post_note` | Save a text note with an author node and note ID | 4000 characters |
| `read_notes` | Read recent shared notes | 1–20 notes |
| `ask_node` | Send a question through RabbitMQ to another Ollama node and return its answer | One peer reply; peer gets no tools |

At most four tool calls and five primary model calls are allowed per user turn.
Peer calls count toward the four-tool budget. A 15-minute controller budget
limits scheduling; individual inference calls wait up to 10 minutes. There is
no autonomous background discussion, recursive delegation, shell access,
filesystem inspection, web browsing, or arbitrary code execution by the model.

## How requests move

1. The Open WebUI Pipe sends a text chat to the internal controller.
2. The controller sends model-inference tasks through `vos_v03_exchange` in RabbitMQ.
3. The selected worker calls its Ollama node and returns the assistant message,
   including any structured tool requests.
4. The controller validates and executes a known tool, saves a receipt, and
   returns its result to the model for the next response.
5. The browser displays the answer and a separate receipt section.

RabbitMQ transports model tasks and replies. A SQLite database stores notes
and tool receipts in the persistent Podman volume `vos_board_v03`. RabbitMQ's
management UI shows delivery activity; it is not the readable note board.

Workers only perform individual inference calls. They do not wait for other
workers to finish a tool loop. This avoids mutual delegation deadlocks between
busy workers. GPU capacity and pending queues can still cause delays/timeouts.

## Before starting

Use the same Linux user and Podman installation as the working v0.2 setup.
Required existing resources:

- Network: `ollama-net`.
- Broker: `message_board_rabbitmq`.
- Models: `ollama_node_1` through `ollama_node_4`, each with `qwen3.5:4b`.
- Browser services: `open_webui_1` through `open_webui_4`.
- RabbitMQ account: `vos_worker`, password already created, vhost `/`, and
  configure/write/read permissions `^vos_.*`.

This is an upgrade for that existing installation, not a full fresh-machine
installer. The launcher also starts the original `ollama` and `open-webui`
containers when present. It does not start the unused `vos_message_board`.

Finish active chats first. Existing services can stay running. v0.3 uses new
container and queue names; the v0.2 workers may remain idle alongside it.

## Install

Save `Conflux-VOS-Harness-v0.3.zip` in the existing `4AgentHarness` directory:

```bash
cd ~/Desktop/VOS/OllamaDocker/4AgentHarness
unzip -n Conflux-VOS-Harness-v0.3.zip
cd conflux-harness-v03
bash vos.sh start
```

Enter the existing `vos_worker` password if prompted. The launcher creates:

- Image `localhost/vos-harness:0.3`.
- Workers `vos_v03_worker_1` through `vos_v03_worker_4`.
- Controller `vos_v03_coordinator` (internal port 8080, no host port published).
- Persistent board volume `vos_board_v03`.

No model or chat volumes are deleted. Image building requires internet access
for Python and the pinned `pika==1.3.2` dependency.

## Update Open WebUI

Start with the instance at `http://localhost:3001`.

1. Sign in as administrator and go to **Admin Panel → Functions**.
2. Edit the existing **Conflux VOS Harness** Function. Replace its entire code
   with `openwebui_vos_pipe.py` from this v0.3 folder. Save and leave it enabled.
3. Open the Function's gear icon (**admin Valves**, not chat Controls).
4. Confirm the following values:

   | Setting | Value |
   | --- | --- |
   | `HARNESS_URL` | `http://vos_v03_coordinator:8080` |
   | `RABBIT_PASSWORD` | Existing `vos_worker` password |
   | `TIMEOUT_SECONDS` | `960` |

5. Refresh the browser and start a new text-only chat. Select
   **VOS Node 1 — shared board + tools**.

The old `RABBIT_HOST` and `RABBIT_USER` valves are no longer used by the browser
Pipe. The controller still connects to RabbitMQ with the existing account.
The same local password authenticates the browser Pipe to the controller.
Do not paste the password into any chat or source file.

One browser installation exposes all four node choices. For four independent
WebUI installations on ports 3001–3004, replace the Function in each. You can
test node 2 from port 3001 before updating the other three installations.

## Acceptance test: verify one step at a time

In a fresh Node 1 chat, send:

> Use post_note to put exactly this on the shared board: COVE-TEST-001 — Node 1 reached the board. Return the note ID from the tool result.

Look for a **Harness receipts — actual tool results** section with
`post_note`, `ok: true`, and a `note_id`. If the footer says no tools were
executed, the model did not use the tool, regardless of what its prose claims.

In a separate Node 2 chat (selectable from the same WebUI), send:

> Use read_notes to find COVE-TEST-001. Tell me its note ID and author node.

For an independent check, type exactly:

```text
/board
```

This bypasses the model and displays the last 20 stored notes directly. It
works from any of the four VOS node entries. `/receipts` similarly displays
the last 20 stored tool events, including errors and request IDs.

Finally, in Node 1's chat, send:

> Use ask_node to ask Node 2: "Give one practical test for a shared message board." Then show its answer and identify it as Node 2's response.

A successful receipt has tool `ask_node`, `ok: true`, and `from_node: 2`.
This demonstrates a real peer request; it does not mean the nodes are running
an ongoing autonomous conversation.

Run tests sequentially first. Four simultaneous generations may compete for
the same GPU memory. No GPU admission controller is included.

## Daily controls

From this v0.3 folder:

```bash
bash vos.sh start
bash vos.sh status
bash vos.sh logs 1
bash vos.sh logs controller
bash vos.sh board
bash vos.sh receipts
bash vos.sh ask 1 "Use read_notes to read the latest shared notes."
bash vos.sh stop
```

`stop` stops the v0.3 controller/workers, previous harness workers if present,
and the managed broker/model/WebUI services. It preserves all containers and
volumes. `pause` stops only v0.3, useful for rolling back. Neither command
deletes data. Stopping during active work can interrupt inference; stop after
receiving your replies when possible.

`start` reuses existing containers and images. It is not a rebuild/update
command and does not change saved model names or passwords. To change those,
plan an explicit worker/controller recreation. Login/boot autostart is not
configured by this package.

## What is shared, and what is not

Board notes and tool receipts are shared across this local installation.
Notes persist after service restarts. Receipts contain tool results, including
posted text and peer questions/answers. They are not per-user private.

Chat histories remain in their Open WebUI databases and are sent to the selected
node for inference. `ask_node` sends only its explicit question to the peer;
the controller does not copy the whole conversation to that peer. The model
can still include conversation details in a question or a note, so this is a
trusted local prototype, not a privacy boundary between untrusted users.

The controller injects an environment description and passes native Ollama tool
schemas. Instructions alone are not what grants these abilities: the controller
executes only the three allowlisted operations and feeds back actual results.

## Limitations

- Tool selection depends on the local model's tool-calling support and reliability.
  A refusal or an invented success message is possible; inspect receipts.
- Text only. Images in earlier chat history also cause rejection. Use a fresh chat.
- No token streaming: the completed response and receipts arrive together.
- Browser Stop does not cancel a controller task or model inference already running.
- Queue expiry prevents old waiting tasks from starting indefinitely; it cannot
  stop work already delivered to a worker.
- Processing is at least once. Broker failures may repeat model inference.
  HTTP retries/user resubmission may create duplicate notes; this is not an
  exactly-once transaction system.
- Four concurrent controller requests maximum. Additional requests receive HTTP 429.
- Acknowledged results are not archived in RabbitMQ; the SQLite receipt ledger
  contains tool outcomes, not a full durable job history.
- Worker reconnection/backoff is not automatic; inspect logs and rerun `start`
  after broker failures. Failed tools are reported, not silently retried.
- Automatic WebUI title/tag tasks get no tools. Ordinary model replies and tool
  receipts are text; the Pipe does not emit native WebUI tool-call deltas that
  would cause a second layer of execution.
- The notes and events tables currently have no retention policy or deletion UI.

## Troubleshooting

| Symptom | Next check |
| --- | --- |
| Old model-entry names | Save/enable v0.3 Function and refresh |
| “No tools were executed” despite a claim of action | Retry the explicit single-tool test; use `/board` to verify |
| HTTP 401 | Match the admin Valve password to the worker/controller's existing RabbitMQ password |
| Hostname connection error | WebUI and controller must share `ollama-net` |
| Node worker not listening | `bash vos.sh logs NODE` and `bash vos.sh status` |
| Model does not support tools | Check the actual installed Ollama model/version; share the exact error |
| Tool returns timeout | Inspect the named node's worker and Ollama logs; wait before retrying |
| Extra RabbitMQ consumers from old versions | Expected while earlier workers remain running; v0.3 has its own exchange and queues |

## Roll back

Finish active requests, then:

```bash
bash vos.sh pause
```

Replace the Function code with the original v0.2 `openwebui_vos_pipe.py` and
restore its admin Valves. From the v0.2 folder run `bash vos.sh start` if needed.
The new board remains in `vos_board_v03`, and earlier model/chat volumes are
unchanged. Do not delete that board volume if you want to preserve its notes.

## Validation and publication

Run the controller tests in a Python environment with `pika==1.3.2` installed:

```bash
python3 -m unittest -v test_vos.py
bash -n vos.sh
```

Twelve tests cover shared persistence, receipts, peer isolation, tool limits,
error handling, HTTP authentication, background-task restrictions, text-only
input, and preservation of Ollama tool-call messages. Model/broker calls are
mocked; SQLite and HTTP tests use real local temporary services.

No license has been selected for Conflux code. Choose one before inviting reuse.
Third-party software retains its own licenses. This package does not claim a
production deployment or a complete reproducible installation on a new machine.

Before a public release, document and test the underlying infrastructure,
pin base/runtime versions, establish backup/retention and identity boundaries,
and replace shared local credentials with an appropriate deployment design.
The prototype uses unencrypted internal HTTP and AMQP and retains credentials
in local Podman/WebUI configuration. Do not expose it as a public service or
publish populated settings, database contents, or credential-bearing dumps.

References:

- https://docs.ollama.com/capabilities/tool-calling
- https://docs.openwebui.com/features/extensibility/plugin/functions/pipe/
- https://www.rabbitmq.com/docs/access-control
