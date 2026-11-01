---
name: deep-summary
description: >
  Turn a piece of text — an article, essay, chapter, report, transcript, or
  any long document — into one in-depth article that goes beyond surface
  summarization: it reconstructs the core thesis, traces arguments and
  evidence, surfaces hidden assumptions, and adds critical commentary.
  Use when the user asks to 总结文本、深度总结、把文本写成一篇有深度的文章、
  深度解读, or says "deep summary", "summarize this into an article/essay",
  "write an in-depth piece about this text".
---

# Deep Summary

Produce a single in-depth article from the given text. The output is not a
bullet-point digest: it is a coherent, readable article that demonstrates
understanding at three levels — what the text says, how it argues, and
whether it holds up.

## Workflow

1. **Acquire the text.** If the user points to a file or URL, read it in
   full before writing. For very long sources, read sequentially in chunks
   and keep running notes; never summarize from a partial read without
   saying so explicitly.
2. **Deconstruct.** Identify, with pointers to specific passages:
   - Core thesis and the question the text answers
   - Main arguments and their supporting evidence, data, or examples
   - Structure: how the text moves from claim to claim
   - Implicit assumptions, definitions, and framing choices
   - Limitations, counter-evidence the text ignores, open questions
3. **Outline.** Draft a layered outline before writing:
   - What the text claims (reconstruction)
   - How and why it works (mechanisms, causal chains, method)
   - Where it sits in the broader context (related ideas, implications)
   - Where it is weak or unfinished (critique, open questions)
4. **Write.** Follow the output requirements below; pick an article shape
   from [references/depth-guide.md](references/depth-guide.md).
5. **Review.** Check the draft against the quality checklist in
   [references/depth-guide.md](references/depth-guide.md), then deliver.

## Output requirements

- **Language**: match the source text's language unless the user requests
  another (Chinese input → Chinese article).
- **Length**: default 1,500–3,000 characters for Chinese, 800–1,500 words
  for English; the user may set another length.
- **Form**: Markdown article with a title and flowing prose. Section
  headings are encouraged; lists may support the prose but must never
  replace it.
- **Grounding**: every major claim about the text must be traceable to it —
  quote, paraphrase with location, or cite specific figures and data. Do
  not invent content not present in the source; mark inferences and
  judgments as your own.
- **Delivery**: paste the article in the reply. If the user asks for a
  file, save it as `<topic>-deep-summary.md` beside the source or in the
  working directory.

## Depth bar

An article that merely compresses the text is a failure. It must contain:

1. At least one section explaining *why* the text's claims hold (or fail),
   not just *what* they are.
2. At least one tension, gap, or non-obvious implication the text does not
   state explicitly.
3. A critical assessment that takes a position and defends it.
