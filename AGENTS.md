 # AGENTS.md — GRID Network Wiki Protocol

## Core Directive
You are an autonomous agent working on the GRID Network Wiki project. You MUST use the **Project Manifest** and **Active Tasks** system to stay aligned. 
**NEVER** read the entire project directory. Only read files explicitly linked in the Manifest or your current task.

## Workflow: The "State Machine"

### 1. Initialization (Every Turn)
Before doing any work, read these two files:
1. `PROJECT-MANIFEST.md` (The Goal)
2. `ACTIVE-TASKS.md` (The Lock)
3. **Workspace Check**: Verify if the local workspace directory (`/Users/tron/grid-network-wiki-tool/`) exists.
   - **IF YES**: **USE IT.** Do NOT create a new one.
   - **IF NO**: Follow the `00 - GRID Network Wiki Project Plan.md` **Phase 0** instructions to create it.

**Logic:**
- Check `current_goal` in the Manifest.
- Scan `ACTIVE-TASKS.md`. 
  - If a task is `Parked` (not started) and `assignee` is `EMPTY` (or `SELF`): **Pick it up.**
  - If a task is `In Progress` (assigned to you): **Resume it.**
  - If a task is `In Progress` (assigned to another agent): **Skip it.**

### 2. Execution
1. **Read**: Open the specific task file linked in `ACTIVE-TASKS.md`.
2. **Lock**: Update `ACTIVE-TASKS.md` to set `status: In Progress` and `assignee: SELF`.
3. **Work**: Execute the steps defined in the task file.
4. **Document**: If you find new info or deviate, update the task file *before* you finish.

### 3. Completion
1. Move the task file from `TASKS/INBOX/` to `TASKS/COMPLETED/`.
2. **Update the Manifest**: 
   - Remove the task from the "Active" list.
   - If the `current_goal` is achieved, update the `current_goal` to the next phase.
3. Report: "Phase complete. New goal set to [Next Goal]."

## Context Hygiene Rules
- **DO NOT** `cat` or `ls` the `DEEP-DOCS/` folder.
- **DO** read only the specific files linked in the Manifest.
- If you find a file that looks important but isn't linked, add it to the Manifest's index for next time.

## Error Handling
If a task requires a decision not in the file, or a command fails >2 times:
1. **STOP**.
2. Mark the task `BLOCKED` in `ACTIVE-TASKS.md`.
3. Write a `REASON` in the task file.
4. Wait for human (Tron) input.

---

## Development Methodology (Embedded)

### Working Principles
1. **Functionality first.** Make the product loop work before broad feature expansion.
2. **Verify with tools.** Do not claim completion unless tests, builds, route checks, and browser/user-flow QA back it up.
3. **Use aggravated-customer testing.** Click through real flows as an impatient first-time user, not just as a developer reading code.
4. **Preserve prior feedback.** Convert feedback into checklists/runbooks so the user does not need to repeat it.
5. **Prefer data-driven demo/test identity.** Demo aliases and fixtures belong in config/seed/database layers, not hardcoded app logic.
6. **Keep master plans versioned.** Never edit the active master plan directly; create a new versioned copy if the master plan needs to change.
7. **Separate workbench from persistent testing.** CT121 is for speed; long-lived Docker test/staging goes in dedicated visible Proxmox LXCs.
8. **Build reusable templates.** If a setup will be repeated for future projects, convert it into a script, doc template, or Hermes skill reference.

### Standard Implementation Loop
1. Read the current plan/status/runbook.
2. Check repo status and baseline commands.
3. Make the smallest useful implementation step.
4. Run relevant focused tests.
5. Run full gates when appropriate:
   ```bash
   npm test
   npm run typecheck
   npm run build
   git diff --check
   ```
6. Run local/server route smoke checks.
7. Run real browser QA against the active environment.
8. Update status/runbook docs with exactly what was verified and what still fails.
9. Commit and push only after verification.
10. Record reusable lessons as skills/templates, not just chat messages.

### Phase Completion Rule
A phase is not complete unless:
- The stated user flow works in the browser.
- Automated tests cover the key regression.
- The active test environment is updated or the limitation is clearly documented.
- Docs/status say what was actually verified.
- Known gaps are listed instead of hidden.

### Feedback Capture Rule
When the user provides product feedback:
- Add it to the current testing/runbook checklist if it affects QA.
- Add it to the implementation plan/status if it affects build order.
- Create a new master-plan version only if strategic scope changes.
- Keep a concise outstanding-feedback list so future testing does not start from scratch.

### Environment Rule
Use this environment split:
- **Local Mac (`/Users/tron/grid-network-wiki-tool/`)**: **SOURCE OF TRUTH.** All code, configs, and scripts live here first.
- **CT121 `grid-dev-01`:** Shared heavy workbench, quick Docker experiments, active build/deploy work.
- **CT120 `grid-core-01`:** **PRODUCTION/STAGING ONLY.** NEVER edit files here directly during dev. Always deploy via script.
- **GitHub**: Backup and collaboration.

**CRITICAL RULE**: 
If you find yourself wanting to edit a file on CT120/CT121, you must STOP and edit it in the Local Workspace first, then deploy it. 
**NEVER** work directly on the server without a local workspace backup.

### Monitoring Rule
Every persistent Docker test/staging environment should have:
- App health endpoint.
- node_exporter.
- cAdvisor.
- Prometheus generated targets.
- Uptime Kuma monitors.
- Reset/update runbook.
- Backup/snapshot path.

See `DEEP-DOCS/docker-test-env-template.md` for details.