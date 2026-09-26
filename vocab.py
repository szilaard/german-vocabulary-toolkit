#!/usr/bin/env python3
"""Search, append, and group entries in vocabulary.yaml without external packages."""

import argparse
from datetime import datetime
import json
import re
import sys
import webbrowser
from pathlib import Path

from practice_page import render_practice_page

if sys.stdout.encoding:
    sys.stdout.reconfigure(encoding="utf-8")


SECTIONS = {
    "noun": "nouns",
    "verb": "verbs",
    "adjective": "adjectives",
    "other": "other",
}

FIELD_ORDER = {
    "noun": ("word", "set_id", "meaning", "topics", "plural", "genitive", "note", "example_de", "example_en"),
    "verb": ("word", "set_id", "meaning", "topics", "forms", "pattern", "note", "example_de", "example_en"),
    "adjective": ("word", "set_id", "meaning", "topics", "forms", "note", "example_de", "example_en"),
    "other": ("word", "set_id", "meaning", "topics", "kind", "note", "example_de", "example_en"),
}

REQUIRED = {
    "noun": ("word", "meaning", "topics", "plural", "genitive"),
    "verb": ("word", "meaning", "topics", "forms"),
    "adjective": ("word", "meaning", "topics", "forms"),
    "other": ("word", "meaning", "topics", "kind"),
}

DEFAULT_VOCABULARY = Path(__file__).with_name("vocabulary.yaml")
VOCABULARY_TEMPLATE = Path(__file__).with_name("vocabulary.example.yaml")
PRACTICE_DIRECTORY = Path(__file__).with_name("practice")


def entries(text):
    """Yield (section, entry text) pairs from the deliberately simple schema."""
    section = None
    block = []
    for line in text.splitlines():
        heading = re.fullmatch(r"(nouns|verbs|adjectives|other):(?: \[\])?", line)
        if heading:
            if block:
                yield section, "\n".join(block)
                block = []
            section = heading.group(1)
        elif section and line.startswith("  - "):
            if block:
                yield section, "\n".join(block)
            block = [line]
        elif block and (line.startswith("    ") or not line.strip()):
            if line.strip():
                block.append(line)
    if block:
        yield section, "\n".join(block)


def entry_word(block):
    match = re.search(r'^  - word: (.+)$', block, re.MULTILINE)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return match.group(1).strip("'\"")


def entry_topics(block):
    match = re.search(r'^    topics: (.+)$', block, re.MULTILINE)
    if not match:
        return []
    try:
        value = json.loads(match.group(1))
        return value if isinstance(value, list) else []
    except json.JSONDecodeError:
        return []


def entry_set_id(block):
    match = re.search(r'^    set_id: (.+)$', block, re.MULTILINE)
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid set_id: {match.group(1)}") from error
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise SystemExit(f"set_id must be a positive integer: {match.group(1)}")
    return value


def print_entries(matches):
    if not matches:
        print("No matches.")
        return
    previous_section = None
    for section, block in matches:
        if section != previous_section:
            if previous_section is not None:
                print()
            print(f"{section}:")
            previous_section = section
        print(block)


def search(path, query):
    text = path.read_text(encoding="utf-8")
    matches = [(section, block) for section, block in entries(text) if query.casefold() in block.casefold()]
    print_entries(matches)


def list_entries(path, kind=None):
    selected_section = SECTIONS[kind] if kind else None
    matches = [
        (section, block)
        for section, block in entries(path.read_text(encoding="utf-8"))
        if selected_section is None or section == selected_section
    ]
    print_entries(matches)


def query_entries(path, kind=None, set_id=None, topics=None, contains=None):
    """Print entries matching every supplied filter."""
    selected_section = SECTIONS[kind] if kind else None
    topic_keys = {topic.casefold() for topic in topics or []}
    matches = []
    for section, block in entries(path.read_text(encoding="utf-8")):
        if selected_section is not None and section != selected_section:
            continue
        if set_id is not None and entry_set_id(block) != set_id:
            continue
        entry_topic_keys = {topic.casefold() for topic in entry_topics(block)}
        if not topic_keys.issubset(entry_topic_keys):
            continue
        if contains is not None and contains.casefold() not in block.casefold():
            continue
        matches.append((section, block))
    print_entries(matches)


def list_topics(path):
    topic_counts = {}
    for _, block in entries(path.read_text(encoding="utf-8")):
        for topic in entry_topics(block):
            key = topic.casefold()
            label, count = topic_counts.get(key, (topic, 0))
            topic_counts[key] = (label, count + 1)
    if not topic_counts:
        print("No topics.")
        return
    for label, count in sorted(topic_counts.values(), key=lambda item: item[0].casefold()):
        print(f"{label} ({count})")


def find_topic(path, topic):
    key = topic.casefold()
    matches = [
        (section, block)
        for section, block in entries(path.read_text(encoding="utf-8"))
        if any(value.casefold() == key for value in entry_topics(block))
    ]
    print_entries(matches)


def append_entry(path, kind, values):
    text = path.read_text(encoding="utf-8")
    section = SECTIONS[kind]
    word = values["word"]

    for existing_section, block in entries(text):
        if existing_section == section and (entry_word(block) or "").casefold() == word.casefold():
            raise SystemExit(f'Entry already exists in {section}: {word}')

    block = []
    for field in FIELD_ORDER[kind]:
        value = values.get(field)
        if value:
            prefix = "  - " if not block else "    "
            block.append(f"{prefix}{field}: {json.dumps(value, ensure_ascii=False)}")

    lines = text.splitlines()
    heading_index = next(
        (i for i, line in enumerate(lines) if re.fullmatch(rf"{section}:(?: \[\])?", line)),
        None,
    )
    if heading_index is None:
        raise SystemExit(f"Missing section in {path}: {section}")

    if lines[heading_index] == f"{section}: []":
        lines[heading_index] = f"{section}:"
        insert_at = heading_index + 1
    else:
        insert_at = len(lines)
        for i in range(heading_index + 1, len(lines)):
            if re.fullmatch(r"(nouns|verbs|adjectives|other):(?: \[\])?", lines[i]):
                insert_at = i
                break
        while insert_at > heading_index + 1 and not lines[insert_at - 1].strip():
            insert_at -= 1

    separator = [""] if insert_at < len(lines) and lines[insert_at].strip() else []
    lines[insert_at:insert_at] = block + separator
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f'Added {word} to {section}.')


def create_set(path, dry_run=False):
    text = path.read_text(encoding="utf-8")
    parsed_entries = list(entries(text))
    assigned_ids = [entry_set_id(block) for _, block in parsed_entries]
    unassigned = [(section, block) for section, block in parsed_entries if entry_set_id(block) is None]
    if not unassigned:
        print("No unassigned entries.")
        return

    set_id = max((value for value in assigned_ids if value is not None), default=0) + 1
    if dry_run:
        print(f"Set {set_id} would be assigned to {len(unassigned)} unassigned entries.")
        return

    for _, block in unassigned:
        updated_block = re.sub(r'^(  - word: .+\n)', rf'\1    set_id: {set_id}\n', block, count=1)
        text = text.replace(block, updated_block, 1)
    path.write_text(text, encoding="utf-8")
    print(f"Created set {set_id} and assigned it to {len(unassigned)} entries.")


def validate_entry(value, index):
    label = f"entry {index}"
    if not isinstance(value, dict):
        raise SystemExit(f"{label} must be a JSON object")

    kind = value.get("type")
    if not isinstance(kind, str) or kind not in SECTIONS:
        raise SystemExit(f"{label}.type must be one of: {', '.join(SECTIONS)}")

    allowed = {"type", *FIELD_ORDER[kind]}
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise SystemExit(f"{label} has unknown fields: {', '.join(unknown)}")

    missing = [field for field in REQUIRED[kind] if not value.get(field)]
    if missing:
        raise SystemExit(f"{label} requires: {', '.join(missing)}")

    invalid = [
        field
        for field, field_value in value.items()
        if (
            field == "topics"
            and (
                not isinstance(field_value, list)
                or not field_value
                or any(not isinstance(topic, str) or not topic for topic in field_value)
            )
        )
        or (field == "set_id" and (isinstance(field_value, bool) or not isinstance(field_value, int) or field_value < 1))
        or (field not in {"topics", "set_id"} and not isinstance(field_value, str))
    ]
    if invalid:
        raise SystemExit(f"{label} has invalid fields: {', '.join(invalid)}")

    return kind, {field: value.get(field) for field in FIELD_ORDER[kind]}


def initialize_vocabulary(path):
    if path.exists():
        return
    try:
        path.write_text(VOCABULARY_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    except OSError as error:
        raise SystemExit(f"Could not initialize {path}: {error}") from error
    print(f"Initialized {path} from {VOCABULARY_TEMPLATE.name}.", file=sys.stderr)


def read_json_argument(value):
    """Read JSON from an inline value, a file path, or standard input."""
    try:
        if value == "-":
            raw = sys.stdin.read()
        elif value.lstrip().startswith(("{", "[")):
            raw = value
        else:
            raw = Path(value).read_text(encoding="utf-8")
        return json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Could not read JSON input: {error}") from error


def practice_output_path(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-") or "practice"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output = PRACTICE_DIRECTORY / f"{timestamp}-{slug}.html"
    suffix = 2
    while output.exists():
        output = PRACTICE_DIRECTORY / f"{timestamp}-{slug}-{suffix}.html"
        suffix += 1
    return output


def create_practice_page(payload, title, output=None):
    if not isinstance(payload, list) or not payload:
        raise SystemExit("Practice input must be a non-empty JSON array")

    questions = []
    for index, item in enumerate(payload, 1):
        if not isinstance(item, dict) or set(item) != {"question", "answer"}:
            raise SystemExit(f"practice question {index} must contain only: question, answer")
        if any(not isinstance(item[field], str) or not item[field].strip() for field in ("question", "answer")):
            raise SystemExit(f"practice question {index} requires non-empty question and answer strings")
        questions.append({"question": item["question"].strip(), "answer": item["answer"].strip()})

    output = output or practice_output_path(title)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_practice_page(title, questions), encoding="utf-8")
    except OSError as error:
        raise SystemExit(f"Could not write practice page: {error}") from error
    label = "question" if len(questions) == 1 else "questions"
    print(f"Created practice page with {len(questions)} {label}: {output}")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_VOCABULARY)
    commands = parser.add_subparsers(dest="command", required=True)

    search_parser = commands.add_parser("search", help="print entries containing a term")
    search_parser.add_argument("query")

    list_parser = commands.add_parser("list", help="print the complete vocabulary or one word type")
    list_parser.add_argument("kind", nargs="?", choices=SECTIONS)

    query_parser = commands.add_parser("query", help="print entries matching all supplied optional filters")
    query_parser.add_argument("--set", dest="set_id", type=int, help="match a set ID")
    query_parser.add_argument("--type", dest="kind", choices=SECTIONS, help="match a word type")
    query_parser.add_argument("--topic", action="append", help="match a topic; repeat to require multiple topics")
    query_parser.add_argument("--contains", help="match text anywhere in an entry")

    commands.add_parser("topics", help="list topics with entry counts")

    new_set_parser = commands.add_parser("new-set", help="assign the next set ID to all unassigned entries")
    new_set_parser.add_argument("--dry-run", action="store_true", help="show the next set ID without changing the file")

    topic_parser = commands.add_parser("topic", help="print all entries in a topic")
    topic_parser.add_argument("name")

    practice_parser = commands.add_parser("practice", help="generate a practice page from question-answer pairs")
    practice_parser.add_argument("input", nargs="?", help="inline JSON, a JSON file, or - for standard input")
    practice_parser.add_argument(
        "--item",
        nargs=2,
        action="append",
        metavar=("QUESTION", "ANSWER"),
        help="add a question-answer pair; may be repeated",
    )
    practice_parser.add_argument("--title", default="Vocabulary Practice")
    practice_parser.add_argument("--output", type=Path)

    add_parser = commands.add_parser("add", help="append entries from arguments or JSON")
    add_parser.add_argument("input", nargs="?", help="inline JSON, a JSON file, or - for standard input")
    add_parser.add_argument("--type", dest="entry_type", choices=SECTIONS)
    add_parser.add_argument("--word")
    add_parser.add_argument("--meaning")
    add_parser.add_argument("--topic", dest="topics", action="append")
    add_parser.add_argument("--set-id", type=int)
    for field in ("plural", "genitive", "forms", "pattern", "kind", "note", "example_de", "example_en"):
        add_parser.add_argument(f"--{field.replace('_', '-')}")

    args = parser.parse_args()
    initialize_vocabulary(args.file)
    if args.command == "search":
        search(args.file, args.query)
        return
    if args.command == "list":
        list_entries(args.file, args.kind)
        return
    if args.command == "query":
        query_entries(args.file, args.kind, args.set_id, args.topic, args.contains)
        return
    if args.command == "topics":
        list_topics(args.file)
        return
    if args.command == "new-set":
        create_set(args.file, args.dry_run)
        return
    if args.command == "topic":
        find_topic(args.file, args.name)
        return
    if args.command == "practice":
        if (args.input is None) == (args.item is None):
            raise SystemExit("Provide either JSON input or one or more --item pairs")
        payload = (
            read_json_argument(args.input)
            if args.input is not None
            else [{"question": question, "answer": answer} for question, answer in args.item]
        )
        output = create_practice_page(payload, args.title, args.output)
        webbrowser.open(output.resolve().as_uri())
        return

    argument_fields = {
        "type": args.entry_type,
        "word": args.word,
        "set_id": args.set_id,
        "meaning": args.meaning,
        "topics": args.topics,
        "plural": args.plural,
        "genitive": args.genitive,
        "forms": args.forms,
        "pattern": args.pattern,
        "kind": args.kind,
        "note": args.note,
        "example_de": args.example_de,
        "example_en": args.example_en,
    }
    supplied_fields = {field: value for field, value in argument_fields.items() if value is not None}

    if args.input is not None and supplied_fields:
        raise SystemExit("Use either direct entry arguments or JSON input, not both")

    if args.input is None:
        payload = supplied_fields
    else:
        payload = read_json_argument(args.input)

    items = payload if isinstance(payload, list) else [payload]
    if not items:
        raise SystemExit("JSON input contains no entries")
    validated = [validate_entry(item, index) for index, item in enumerate(items, start=1)]
    for kind, values in validated:
        append_entry(args.file, kind, values)


if __name__ == "__main__":
    main()
