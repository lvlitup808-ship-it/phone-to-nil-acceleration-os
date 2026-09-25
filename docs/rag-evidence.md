# Evidence pipeline (RAG)

Source pattern from @techyoutbe: production RAG is not Query → Retrieve → Generate.

```
Retrieve → Judge → Filter → Assemble → Generate → Verify
                 └──────── fail? rewrite query ───────────┘
```

Used here for:

- Drill library lookup given a cue + position
- Comparable athlete cluster explanations
- NIL policy / disclaimer snippets
- Coach annotation search

## Six decisions

1. Which chunks? Hybrid vector + keyword over `drills`, `comps`, `legal`.
2. Rerank? Yes for NIL narrative, no for a single drill FAQ.
3. Which passages survive? Min score + context budget.
4. How much context? 3–8 chunks. More is not better.
5. Grounded? Every numeric NIL claim must map to a retrieved comp row.
6. Cite? Always for valuation and legal text.

If grounding fails, rewrite the query and retrieve again. Do not emit a point estimate.
