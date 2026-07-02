# Phase 8: Change Kanban Workflow

**Goal**: Build change management workflow where agents submit changes and Tron reviews them.

**Estimated Effort**: 2-3 hours

**Dependencies**: Phase 7 complete

**Acceptance Criteria**:
- Change submission working
- Dashboard kanban board integration
- User flagging functional
- Change approval/rejection workflow
- Dashboard integration for change kanban

---

## Task 8.1: Change Submission

**Target**: Create change card template and submission logic

**Steps**:
1. Create change card template: `/srv/grid-wiki/wiki-templates/change-card.md`
   ```markdown
   ---
   title: "<Change Summary>"
   type: change
   status: pending
   submitted: "2026-06-28T00:00:00Z"
   reviewed: null
   risk: low|medium|high
   ---

   # <Change Summary>

   ## Proposed Change
   <What will change>

   ## Rationale
   <Why this change is needed>

   ## Evidence
   <Discovery output, logs, or context>

   ## Impact Assessment
   - **Services affected**: <list>
   - **Downtime required**: <yes/no>
   - **Rollback procedure**: <brief>

   ## Review Notes
   <Reviewer comments>

   ## Approval
   <Approved by: Tron / Auto-approved>
   ```

2. Create change submission script: `/srv/grid-wiki/cron/submit-change.sh`
   ```bash
   #!/bin/bash
   # Submit change card to change-kanban

   set -euo pipefail

   TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   CHANGE_KANBAN_DIR="/srv/grid-wiki/change-kanban/pending"
   CHANGE_CARD_TEMPLATE="/srv/grid-wiki/wiki-templates/change-card.md"

   # Get change details from arguments
   CHANGE_SUMMARY="${1:-}"
   CHANGE_RATIONALE="${2:-}"
   CHANGE_EVIDENCE="${3:-}"
   CHANGE_SERVICES="${4:-}"
   CHANGE_DOWNTIME="${5:-}"
   CHANGE_ROLLBACK="${6:-}"

   if [ -z "$CHANGE_SUMMARY" ]; then
     echo "Error: Change summary required"
     exit 1
   fi

   # Generate change card
   cat > "$CHANGE_KANBAN_DIR/$(date +%Y%m%d-%H%M%S)-$CHANGE_SUMMARY.md" << EOF
   ---
   title: "$CHANGE_SUMMARY"
   type: change
   status: pending
   submitted: "$TIMESTAMP"
   reviewed: null
   risk: medium
   ---

   # $CHANGE_SUMMARY

   ## Proposed Change
   $CHANGE_SUMMARY

   ## Rationale
   $CHANGE_RATIONALE

   ## Evidence
   $CHANGE_EVIDENCE

   ## Impact Assessment
   - **Services affected**: $CHANGE_SERVICES
   - **Downtime required**: $CHANGE_DOWNTIME
   - **Rollback procedure**: $CHANGE_ROLLBACK

   ## Review Notes
   <Reviewer comments>

   ## Approval
   <Approved by: Tron / Auto-approved>
   EOF

   echo "Change card created: $CHANGE_SUMMARY"

   exit 0
   ```
3. Make executable: `chmod +x /srv/grid-wiki/cron/submit-change.sh`
4. Test locally: `./cron/submit-change.sh "Test Change" "Test rationale" "Test evidence" "Test services" "No" "Test rollback"`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./cron/submit-change.sh \"Test Change\" \"Test rationale\" \"Test evidence\" \"Test services\" \"No\" \"Test rollback\"'"
ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/change-kanban/pending/"
```

**Output Files**:
- `/srv/grid-wiki/wiki-templates/change-card.md`
- `/srv/grid-wiki/cron/submit-change.sh`
- `/srv/grid-wiki/change-kanban/pending/*.md` (new change cards)

---

## Task 8.2: Dashboard Integration

**Target**: Add Change Kanban board to dashboard

**Steps**:
1. Update dashboard.js to render change kanban:
   ```javascript
   async renderChangeKanban() {
     try {
       const response = await fetch('/api/kanban/changes');
       const changes = await response.json();

       this.content.innerHTML = `
         <div class="card">
           <h3>Change Kanban</h3>
           <div class="kanban-board">
             <div class="kanban-column">
               <h4>Pending</h4>
               <div class="kanban-cards">
                 ${changes.filter(c => c.status === 'pending').map(change => `
                   <div class="kanban-card">
                     <strong>${change.title}</strong>
                     <p>${change.risk}</p>
                     <button class="btn btn-primary" onclick="approveChange('${change.id}')">Approve</button>
                     <button class="btn btn-secondary" onclick="rejectChange('${change.id}')">Reject</button>
                   </div>
                 `).join('')}
               </div>
             </div>
             <div class="kanban-column">
               <h4>Approved</h4>
               <div class="kanban-cards">
                 ${changes.filter(c => c.status === 'approved').map(change => `
                   <div class="kanban-card">
                     <strong>${change.title}</strong>
                     <p>${change.risk}</p>
                   </div>
                 `).join('')}
               </div>
             </div>
             <div class="kanban-column">
               <h4>Rejected</h4>
               <div class="kanban-cards">
                 ${changes.filter(c => c.status === 'rejected').map(change => `
                   <div class="kanban-card">
                     <strong>${change.title}</strong>
                     <p>${change.risk}</p>
                   </div>
                 `).join('')}
               </div>
             </div>
           </div>
         </div>
       `;
     } catch (error) {
       console.error('Error loading change kanban:', error);
     }
   }

   async approveChange(cardId) {
     try {
       await WikiAPI.approveChange(cardId);
       this.renderChangeKanban();
       this.showNotification('Change approved!');
     } catch (error) {
       console.error('Error approving change:', error);
       this.showNotification('Error approving change', 'error');
     }
   }

   async rejectChange(cardId) {
     try {
       await WikiAPI.rejectChange(cardId);
       this.renderChangeKanban();
       this.showNotification('Change rejected!');
     } catch (error) {
       console.error('Error rejecting change:', error);
       this.showNotification('Error rejecting change', 'error');
     }
   }
   ```
2. Deploy to CT120 and test

**Verification**:
- Change kanban board loads
- Approve/reject buttons work
- Cards move between columns

**Output Files**:
- `/srv/grid-wiki/dashboard/js/dashboard.js` (updated)

---

## Task 8.3: User Flagging

**Target**: Add user flagging to change cards

**Steps**:
1. Update change card template to include user flagging:
   ```markdown
   ---
   title: "<Change Summary>"
   type: change
   status: pending
   submitted: "2026-06-28T00:00:00Z"
   reviewed: null
   risk: low|medium|high
   user_flags: []
   ---

   # <Change Summary>

   ## Proposed Change
   <What will change>

   ## Rationale
   <Why this change is needed>

   ## Evidence
   <Discovery output, logs, or context>

   ## Impact Assessment
   - **Services affected**: <list>
   - **Downtime required**: <yes/no>
   - **Rollback procedure**: <brief>

   ## User Flags
   <User-reported flags>

   ## Review Notes
   <Reviewer comments>

   ## Approval
   <Approved by: Tron / Auto-approved>
   ```
2. Update dashboard.js to add flagging:
   ```javascript
   async flagChange(cardId, flag) {
     try {
       const response = await fetch(`/api/kanban/changes/${cardId}/flag`, {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json'
         },
         body: JSON.stringify({ flag })
       });
       const result = await response.json();
       this.renderChangeKanban();
       this.showNotification('Flag added!');
     } catch (error) {
       console.error('Error flagging change:', error);
       this.showNotification('Error flagging change', 'error');
     }
   }
   ```
3. Deploy to CT120 and test

**Verification**:
- User can flag changes
- Flags appear on change cards
- Flags feed into kanban

**Output Files**:
- `/srv/grid-wiki/wiki-templates/change-card.md` (updated)
- `/srv/grid-wiki/dashboard/js/dashboard.js` (updated)

---

## Task 8.4: Dashboard Integration for Maintenance Kanban

**Target**: Add Maintenance Kanban board to dashboard

**Steps**:
1. Update dashboard.js to render maintenance kanban:
   ```javascript
   async renderMaintenanceKanban() {
     try {
       const response = await fetch('/api/kanban/maintenance');
       const maintenance = await response.json();

       this.content.innerHTML = `
         <div class="card">
           <h3>Maintenance Kanban</h3>
           <div class="kanban-board">
             <div class="kanban-column">
               <h4>Open</h4>
               <div class="kanban-cards">
                 ${maintenance.filter(m => m.status === 'open').map(m => `
                   <div class="kanban-card">
                     <strong>${m.title}</strong>
                     <p>${m.severity}</p>
                     <button class="btn btn-primary" onclick="resolveMaintenance('${m.id}')">Resolve</button>
                   </div>
                 `).join('')}
               </div>
             </div>
             <div class="kanban-column">
               <h4>Resolved</h4>
               <div class="kanban-cards">
                 ${maintenance.filter(m => m.status === 'resolved').map(m => `
                   <div class="kanban-card">
                     <strong>${m.title}</strong>
                     <p>${m.severity}</p>
                   </div>
                 `).join('')}
               </div>
             </div>
           </div>
         </div>
       `;
     } catch (error) {
       console.error('Error loading maintenance kanban:', error);
     }
   }

   async resolveMaintenance(cardId) {
     try {
       await WikiAPI.resolveMaintenance(cardId);
       this.renderMaintenanceKanban();
       this.showNotification('Maintenance resolved!');
     } catch (error) {
       console.error('Error resolving maintenance:', error);
       this.showNotification('Error resolving maintenance', 'error');
     }
   }
   ```
2. Deploy to CT120 and test

**Verification**:
- Maintenance kanban board loads
- Resolve button works
- Cards move between columns

**Output Files**:
- `/srv/grid-wiki/dashboard/js/dashboard.js` (updated)

---

## Task 8.5: Update Project Manifest

**Target**: Mark Phase 8 complete in PROJECT-MANIFEST.md

**Steps**:
1. Read current `PROJECT-MANIFEST.md`
2. Update `current_goal` to "Phase 9: Agent Knowledge Base Enhancement"
3. Add Phase 8 to `completed_phases` list
4. Commit changes: `git add . && git commit -m "Phase 8 complete"`

**Verification**:
```bash
cat /Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md | grep -A 2 "current_goal"
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md` (updated)

---

## Task 8.6: Document Phase 8 Completion

**Target**: Create Phase 8 completion report

**Steps**:
1. Create `/srv/grid-wiki/raw/live-state/phase-8-completion.md`
2. Document:
   - Change submission working
   - Dashboard kanban board integration
   - User flagging functional
   - Change approval/rejection workflow
3. Commit to git: `git add . && git commit -m "Phase 8 completion report"`

**Verification**:
```bash
cat /srv/grid-wiki/raw/live-state/phase-8-completion.md
```

**Output Files**:
- `/srv/grid-wiki/raw/live-state/phase-8-completion.md`

---

## Summary

**Total Tasks**: 6
**Estimated Time**: 2-3 hours
**Files Created**: 2
**Directories Created**: 0
**Kanban Boards**: 2

**Next Phase**: Phase 9 — Agent Knowledge Base Enhancement