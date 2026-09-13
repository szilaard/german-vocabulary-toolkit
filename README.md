# German Vocabulary Helper

A small, dependency-free Python CLI and OpenCode skill for maintaining a
personal German vocabulary list.

## Getting Started

Requires Python 3.8 or newer.

```bash
python vocab.py list
```

On first use, `vocab.py` creates `vocabulary.yaml` from the tracked
`vocabulary.example.yaml` template. The personal file is ignored by Git, so
vocabulary can be added without publishing it.

## Commands

```bash
python vocab.py search "WORD"
python vocab.py list
python vocab.py list noun
python vocab.py topics
python vocab.py topic "TOPIC"
python vocab.py add --type verb --word lernen --meaning "to learn" --topic education --forms "lernt; lernte; hat gelernt"
python vocab.py new-set --dry-run
python vocab.py new-set
```

Use `--file PATH` before the command to work with another vocabulary file. A
missing file is initialized from the example template.

```bash
python vocab.py --file another-vocabulary.yaml list
```

See `AGENTS.md` and `.opencode/skills/german-vocabulary/SKILL.md` for the
OpenCode workflow and vocabulary conventions.

## Publishing

The included `.gitignore` excludes personal vocabulary, Python caches, and
locally installed OpenCode packages. Before the first commit, verify the files
Git will include:

```bash
git init
git status --short
git add .
git status --short
git commit -m "Initial commit"
```

Then create an empty GitHub repository and connect it using the commands GitHub
shows, or use the GitHub CLI:

```bash
gh repo create german-vocabulary --source=. --public --push
```
