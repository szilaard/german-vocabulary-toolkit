---
name: german-practice
description: Use when the user wants a German vocabulary practice page, exercise, test, quiz, answer-reveal UI, or wants to practise a vocabulary set, topic, or word type.
---

# German Practice

Create a browser practice page from the vocabulary selection requested by the
user. Retrieve only the relevant entries with `vocab.py query`, turn them into
concise question-answer pairs, and pass each pair directly to the practice
command. For example, set 1 verbs are retrieved with:

```console
python vocab.py query --set 1 --type verb
```

```console
python vocab.py practice --title "Set 1 verbs" --item "to learn" "lernen" --item "to avoid" "vermeiden"
```

The command opens the finished page in the user's browser. Do not pass
`--output` unless the user requests a particular location or filename; the
command automatically preserves pages in the `practice/` directory.

Follow the requested direction and exercise format. For a normal
English-to-German vocabulary exercise, use the English meaning as the question
and the German word as the answer. Keep noun articles in German answers. Do not
add, edit, or reorganize vocabulary while creating a practice page unless the
user separately asks for those changes.
