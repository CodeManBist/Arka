# CLAUDE.md

You are working on Blast Radius (repository: Arka).

Before implementing any feature:

1. Read:
   - ai-context/00_identity.md
   - ai-context/02_current_state.md
   - ai-context/03_architecture.md
   - ai-context/09_coding_rules.md
   - ai-context/10_task_workflow.md

2. Search the existing codebase before writing new code.

3. Reuse existing modules whenever possible.

4. Never rewrite working code.

5. Implement exactly one feature per task.

6. Keep frontend, backend, and analysis service responsibilities separate.

7. Static analysis is the source of truth.
   LLMs only explain graph-derived results.

8. After implementation:
   - update documentation
   - update roadmap
   - explain every changed file
   - list follow-up improvements

Always optimize for correctness, maintainability, and deterministic analysis over cleverness.