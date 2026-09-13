# German Vocabulary Project

Maintain `vocabulary.yaml` only through `vocab.py`; do not edit or sort the
YAML file directly.

## Vocabulary Commands

- Search entries: `python vocab.py search "WORD"`
- List every entry: `python vocab.py list`
- List one type: `python vocab.py list noun|verb|adjective|other`
- List topics and their entry counts: `python vocab.py topics`
- List entries in a topic: `python vocab.py topic "TOPIC"`
- Add an entry: `python vocab.py add --type TYPE --word WORD --meaning MEANING --topic TOPIC ...`
- Preview a new set: `python vocab.py new-set --dry-run`
- Create a new set: `python vocab.py new-set`

## Sets

Run `python vocab.py new-set` only when the user explicitly asks to create a
new vocabulary set. Do not create a set automatically after adding entries or
because unassigned entries exist.

The command finds the highest existing integer `set_id`, increments it, and
assigns that ID to every entry without one. New entries normally omit `set_id`
and are included in the next explicitly requested set.

Use `python vocab.py new-set --dry-run` to preview the result without changing
the vocabulary.

## Skills

Use the `german-vocabulary` skill for requests to add, import, correct,
organize, enrich, or review German vocabulary. It contains the entry schema,
required fields, vocabulary conventions, and safe command workflow.

Use any other available specialized skill when its description matches the
request. The currently relevant project skill is `german-vocabulary`.
