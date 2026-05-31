# Memory and Five-Layer Notes

Session learning: the JSON Tool Runtime pattern should treat memory as a structured preference/state layer and should map cleanly into the user's Five-Layer World Collaboration Model.

## Structured memory layer

Memory is not raw chat logs and not magical model state. It is bounded, queryable context that helps the program adapt over time.

Good memory candidates:

- User preferences: language, tone, timezone, default currency, UI style, notification style.
- User corrections: category fixes, preferred package manager, actions that should require confirmation.
- Stable domain facts: project conventions, account/category mappings, workspace defaults.
- Developer-queryable iteration signals: recurring parse failures, common clarification reasons, accepted corrections, rejected actions.

Bad memory candidates:

- Raw conversations or full transcripts.
- Secrets, credentials, private tokens, sensitive payloads.
- Temporary task progress.
- Unvalidated LLM guesses.
- Product records that belong in the application database.

Runtime rule:

```text
current user input > scoped retrieved memory > old/default memory
```

Memory can bias parsing/defaults, but it must never bypass schema validation, policy checks, or confirmation rules.

## Preference Correction Loop

Split preference correction into two stages:

```text
Pre-LLM correction teaches the model before it decides.
Post-LLM correction controls, repairs, or rejects the decision after it is produced.
```

### Pre-LLM Preference Injection

Use before the model call:

```text
user input
  -> retrieve scoped preferences, stable facts, and prior corrections
  -> build bounded prompt context
  -> LLM outputs strict JSON
```

Good uses:

- Inject timezone, language, currency, UI/tone, and project defaults.
- Inject user corrections such as category mappings or preferred adapter behavior.
- Bias ambiguous parsing without overriding explicit current input.

Rule: pre-LLM memory helps the model decide, but cannot bypass schemas, policy gates, or confirmations.

### Post-LLM Validation and Correction

Use after the model emits JSON:

```text
LLM JSON
  -> parse
  -> schema validation
  -> policy gate
  -> deterministic normalization when safe
  -> user confirmation/correction when needed
```

Good uses:

- Reject malformed JSON, unknown actions, missing required fields, and invalid argument types.
- Escalate destructive, external, sensitive, or privileged actions to confirmation.
- Apply deterministic normalization only when safe and auditable.
- Capture user feedback after a bad decision.

Rule: post-LLM correction prevents bad model decisions from becoming side effects.

### Correction-to-Memory Feedback

```text
Post-LLM correction
  -> classify whether correction is durable
  -> write structured memory if durable
  -> retrieve it as future Pre-LLM context
  -> update golden tests/schema/prompt if systematic
```

This closes the loop: LLM 后纠偏产生新规则；新规则下次变成 LLM 前纠偏。

## Online correction loop

```text
LLM JSON decision
  -> program validates/proposes/executes
  -> user corrects
  -> program classifies correction durability
  -> durable correction becomes structured memory
  -> future prompts retrieve relevant memory
  -> golden tests/schema/prompt may be updated if the correction is systematic
```

## Five-Layer mapping

Map JSON Tool Runtime components to the Five-Layer World Collaboration Model:

| Layer | JSON Tool Runtime role |
|---|---|
| Cellular / tools | JSON schemas, validators, policy gates, adapter functions, scripts, API clients, logs, tests |
| Biological / agents | An agent/app instance that uses the runtime with role, memory, tools, state, health |
| Societal / multi-agent | L0/L1/L2 agents sharing action contracts, review evidence, handoffs, and correction loops |
| Planetary / world | A coherent runtime with workspace, gateway, memory, docs, cron, skills, and registries aligned |
| Cosmic / multi-node | Multi-device/multi-service hands that execute validated actions and return evidence |

Design implication:

- Start at the lowest sufficient layer.
- Promote repeated adapter/tool behavior into scripts/tests.
- Promote reusable process into skills.
- Promote worldview/governance into canonical docs.
- Keep memory as a slow-variable input layer, not as execution authority.

## Public naming note

The install slug may remain `llm-json-tool-runtime` for compatibility. Public docs can use the shorter display phrase `JSON Tool Runtime` without renaming the skill or repository.
