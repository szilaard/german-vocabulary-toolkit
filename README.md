# German Vocabulary Helper

A small, dependency-free Python CLI and OpenCode skill for maintaining a
personal German vocabulary list.

## Getting Started

Requires Python 3.8 or newer. Open the project in OpenCode and describe what
you want to add, review, or practise. You do not need to format the vocabulary
or run the commands yourself.

On the first vocabulary request, the toolkit creates a personal
`vocabulary.yaml` from the included example. This file is ignored by Git, so
your vocabulary stays local.

## Add Words

Tell OpenCode what you want to add. You can use German or English and add one
word or several at once.

> Add lernen to my vocabulary.

> Add appointment, reliable, and to avoid to my vocabulary.

> Add der Termin, zuverlässig, and vermeiden.

The toolkit fills in useful details such as forms, meanings, topics, and
examples.

## Topics

Words can be organized into topics such as travel, work, or education. You can
ask OpenCode to show your topics or retrieve the words from one of them.

## Learn In Sets

Sets let you learn words in batches. They are not thematic: a set simply groups
the unassigned words you have collected. New words wait for the next set until
you ask to create it.

> Create a new set.

> What will be in the next set?

> Give me set 5.

The command-line query form supports combining the same filters:

```console
python vocab.py query --set 1 --type verb
python vocab.py query --type noun --topic travel
python vocab.py query --topic travel --contains train
```

Every filter is optional, and every supplied filter must match. Repeat
`--topic` to require multiple topics. `--contains` is optional text matching
that can be combined with any other filter.

## Practise And Quiz

> Quiz me on set 5. Give me a list of English words to translate into German.
> Do not use multiple choice.

Answer with your translations and ask OpenCode to check them. You can customize
the task by changing the direction, number of words, word type, or grammar
focus. For example:

> Give me German words to translate into English.

> Give me verbs and ask for their simple past and perfect forms.

> Give me nouns without their articles and let me add the correct articles.

For a browser-based exercise, ask OpenCode to generate a practice page. The
page lets you type answers, reveal or hide the expected answer, clear your
responses, and reshuffle the questions. It is a self-contained HTML file and
does not send or save your answers anywhere.

The agent can pass question-answer pairs directly by repeating `--item`:

```console
python vocab.py practice --title "Set 1 verbs" --item "to learn" "lernen" --item "to avoid" "vermeiden"
```

By default, pages are saved with unique names under `practice/`, so generating
a new exercise does not replace an older one. The generated page opens in the
default browser automatically.

For programmatic use, the command also accepts a JSON list of objects with
`question` and `answer` fields from inline JSON, a file, or standard input.

The underlying CLI remains available for scripting. Run `python vocab.py
--help` for its commands. See `AGENTS.md` and
`.opencode/skills/german-vocabulary/SKILL.md` for the OpenCode workflow and
vocabulary conventions.
