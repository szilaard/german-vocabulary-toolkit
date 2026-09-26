"""Render a self-contained vocabulary practice page."""

import html
import json
import re


PAGE_TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <style>
    :root {
      color-scheme: light;
      --paper: #f4efe3;
      --card: #fffdf7;
      --ink: #202824;
      --muted: #6f756f;
      --line: #d8d2c4;
      --accent: #c44932;
      --answer: #25685b;
      --shadow: 0 18px 45px rgba(52, 45, 34, 0.1);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at 8% 2%, rgba(196, 73, 50, 0.12), transparent 24rem),
        linear-gradient(90deg, transparent 0 4.8rem, rgba(196, 73, 50, 0.2) 4.8rem 4.9rem, transparent 4.9rem),
        var(--paper);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    button, input { font: inherit; }

    .shell {
      width: min(920px, calc(100% - 2rem));
      margin: 0 auto;
      padding: 4.5rem 0 7rem;
    }

    header {
      display: grid;
      grid-template-columns: 1fr auto;
      align-items: end;
      gap: 2rem;
      margin-bottom: 2rem;
    }

    .eyebrow {
      margin: 0 0 0.55rem;
      color: var(--accent);
      font-size: 0.73rem;
      font-weight: 800;
      letter-spacing: 0.16em;
      text-transform: uppercase;
    }

    h1 {
      max-width: 680px;
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(2.45rem, 7vw, 5rem);
      font-weight: 500;
      letter-spacing: -0.055em;
      line-height: 0.95;
    }

    .count {
      color: var(--muted);
      font-size: 0.9rem;
      white-space: nowrap;
    }

    .toolbar {
      position: sticky;
      top: 0.75rem;
      z-index: 10;
      display: flex;
      flex-wrap: wrap;
      gap: 0.55rem;
      align-items: center;
      margin-bottom: 1rem;
      padding: 0.7rem;
      border: 1px solid rgba(216, 210, 196, 0.9);
      border-radius: 16px;
      background: rgba(255, 253, 247, 0.88);
      box-shadow: 0 8px 28px rgba(52, 45, 34, 0.08);
      backdrop-filter: blur(14px);
    }

    .progress {
      margin-right: auto;
      padding: 0 0.55rem;
      color: var(--muted);
      font-size: 0.84rem;
      font-weight: 650;
    }

    .tool, .reveal {
      border: 1px solid var(--line);
      border-radius: 10px;
      color: var(--ink);
      background: transparent;
      cursor: pointer;
      font-weight: 720;
      transition: border-color 150ms ease, background 150ms ease, transform 150ms ease;
    }

    .tool {
      min-height: 2.5rem;
      padding: 0.55rem 0.8rem;
      font-size: 0.78rem;
    }

    .tool:hover, .reveal:hover {
      border-color: var(--ink);
      background: rgba(32, 40, 36, 0.04);
    }

    .tool:active, .reveal:active { transform: translateY(1px); }
    .tool:disabled { cursor: default; opacity: 0.38; }

    .cards {
      display: grid;
      gap: 0.8rem;
    }

    .card {
      position: relative;
      display: grid;
      grid-template-columns: 2.2rem 1fr;
      gap: 0.8rem;
      padding: 1.25rem 1.35rem 1.3rem 1rem;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--card);
      box-shadow: var(--shadow);
      animation: enter 320ms both;
    }

    .card::after {
      position: absolute;
      inset: 0 auto 0 0;
      width: 4px;
      background: var(--accent);
      content: "";
      opacity: 0;
      transition: opacity 160ms ease;
    }

    .card:focus-within::after { opacity: 1; }

    .card.is-known::after {
      background: var(--answer);
      opacity: 1;
    }

    .number {
      padding-top: 0.22rem;
      color: var(--accent);
      font-family: Georgia, "Times New Roman", serif;
      font-size: 1rem;
      font-variant-numeric: tabular-nums;
    }

    .question {
      margin: 0 0 0.95rem;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(1.2rem, 3vw, 1.55rem);
      line-height: 1.25;
    }

    .response-row {
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 0.65rem;
    }

    .response {
      min-width: 0;
      height: 2.85rem;
      padding: 0 0.85rem;
      border: 1px solid var(--line);
      border-radius: 10px;
      outline: none;
      color: var(--ink);
      background: #fff;
      transition: border-color 150ms ease, box-shadow 150ms ease;
    }

    .response:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(196, 73, 50, 0.12);
    }

    .response::placeholder { color: #aaa79f; }

    .reveal {
      min-width: 5.3rem;
      padding: 0.55rem 0.85rem;
      background: var(--ink);
      color: var(--card);
      border-color: var(--ink);
      font-size: 0.79rem;
    }

    .reveal:hover { background: #36413b; color: #fff; }

    .known-toggle {
      min-width: 6.8rem;
      padding: 0.55rem 0.85rem;
      border: 1px solid var(--line);
      border-radius: 10px;
      color: var(--ink);
      background: transparent;
      cursor: pointer;
      font-size: 0.79rem;
      font-weight: 720;
      transition: border-color 150ms ease, background 150ms ease, color 150ms ease, transform 150ms ease;
    }

    .known-toggle:hover {
      border-color: var(--answer);
      background: rgba(37, 104, 91, 0.06);
    }

    .known-toggle[aria-pressed="true"] {
      border-color: var(--answer);
      color: #fff;
      background: var(--answer);
    }

    .known-toggle:active { transform: translateY(1px); }

    .answer {
      margin-top: 0.8rem;
      padding: 0.85rem 1rem;
      border-left: 3px solid var(--answer);
      border-radius: 0 9px 9px 0;
      color: #174d43;
      background: #e9f2ec;
      white-space: pre-wrap;
      line-height: 1.45;
    }

    .answer[hidden] { display: none; }

    .answer-label {
      display: block;
      margin-bottom: 0.2rem;
      color: var(--answer);
      font-size: 0.68rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }

    @keyframes enter {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 620px) {
      body {
        background:
          radial-gradient(circle at 8% 2%, rgba(196, 73, 50, 0.11), transparent 18rem),
          var(--paper);
      }

      .shell { width: min(100% - 1rem, 920px); padding-top: 2.5rem; }
      header { grid-template-columns: 1fr; gap: 0.8rem; }
      .toolbar { top: 0.35rem; }
      .progress { width: 100%; padding-bottom: 0.15rem; }
      .card { grid-template-columns: 1.7rem 1fr; padding-right: 0.85rem; }
      .response-row { grid-template-columns: 1fr; }
      .reveal, .known-toggle { width: 100%; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { scroll-behavior: auto !important; animation: none !important; transition: none !important; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <div>
        <p class="eyebrow">German practice</p>
        <h1>__TITLE__</h1>
      </div>
      <div class="count" id="question-count"></div>
    </header>

    <nav class="toolbar" aria-label="Practice controls">
      <span class="progress" id="progress">0 answered</span>
      <button class="tool" id="hide-all" type="button">Hide answers</button>
      <button class="tool" id="clear-all" type="button">Clear answers</button>
      <button class="tool" id="clear-known" type="button">Clear known</button>
      <button class="tool" id="reshuffle" type="button">Reshuffle</button>
    </nav>

    <section class="cards" id="cards" aria-label="Practice questions"></section>
  </main>

  <script>
    const questions = __QUESTIONS__;
    const responses = new Map();
    const revealed = new Set();
    const knownItems = new Set();
    let order = questions.map((_, index) => index);

    const cards = document.querySelector("#cards");
    const progress = document.querySelector("#progress");
    const hideAll = document.querySelector("#hide-all");
    const clearAll = document.querySelector("#clear-all");
    const clearKnown = document.querySelector("#clear-known");

    document.querySelector("#question-count").textContent =
      `${questions.length} ${questions.length === 1 ? "question" : "questions"}`;

    function updateControls() {
      const answered = [...responses.values()].filter(value => value.trim()).length;
      progress.textContent = `${answered} answered | ${knownItems.size} known`;
      hideAll.disabled = revealed.size === 0;
      clearAll.disabled = answered === 0;
      clearKnown.disabled = knownItems.size === 0;
    }

    function render() {
      cards.replaceChildren();

      order.forEach((questionIndex, displayIndex) => {
        const item = questions[questionIndex];
        const card = document.createElement("article");
        card.className = "card";
        card.style.animationDelay = `${Math.min(displayIndex * 28, 280)}ms`;

        const number = document.createElement("div");
        number.className = "number";
        number.textContent = String(displayIndex + 1).padStart(2, "0");

        const content = document.createElement("div");
        const question = document.createElement("p");
        question.className = "question";
        question.textContent = item.question;

        const responseRow = document.createElement("div");
        responseRow.className = "response-row";

        const input = document.createElement("input");
        input.className = "response";
        input.type = "text";
        input.value = responses.get(questionIndex) || "";
        input.placeholder = "Type the German answer";
        input.autocomplete = "off";
        input.spellcheck = false;
        input.setAttribute("aria-label", `Your answer for ${item.question}`);
        input.addEventListener("input", () => {
          responses.set(questionIndex, input.value);
          updateControls();
        });

        const answerId = `answer-${questionIndex}`;
        const reveal = document.createElement("button");
        reveal.className = "reveal";
        reveal.type = "button";
        reveal.setAttribute("aria-controls", answerId);

        const knownToggle = document.createElement("button");
        knownToggle.className = "known-toggle";
        knownToggle.type = "button";

        function syncKnown() {
          const isKnown = knownItems.has(questionIndex);
          card.classList.toggle("is-known", isKnown);
          knownToggle.textContent = isKnown ? "Known" : "Mark known";
          knownToggle.setAttribute("aria-pressed", String(isKnown));
        }

        knownToggle.addEventListener("click", () => {
          if (knownItems.has(questionIndex)) knownItems.delete(questionIndex);
          else knownItems.add(questionIndex);
          syncKnown();
          updateControls();
        });

        const answer = document.createElement("div");
        answer.className = "answer";
        answer.id = answerId;
        const label = document.createElement("span");
        label.className = "answer-label";
        label.textContent = "Answer";
        const answerText = document.createElement("span");
        answerText.textContent = item.answer;
        answer.append(label, answerText);

        function syncReveal() {
          const isRevealed = revealed.has(questionIndex);
          answer.hidden = !isRevealed;
          reveal.textContent = isRevealed ? "Hide" : "Reveal";
          reveal.setAttribute("aria-expanded", String(isRevealed));
        }

        reveal.addEventListener("click", () => {
          if (revealed.has(questionIndex)) revealed.delete(questionIndex);
          else revealed.add(questionIndex);
          syncReveal();
          updateControls();
        });

        syncReveal();
        syncKnown();
        responseRow.append(input, reveal, knownToggle);
        content.append(question, responseRow, answer);
        card.append(number, content);
        cards.append(card);
      });

      updateControls();
    }

    hideAll.addEventListener("click", () => {
      revealed.clear();
      render();
    });

    clearAll.addEventListener("click", () => {
      responses.clear();
      render();
      cards.querySelector("input")?.focus();
    });

    clearKnown.addEventListener("click", () => {
      knownItems.clear();
      render();
    });

    document.querySelector("#reshuffle").addEventListener("click", () => {
      function shuffle(items) {
        for (let index = items.length - 1; index > 0; index -= 1) {
          const target = Math.floor(Math.random() * (index + 1));
          [items[index], items[target]] = [items[target], items[index]];
        }
        return items;
      }

      const unknown = order.filter(questionIndex => !knownItems.has(questionIndex));
      const known = order.filter(questionIndex => knownItems.has(questionIndex));
      order = [...shuffle(unknown), ...shuffle(known)];
      render();
    });

    render();
  </script>
</body>
</html>
'''


def render_practice_page(title, questions):
    """Return a complete HTML document for the supplied questions."""
    question_json = json.dumps(questions, ensure_ascii=False).replace("<", "\\u003c")
    replacements = {"__TITLE__": html.escape(title), "__QUESTIONS__": question_json}
    return re.sub(r"__TITLE__|__QUESTIONS__", lambda match: replacements[match.group()], PAGE_TEMPLATE)
