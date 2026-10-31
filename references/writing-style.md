# Writing style — artifacts are read by people

Every Markdown file a skill writes is a working document for engineers, architects and
stakeholders — not a transcript of the session that produced it. Write it the way a careful
colleague would.

## Voice

- **Plain sentences first.** Prefer a short sentence to a fragment chain. A reader should be
  able to read any paragraph aloud without stumbling over `·` separators, arrow chains, or
  symbol salad. Tables are for enumerable facts; everything that needs a *because* belongs in
  prose around them.
- **No filler.** Never pad with words that claim quality instead of showing it: *seamless*,
  *robust and scalable*, *cutting-edge*, *state-of-the-art*, *best-in-class*, *leverages*,
  *holistic*, *delve*, *utilize* (say *use*), *synergy*, *it is worth noting*, *in conclusion*.
  If a sentence survives deleting the word, delete the word. `validate.py` rejects the worst of
  these.
- **Numbers over adjectives.** "Recovers in under 60 seconds" beats "recovers quickly";
  "4 business goals, 6 scenarios" beats "a comprehensive set of drivers".
- **Bold sparingly.** Bold marks a defined term at first use or a label in a list — never
  emphasis sprinkled mid-sentence. If more than a few words per paragraph are bold, none of
  them stand out.
- **No meta-commentary.** The artifact never describes itself from the producer's point of view
  ("This file holds the ID legend…", "rendered and verified"). Template guidance stays in HTML
  comments in the template; what the reader sees is content.

## Orientation — every artifact opens with a reader's paragraph

The first thing after the header block is one to three plain sentences that answer: *what is
this, what does it cover, where should I start?* Written for someone who has never seen the SEI
method — e.g. "This register lists everything that shapes the architecture: four business
goals, four use cases… Start with the prioritised list."

## Notation is explained at first use

Shorthand is fine *after* it has been introduced, in the same file:

- `(V, R)` → say once: "business value and technical risk, each rated high/medium/low".
- `p95`, `≥ 99.5 %/mo`, `(H, H)` → spell out the first occurrence or add a one-line key.
- ID prefixes (`AQA`, `SQA`…) → a legend listing **only the prefixes in use**; the full table
  lives in the plugin, not in every artifact.

## Structure

- One idea per section; headings say what the section contains, not what activity produced it.
- Every cross-reference is a relative Markdown link the reader can click, with link text that
  says where it goes ("the [traceability matrix](#traceability-matrix)", not "see below").
- Each file ends with the Navigation footer — up to the package index, across only to packages
  that exist.
