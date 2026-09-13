---
name: german-vocabulary
description: Use when the user wants to add, import, correct, organize, enrich, or review German words, vocabulary, phrases, nouns, verbs, or adjectives in vocabulary.yaml.
---

# German Vocabulary

Maintain `vocabulary.yaml` only through `vocab.py`. Do not read the whole file
unless the user asks for the full vocabulary, and do not sort it.

## Schema

Before adding, importing, or correcting any entry, read
`../../../vocabulary-entry.schema.json` in full. It is the authoritative entry
schema. Do not infer the schema from this skill's examples or summary, and do
not claim that `vocab.py` validates against the JSON Schema.

## Read

- Find text anywhere in an entry: `python vocab.py search "WORD"`
- Get the complete vocabulary: `python vocab.py list`
- Get one word type: `python vocab.py list noun|verb|adjective|other`
- List available topics and counts: `python vocab.py topics`
- Get one topic: `python vocab.py topic "TOPIC"`

## Sets

When the user asks to create a new set, run `python vocab.py new-set`. It finds
the highest existing `set_id`, increments it, and assigns that ID to every entry
without one. Use `python vocab.py new-set --dry-run` to preview the result.

Use `list` or `topic` to load the requested material before quizzes or practice.

## Add

After reading the schema, pass each entry directly as command arguments. The
following command is only an example, not a complete schema definition:

`python vocab.py add --type verb --word lernen --meaning "to learn" --topic education --forms "lernt; lernte; hat gelernt"`

Repeat `--topic` for multiple topics.

New entries normally omit `set_id` and are included in the next new set.

Do not create a temporary JSON file. Add multiple entries with separate
commands. JSON file paths, inline JSON, and `-` for standard input remain
supported when the user explicitly requests them.

The notes below are vocabulary conventions and usage examples. They supplement
the JSON Schema but never replace it. `vocab.py` performs its own input checks
and prevents exact duplicates.

Every entry should have one to three simple lowercase `topics`.

- Noun: include its article in `word`; include `meaning`, `topics`, `plural`,
  and `genitive`.
- Verb: include `meaning`, `topics`, and `forms` containing third-person
  singular present, simple past, and perfect, such as
  `fängt an; fing an; hat angefangen`.
- Adjective: include `meaning`, `topics`, and `forms` containing comparative
  and superlative.
- Other: include `meaning`, `topics`, and `kind`.
- Add `pattern` to verbs whenever separability, reflexive use, case, a fixed
  preposition, or another common construction can be shown usefully.
- Include a concise, natural `example_de` and matching `example_en` whenever
  possible. Prefer examples that demonstrate the word's typical usage or
  grammatical pattern rather than merely placing it in a generic sentence.
- Add `note` when it helps explain register, nuance, regional usage, common
  confusion, or a distinction not captured by the English meaning.
- Use internal knowledge for ordinary Standard German. Do not browse unless
  requested; state uncertainty instead of guessing.
