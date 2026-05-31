---
name: llm-json-tool-runtime
description: "Use when designing, rebuilding, or implementing AI-powered software where an LLM converts messy inputs into strict JSON and deterministic program code validates the JSON before executing tools, commands, APIs, or state changes."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ai-apps, llm, json-schema, tool-runtime, software-architecture, agents]
    related_skills: [test-driven-development, systematic-debugging, writing-plans]
---

# LLM JSON Tool Runtime

## Overview

This skill captures MarsDoge's preferred framework for rebuilding or developing AI projects.

Public-facing shorthand: **JSON Tool Runtime**. The installed skill name is `llm-json-tool-runtime`, but when publishing docs, repos, examples, or product copy, prefer the shorter phrase “JSON Tool Runtime” unless an exact install command needs the full skill slug.

The core idea: an LLM is the thinking transform from input to output, not the whole application. The application should build deterministic “hands, feet, and components” around the LLM: file IO, API clients, shell wrappers, database writes, browser extractors, notification senders, and other bounded tool adapters.

Use the LLM to turn ambiguous human input into strict structured JSON. Then normal program code validates that JSON and dispatches safe deterministic tools. Program code owns state, permissions, retries, idempotency, logging, and side effects.

Canonical shape:

```text
Natural language / event
  -> program builds fixed prompt + context + action manifest + schema
  -> LLM outputs strict JSON only
  -> program parses and validates JSON
  -> program dispatches deterministic tool adapter
  -> adapter performs side effect or returns data
  -> program records trace and returns result
```

Short version:

```text
LLM = brain / parser / planner
Program = nervous system / validator / execution controller
Tools = hands and feet / deterministic components
```

Do not let the LLM directly control the world. Let it describe an intended action in a typed JSON contract, then let code decide whether and how that action is allowed to run.

## When to Use

Use this skill when:

- Designing a new AI app, AI agent, bot, automation workflow, or LLM-powered product.
- Rebuilding an existing AI project that currently relies on loose prompts and unstructured text.
- Turning natural language into actions: accounting entries, issue creation, file edits, calendar events, notifications, browser operations, database writes, or shell commands.
- Defining tool-calling architecture without relying on model-specific magic.
- Building safe software where LLM output may lead to external side effects.
- Creating MVPs where the LLM should classify, parse, plan, or route work, but program code must remain in control.

Do not use this as a heavy framework for:

- Simple one-shot text generation with no side effects and no machine parsing.
- Pure chatbots where free-form prose is the only output.
- Fully deterministic tasks where no LLM is needed.

## Core Principles

1. **Define the program before the prompt.** First specify what the application actually does, what inputs it accepts, and what actions it may take.
2. **LLM output must be machine-readable.** Prefer strict JSON Schema, Pydantic, Zod, TypeBox, or equivalent typed contracts.
3. **Code validates before execution.** Never execute a tool, command, API call, or database write before schema validation and permission checks.
4. **Adapters are deterministic.** Each tool adapter has a small name, strict arguments, known outputs, timeout behavior, error behavior, and tests.
5. **Side effects are owned by code.** The LLM proposes; program code disposes.
6. **Unsafe actions require confirmation.** Destructive, external, costly, irreversible, or privacy-sensitive actions need explicit confirmation unless the user has already granted scoped permission.
7. **Prompts are contracts, not vibes.** A prompt should describe role, context, available actions, schema, unknown handling, safety rules, and output-only constraints.
8. **No chain-of-thought dependency.** Store short `reason_codes` or `explanation` fields if needed for debugging, but do not require hidden reasoning text for execution.
9. **Observable by default.** Log schema version, prompt version, model, parsed action, validation result, adapter result, and error path without leaking secrets.
10. **Start narrow.** Add a few safe actions first; expand the tool surface only after tests and guardrails exist.
11. **Memory is structured preference/state, not raw chat logs.** Use memory to dynamically capture user preferences, corrections, stable domain facts, and developer-queryable iteration data. Feed retrieved memory back into the prompt contract as bounded context, then let schemas and policy gates still control execution.

## Memory and User Preference Layer

See `references/memory-and-five-layer-notes.md` for the condensed session notes covering structured memory, online correction loops, Five-Layer mapping, and public naming guidance.

Memory is a first-class input layer in this framework. It should not be treated as magical model state or a raw transcript dump. It is structured, queryable context that helps the program adapt to the user over time.

Use memory for:

- User preferences: language, tone, default currency, timezone, UI style, risk tolerance, notification style.
- User corrections: “this category should be food, not shopping”, “never auto-post this type”, “prefer pnpm over npm”.
- Stable domain facts: project conventions, account/category mappings, workspace defaults, schema defaults.
- Developer-queryable iteration data: recurring parse failures, common clarification reasons, accepted corrections, preferred adapter behavior.
- Online correction loops: when the user corrects an LLM decision, persist the corrected preference/fact so future runs improve.

Do not use memory for:

- Raw chat logs.
- Secrets, credentials, private tokens, or sensitive payloads.
- Temporary task progress that will become stale soon.
- Unvalidated model guesses.
- Side-effect records that belong in the product database.

Memory should feed the LLM as bounded context:

```text
user input
  + fixed prompt contract
  + action manifest
  + JSON schema
  + retrieved user preferences / stable facts / prior corrections
  -> LLM JSON decision
```

The runtime should still validate everything. Memory can bias parsing and defaults, but it must not bypass schema validation, permission checks, or confirmation rules.

Recommended memory record shape:

```json
{
  "type": "user_preference",
  "scope": "bookkeeping",
  "key": "default_payment_method",
  "value": "wechat",
  "source": "user_correction",
  "confidence": "high",
  "updated_at": "2026-05-31T22:30:00+08:00"
}
```

Online correction flow:

1. Program executes or proposes a JSON decision.
2. User corrects the result.
3. Program classifies whether the correction is durable.
4. If durable, write a structured memory record.
5. Future prompts retrieve relevant memory and include it as context.
6. Tests/golden cases are updated if the correction reveals a systematic behavior.

Developer iteration flow:

1. Log validation failures, clarification reasons, rejected actions, and user corrections.
2. Aggregate these records for developers.
3. Use them to improve schemas, prompts, action definitions, and adapters.
4. Keep product data, traces, and user preferences separated.

## Development Workflow

When building an AI project with this framework, follow this order:

1. **Write the product goal.** One paragraph: who uses it, what input arrives, what output or side effect is expected.
2. **List input events.** Examples: user text, voice transcript, webhook payload, uploaded file, scheduled cron tick, email, chat message.
3. **List allowed actions.** Use stable action names like `ledger.add_expense`, `file.patch`, `calendar.create_event`, `notification.send`, `db.insert_record`.
4. **Define the JSON schema.** Make action names enums. Make required fields explicit. Reject unknown fields where possible.
5. **Design deterministic adapters.** Each action maps to one adapter function/module with strict input/output types.
6. **Write the prompt contract.** Include domain rules, available actions, output schema, examples, unknown handling, safety constraints, and bounded retrieved memory.
7. **Build the runtime loop.** Normalize input -> retrieve relevant memory -> call LLM -> parse JSON -> validate -> dispatch adapter -> return result.
8. **Handle failures.** Malformed JSON, schema mismatch, unsafe action, missing fields, unknown action, adapter error, timeout.
9. **Add tests.** Golden examples, invalid examples, adapter unit tests, dry-run end-to-end tests.
10. **Add observability.** Trace IDs, schema version, prompt version, model, validation errors, adapter status, but no secrets.
11. **Then improve UX.** Only after the core loop is reliable should you add rich UI, more actions, or more model autonomy.

## Runtime Execution Loop

Use this mental model for most projects:

```python
def handle_event(event):
    normalized = normalize_event(event)
    context = load_context(normalized)
    memory_context = retrieve_relevant_memory(normalized, context)

    llm_input = build_prompt(
        base_prompt=BASE_PROMPT,
        schema=OUTPUT_SCHEMA,
        action_manifest=ACTION_MANIFEST,
        context=context,
        memory_context=memory_context,
        user_input=normalized,
    )

    raw = call_llm(llm_input)
    data = parse_json(raw)
    validated = validate_schema(data, OUTPUT_SCHEMA)

    decision = enforce_policy(validated)
    if decision.requires_confirmation:
        return ask_user_to_confirm(decision)

    adapter = ADAPTERS[decision.action]
    result = adapter.run(decision.arguments)

    record_trace(event, decision, result)
    return format_result(result)
```

Critical invariant:

```text
No adapter runs before parse + schema validation + policy check.
```

## Prompt Contract Pattern

A good base prompt says exactly what the LLM is allowed to do.

Template:

```text
You are a bounded parser/planner inside a larger program.
You do not execute tools directly.
Your job is to convert the user input into exactly one JSON object.

Available actions:
- ledger.add_expense: create one expense record
- ledger.ask_clarification: ask the user for missing required details
- no_action: use when the user input does not request an allowed action

Rules:
- Output JSON only. No markdown. No prose outside JSON.
- Use only actions listed in the action manifest.
- If required information is missing, output ledger.ask_clarification.
- If the request is destructive, external, or ambiguous, set requires_confirmation=true.
- Do not invent amounts, dates, people, file paths, or API targets.
- Timezone: Asia/Shanghai.
- Currency default: CNY only when the user did not specify another currency and the domain allows this default.

Schema:
<insert JSON schema here>

Relevant memory:
<insert bounded user preferences, stable facts, and prior corrections here>

User input:
<insert normalized user input here>
```

Prompt quality checklist:

- [ ] Role is bounded: parser/planner, not autonomous actor.
- [ ] Action list is explicit.
- [ ] JSON schema is included or referenced by name/version.
- [ ] Output is JSON-only.
- [ ] Unknown/missing information path is specified.
- [ ] Risky action confirmation rule is specified.
- [ ] Domain defaults are explicit.
- [ ] Relevant memory is bounded, durable, and non-secret.
- [ ] Examples cover common and ambiguous inputs.

## JSON Schema Contract Pattern

For action-oriented apps, prefer a top-level schema like:

```json
{
  "intent": "create_record",
  "action": "ledger.add_expense",
  "arguments": {
    "amount": 32.5,
    "currency": "CNY",
    "category": "food",
    "occurred_at": "2026-05-31T20:10:00+08:00",
    "payment_method": "wechat",
    "note": "晚饭"
  },
  "requires_confirmation": false,
  "confidence": "high",
  "reason_codes": ["amount_detected", "category_detected"]
}
```

Recommended fields:

- `intent`: coarse intent enum, useful for analytics and routing.
- `action`: exact deterministic adapter name, enum only.
- `arguments`: object that matches the selected adapter input schema.
- `requires_confirmation`: boolean safety gate.
- `confidence`: `high | medium | low`, not a free-form essay.
- `reason_codes`: short enum/list for debuggability, not chain-of-thought.
- `user_message`: optional user-facing message for clarification or no-action cases.

Schema rules:

- Prefer enums over free strings for action names, categories, states, and permission levels.
- Reject unknown top-level fields when possible.
- Make risky fields explicit: paths, URLs, account IDs, recipients, amounts, commands, destructive flags.
- Version schemas: `schema_version: "2026-05-31.v1"` or similar.
- Keep generated JSON separate from final prose unless the schema deliberately includes a `user_message` field.

## Tool Adapter Pattern

Each adapter is a deterministic component. Treat it like a small API surface.

Adapter definition should include:

```text
name: ledger.add_expense
purpose: Insert one validated expense record.
input_schema: AddExpenseArgs
output_schema: AddExpenseResult
permission_level: normal_write
idempotency_key: user_id + occurred_at + amount + note_hash
timeout: 5 seconds
retry: safe on transient database/network errors only
side_effect: writes one ledger row
dry_run: supported
confirmation_required: false for normal expense; true for unusually large amount
```

Implementation guidance:

- Do not expose raw shell, raw SQL, broad HTTP, or arbitrary file writes as first-class LLM actions.
- Prefer narrow adapters like `file.patch_known_file` over `shell.run`.
- If shell access is unavoidable, use allowlists, sandboxing, argument arrays, and explicit confirmation.
- Each adapter should return structured results, not only human prose.
- Each adapter should have tests independent of the LLM.

Example adapter families:

```text
file.read
file.patch
file.write_new
shell.run_allowlisted
db.insert_record
db.query_readonly
http.post_json_allowlisted
calendar.create_event
ledger.add_expense
browser.extract_text
notification.send
issue.create
```

## Example 1: AI Bookkeeping

User says:

```text
今天晚上吃饭花了 32.5，微信支付
```

The application sends the LLM a fixed prompt plus schema. The LLM must output JSON:

```json
{
  "intent": "expense_record",
  "action": "ledger.add_expense",
  "arguments": {
    "amount": 32.5,
    "currency": "CNY",
    "category": "food",
    "payment_method": "wechat",
    "note": "晚饭",
    "occurred_at": "2026-05-31T20:00:00+08:00"
  },
  "requires_confirmation": false,
  "confidence": "high",
  "reason_codes": ["amount_detected", "payment_method_detected", "food_detected"]
}
```

The program then:

1. Parses JSON.
2. Validates schema.
3. Checks amount/category/payment method policy.
4. Calls `ledger.add_expense(arguments)`.
5. Returns a human message like: `已记账：晚饭 32.5 CNY，微信支付。`

The LLM did not write the database. It translated messy language into a validated action request.

## Example 2: File Patch Assistant

User says:

```text
帮我把 README 里的安装命令改成 pnpm install
```

Allowed actions:

```json
[
  {"name": "file.read", "description": "Read a project file"},
  {"name": "file.patch", "description": "Replace an exact unique string in a project file"}
]
```

LLM output:

```json
{
  "intent": "edit_file",
  "action": "file.patch",
  "arguments": {
    "path": "README.md",
    "old_text": "npm install",
    "new_text": "pnpm install"
  },
  "requires_confirmation": false,
  "confidence": "medium",
  "reason_codes": ["target_file_detected", "replacement_detected"]
}
```

Program checks:

- Path is inside workspace.
- File exists.
- `old_text` appears exactly once.
- Action is allowlisted.
- Patch is not destructive.

Then the program applies the patch and returns the diff.

## Example 3: Safe Shell Wrapper

User says:

```text
看一下当前目录有多大
```

Do not ask the LLM for arbitrary shell text. Define a safe action:

```json
{
  "intent": "inspect_disk_usage",
  "action": "workspace.disk_usage",
  "arguments": {
    "path": "."
  },
  "requires_confirmation": false,
  "confidence": "high",
  "reason_codes": ["disk_usage_requested"]
}
```

Program maps this to a safe internal implementation:

```python
def workspace_disk_usage(path):
    safe_path = ensure_inside_workspace(path)
    return run(["du", "-sh", safe_path])
```

If the user says “清理一下没用的文件”, the model should not guess a delete command. It should emit a clarification or confirmation action:

```json
{
  "intent": "needs_clarification",
  "action": "ask_clarification",
  "arguments": {
    "question": "清理文件属于破坏性操作。请确认具体目录、文件类型和是否先 dry-run。"
  },
  "requires_confirmation": true,
  "confidence": "high",
  "reason_codes": ["destructive_action", "target_unspecified"]
}
```

## Example 4: Meeting Summary to Tasks

Input:

```text
Meeting transcript text...
```

Schema:

```json
{
  "summary": "string",
  "todos": [
    {
      "owner": "string | unknown",
      "task": "string",
      "deadline": "string | null",
      "priority": "high | medium | low"
    }
  ],
  "decisions": [
    {
      "decision": "string",
      "reason": "string"
    }
  ],
  "risks": [
    {
      "risk": "string",
      "level": "high | medium | low"
    }
  ]
}
```

Program then writes tasks to Linear/Feishu/Notion only after validation and user/project policy checks.

## Five-Layer World Mapping

When this runtime is used inside the user's Five-Layer World Collaboration Model, place each part at the right layer instead of turning everything into an agent:

- Cellular / tools: the LLM JSON action executors: JSON schemas, validators, policy gates, adapter functions, scripts, API clients, logs, and tests.
- Biological / agents: an agent or app instance using the runtime with role, memory, tools, state, and health.
- Societal / multi-agent: L0/L1/L2 agents sharing action contracts, review evidence, handoffs, and correction loops.
- Planetary / world: workspace, gateway, memory, docs, cron, skills, and registries coherently running together.
- Cosmic / multi-node: multi-device or multi-service hands that execute validated actions and return evidence.

Rule: memory and schemas improve the lower layers, but execution authority still lives in validated code and explicit policy gates.

## Safety and Permission Model

Classify actions before implementation:

```text
readonly: read files, query database, fetch public data
normal_write: create ordinary records, save drafts, write scoped app state
external_write: send messages, create public issues, post webhooks, charge money
sensitive_read: read secrets, private messages, personal data, credentials
destructive: delete, overwrite, force push, revoke, transfer, clear database
privileged: change permissions, deploy production, modify DNS, rotate secrets
```

Default policy:

- `readonly`: allowed if scoped to the project/user request.
- `normal_write`: allowed after schema validation, unless unusual amount/scope.
- `external_write`: usually requires explicit confirmation or prior scoped permission.
- `sensitive_read`: ask first and minimize what enters the LLM context.
- `destructive`: explicit confirmation with target + reason + dry-run when possible.
- `privileged`: explicit confirmation and audit log.

## Error Handling

Handle these paths explicitly:

- LLM returned non-JSON.
- JSON parses but fails schema validation.
- Unknown action name.
- Known action but invalid arguments.
- Missing required information.
- Action requires confirmation.
- Adapter timeout.
- Adapter returned partial success.
- External API rate limit or auth failure.
- Duplicate/idempotent action detected.

Recommended behavior:

```text
Malformed model output -> retry once with validation error included -> if still bad, fail safely.
Missing info -> ask clarification.
Unsafe request -> ask confirmation or refuse.
Adapter failure -> return structured error and do not pretend success.
Duplicate request -> return existing result or no-op with explanation.
```

## Testing and Validation

Minimum tests for projects using this framework:

- Valid example JSON passes schema.
- Missing required fields fail schema.
- Unknown action fails schema or policy.
- Malformed LLM text never reaches adapter execution.
- Runtime does not execute adapters before validation.
- Risky/destructive examples require confirmation.
- Adapter unit tests run without LLM calls.
- Golden user inputs produce expected JSON decisions.
- Ambiguous inputs produce clarification, not guessed side effects.
- Dry-run path works before real external writes.

For coding tasks, prefer TDD:

1. Write schema tests.
2. Write adapter tests.
3. Write runtime dispatch tests.
4. Add prompt golden cases.
5. Only then connect the real model/API.

## Common Pitfalls

1. **Letting raw LLM text become commands.** Never run shell commands, SQL, file writes, or API calls directly from free-form model text.
2. **Prompt-only safety.** A sentence like “do not do dangerous things” is not a guardrail. Enforce safety in schema, policy, and adapter code.
3. **Open-ended tool surface.** Avoid exposing `run_command(command: string)` or `http_request(url: string, body: any)` to the LLM unless heavily sandboxed.
4. **No schema version.** Without schema versions, old prompts and new code drift silently.
5. **Combining machine JSON and user prose.** If the runtime expects JSON, require JSON only. Put human text in a `user_message` field if needed.
6. **Skipping idempotency.** External writes can duplicate if retries happen. Design idempotency keys for writes.
7. **Logging secrets.** Do not put API keys, credentials, private tokens, or full sensitive payloads into prompts or traces.
8. **Trusting confidence too much.** `confidence` is a hint, not proof. Validation and policy are still required.
9. **Treating memory as truth.** Memory is useful context, but it can be stale, scoped incorrectly, or user-corrected later. Retrieve narrowly, include provenance when possible, and let explicit current user input override older memory.
10. **Expanding actions too early.** Start with narrow safe actions; add more only after tests catch regressions.
11. **Using the LLM as a database.** Store state in real storage. The LLM can summarize or choose; it should not be the source of truth.
12. **Overlong public names.** For open-source publication and README copy, prefer a concise class-level name such as “JSON Tool Runtime”. Keep longer slugs only when needed for install compatibility or disambiguation.

## Verification Checklist

When applying this skill to a project, verify:

- [ ] Product goal is written before prompts.
- [ ] Input event types are listed.
- [ ] Allowed actions are listed as stable adapter names.
- [ ] JSON schema exists and rejects unknown/invalid actions.
- [ ] Prompt contract says JSON-only and defines unknown handling.
- [ ] Relevant memory is retrieved narrowly and never bypasses policy.
- [ ] User corrections can update durable preferences/facts when appropriate.
- [ ] Runtime validates JSON before dispatch.
- [ ] Policy gate runs before any side effect.
- [ ] Destructive/external actions require confirmation.
- [ ] Adapters are narrow and deterministic.
- [ ] Adapter tests do not depend on the LLM.
- [ ] Golden tests cover normal, ambiguous, and unsafe inputs.
- [ ] Logs include trace IDs and schema/prompt versions.
- [ ] Secrets are not exposed to prompts or logs.

## One-Sentence Rule

AI 项目不是让 LLM 直接控制世界，而是让 LLM 把模糊输入转换成严格 JSON，然后由程序用受控工具验证和执行。
