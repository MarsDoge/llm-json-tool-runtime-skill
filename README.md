# LLM JSON Tool Runtime Skill

A Hermes Agent skill for building AI applications where the LLM is a bounded parser/planner and deterministic program code owns validation, permissions, tool execution, and side effects.

Core rule:

> Do not let the LLM directly control the world. Let it convert messy input into strict JSON, then let program code validate and execute through controlled tools.

## Mental Model

```text
Natural language / event
  -> fixed prompt + context + action manifest + JSON schema
  -> LLM outputs strict JSON only
  -> program parses and validates JSON
  -> policy gate checks safety / permissions / confirmation
  -> deterministic tool adapter executes the side effect
  -> program records trace and returns result
```

```text
LLM     = brain / parser / planner
Program = nervous system / validator / execution controller
Tools   = hands and feet / deterministic components
```

## What This Skill Teaches Agents

Use this skill when designing, rebuilding, or implementing AI-powered software such as:

- AI agents and automation workflows
- natural-language-to-action products
- AI bookkeeping / personal finance capture
- file edit assistants
- safe shell or workspace assistants
- meeting transcript to tasks pipelines
- bots that call APIs, databases, commands, or business tools

The skill guides agents to define:

1. product goal and input events
2. allowed actions
3. strict JSON schema
4. fixed prompt contract
5. deterministic tool adapters
6. validation and policy gates
7. runtime execution loop
8. tests, golden cases, and dry-run checks

## Repository Layout

```text
.
├── README.md
├── LICENSE
├── scripts/
│   └── validate_skill.py
└── skills/
    └── llm-json-tool-runtime/
        └── SKILL.md
```

## Install

### Install into Hermes Agent

```bash
mkdir -p ~/.hermes/skills/software-development
git clone https://github.com/MarsDoge/llm-json-tool-runtime-skill.git /tmp/llm-json-tool-runtime-skill
cp -R /tmp/llm-json-tool-runtime-skill/skills/llm-json-tool-runtime \
  ~/.hermes/skills/software-development/llm-json-tool-runtime
```

Then restart Hermes or run `/reload-skills` if available.

### Load in a Hermes session

```text
/skill llm-json-tool-runtime
```

Or start Hermes with the skill preloaded:

```bash
hermes -s llm-json-tool-runtime
```

## Quick Example

User input:

```text
今天晚上吃饭花了 32.5，微信支付
```

LLM output should be strict JSON, not free-form execution:

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

Program code then validates the JSON and calls a deterministic adapter:

```python
validated = validate_schema(llm_json, OUTPUT_SCHEMA)
policy = enforce_policy(validated)
if policy.requires_confirmation:
    return ask_user(policy.confirmation_message)

result = ADAPTERS[validated["action"]].run(validated["arguments"])
```

The LLM does not write the database. It proposes a structured action; code validates and executes it.

## Validate

```bash
python3 scripts/validate_skill.py
```

Expected output:

```text
OK skills/llm-json-tool-runtime/SKILL.md llm-json-tool-runtime
```

## Design Boundaries

This skill is intentionally framework-level, not a full runtime implementation. It does not prescribe a specific language or model provider. Use it with Python/Pydantic, TypeScript/Zod, JSON Schema, or any equivalent typed validation stack.

Recommended invariant for projects using this skill:

```text
No adapter runs before parse + schema validation + policy check.
```

## License

MIT
