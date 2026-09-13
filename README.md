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

## Practise And Quiz

> Quiz me on set 5. Give me a list of English words to translate into German.
> Do not use multiple choice.

Answer with your translations and ask OpenCode to check them. You can customize
the task by changing the direction, number of words, word type, or grammar
focus. For example:

> Give me German words to translate into English.

> Give me verbs and ask for their simple past and perfect forms.

> Give me nouns without their articles and let me add the correct articles.

The underlying CLI remains available for scripting. Run `python vocab.py
--help` for its commands. See `AGENTS.md` and
`.opencode/skills/german-vocabulary/SKILL.md` for the OpenCode workflow and
vocabulary conventions.
