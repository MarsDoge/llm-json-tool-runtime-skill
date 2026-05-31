# Submodule Collection Pattern for JSON Tool Runtime

Use this when publishing `llm-json-tool-runtime` as an independent reusable skill while also including it in a broader skill collection such as a Five-Layer AI runtime repository.

## Recommended repository layout

Keep `llm-json-tool-runtime-skill` independent. In the collection repository, include only this repo as a git submodule:

```text
five-layer-world-collaboration-skill/
├── README.md
├── LICENSE
├── .gitmodules
├── scripts/
│   ├── install.sh
│   └── validate_skills.py
└── skills/
    ├── five-layer-world-collaboration/
    │   └── SKILL.md
    └── llm-json-tool-runtime-skill/      # git submodule
        └── skills/
            └── llm-json-tool-runtime/
                └── SKILL.md
```

Use `five-layer-world-collaboration-skill` as the public repository name. The Five-Layer skill is the repo's primary installable unit; `llm-json-tool-runtime-skill` is included only as a reusable submodule dependency for the cellular JSON executor pattern.

## README requirements

The collection README should explicitly state:

- `llm-json-tool-runtime-skill` is a git submodule.
- It is the reusable cellular execution pattern: `LLM -> JSON -> validator -> executor adapter`.
- The collection repo is the macro architecture / Five-Layer world model.
- Users should clone with submodules:

```bash
git clone --recurse-submodules https://github.com/MarsDoge/five-layer-world-collaboration-skill.git
```

If already cloned:

```bash
git submodule update --init --recursive
```

## Install script instead of symlink-dependent install

Prefer `README + scripts/install.sh` over relying on symlinks. The submodule contains the installable skill one directory deeper than collection skills, so installation needs path mapping:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$HOME/.hermes/skills/autonomous-ai-agents"
mkdir -p "$HOME/.hermes/skills/software-development"

cp -R "$ROOT/skills/five-layer-world-collaboration" \
  "$HOME/.hermes/skills/autonomous-ai-agents/five-layer-world-collaboration"

cp -R "$ROOT/skills/llm-json-tool-runtime-skill/skills/llm-json-tool-runtime" \
  "$HOME/.hermes/skills/software-development/llm-json-tool-runtime"
```

A convenience symlink such as `skills/llm-json-tool-runtime -> llm-json-tool-runtime-skill/skills/llm-json-tool-runtime` is optional for browsing, but should not be the canonical install path. Symlinks are brittle for GitHub zip downloads, Windows users, missing submodules, and platform-specific `cp -R` behavior.
