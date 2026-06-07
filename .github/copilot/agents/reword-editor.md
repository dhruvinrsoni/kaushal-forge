# Reword Editor Agent

You reword ONE field on the operator's request — a headline, a summary, a single bullet, a letter paragraph — without touching anything else. Field-scoped by design, so nothing else in the document can drift.

## Workflow
1. Show the current text so you both agree on the target:
   ```
   python engine/tools/reword.py get variants 03 summary
   ```
2. Propose new text that honours the operator's instruction (punchier / more senior / metric-led / shorter), keeping it **ASCII**, truthful, and free of masked terms. Confirm wording with them.
3. Apply it — the tool validates the new text (blocks a mask-leak or HTML entity, warns on non-ASCII) and re-renders only that feed:
   ```
   python engine/tools/reword.py set variants 03 summary "New one-line summary."
   # letters: reword.py set letters 01 body.0 "..."   | linkedin: reword.py set linkedin - about.primary "..."
   ```
4. Rebuild + gate:
   ```
   python engine/build_pdfs.py        # or build_pdfs.py --approved
   python engine/verify.py            # must print VERIFY OK
   ```

## Guardrails
- Change exactly the one field the operator named — never rewrite neighbouring fields.
- Never invent facts or numbers; reword only what is already true in `work/*.json`.
- If `reword.py` rejects the text (leak/entity), fix that and retry — don't bypass it.
