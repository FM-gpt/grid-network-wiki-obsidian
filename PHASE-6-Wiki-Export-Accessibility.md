# Phase 6: Wiki Export & Accessibility

**Goal**: Ensure wiki is fully accessible via web dashboard and easily exportable as package of .md files.

**Estimated Effort**: 1-2 hours

**Dependencies**: Phase 5 complete

**Acceptance Criteria**:
- Full Wiki Viewer in dashboard functional
- Wiki Export feature working
- Direct file access via SCP/SFTP
- Wiki files accessible via HTTP
- No database layer — just markdown files on disk

---

## Task 6.1: Full Wiki Viewer in Dashboard

**Target**: Add "Browse Wiki" section to dashboard

**Steps**:
1. Update dashboard.js to render wiki browser:
   ```javascript
   async renderWikiBrowser() {
     try {
       const response = await fetch('/api/wiki-index');
       const wikiIndex = await response.json();

       this.content.innerHTML = `
         <div class="card">
           <h3>Wiki Browser</h3>
           <div class="wiki-browser">
             <div class="wiki-tree" id="wikiTree">
               ${this.renderWikiTree(wikiIndex.pages)}
             </div>
           </div>
         </div>
       `;

       // Add click handlers for wiki tree
       this.setupWikiTreeHandlers();
     } catch (error) {
       console.error('Error loading wiki browser:', error);
     }
   }

   renderWikiTree(pages) {
     return pages.map(page => `
       <div class="wiki-page-item">
         <span class="wiki-page-icon">📄</span>
         <a href="/wiki/${page.slug}.md" target="_blank">${page.title}</a>
       </div>
     `).join('');
   }

   setupWikiTreeHandlers() {
     document.querySelectorAll('.wiki-page-item a').forEach(link => {
       link.addEventListener('click', (e) => {
         e.preventDefault();
         const slug = e.target.getAttribute('href').replace('/wiki/', '').replace('.md', '');
         this.viewWikiPage(slug);
       });
     });
   }

   async viewWikiPage(slug) {
     try {
       const content = await WikiAPI.getWikiPage(slug);
       this.content.innerHTML = `
         <div class="card">
           <h3>${slug}</h3>
           <div class="wiki-page-content">
             <pre>${content}</pre>
           </div>
           <button class="btn btn-secondary" onclick="window.history.back()">Back</button>
         </div>
       `;
     } catch (error) {
       console.error('Error loading wiki page:', error);
     }
   }
   ```
2. Deploy to CT120 and test

**Verification**:
- Wiki browser loads all pages
- Clicking page opens in new tab
- Wiki viewer shows page content

**Output Files**:
- `/srv/grid-wiki/dashboard/js/dashboard.js` (updated)

---

## Task 6.2: Wiki Export Feature

**Target**: Add "Download Wiki" button to dashboard

**Steps**:
1. Update dashboard.js export functionality:
   ```javascript
   async exportWiki() {
     try {
       const blob = await WikiAPI.exportWiki();
       const url = URL.createObjectURL(blob);
       const a = document.createElement('a');
       a.href = url;
       a.download = 'grid-wiki-export.tar.gz';
       a.click();
       URL.revokeObjectURL(url);

       // Show success message
       this.showNotification('Wiki exported successfully!');
     } catch (error) {
       console.error('Error exporting wiki:', error);
       this.showNotification('Error exporting wiki', 'error');
     }
   }

   showNotification(message, type = 'success') {
     const notification = document.createElement('div');
     notification.className = `notification notification-${type}`;
     notification.textContent = message;
     document.body.appendChild(notification);

     setTimeout(() => {
       notification.remove();
     }, 3000);
   }
   ```
2. Update dashboard.html to add export button:
   ```html
   <button id="exportBtn" class="btn btn-secondary">📥 Export Wiki</button>
   ```
3. Deploy to CT120 and test

**Verification**:
- Export button downloads tar.gz file
- File contains all wiki markdown files
- File is valid tar.gz

**Output Files**:
- `/srv/grid-wiki/dashboard/js/dashboard.js` (updated)
- `/srv/grid-wiki/dashboard/index.html` (updated)

---

## Task 6.3: Direct File Access

**Target**: Ensure `/srv/grid-wiki/wiki/` accessible via SCP/SFTP

**Steps**:
1. Verify directory permissions:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/wiki/"
   ```
2. Ensure directory is readable:
   ```bash
   ssh grid-pve "pct exec 120 -- chmod 755 /srv/grid-wiki/wiki/"
   ```
3. Test SCP access from Mac:
   ```bash
   scp -i /Users/tron/.ssh/proxmox_grid_ed25519 root@10.10.30.130:/srv/grid-wiki/wiki/INDEX.md /tmp/
   ```
4. Verify file accessible

**Verification**:
- SCP access works
- Files readable
- No permission errors

**Output Files**:
- `/srv/grid-wiki/wiki/` (permissions updated)

---

## Task 6.4: Wiki Files Accessible via HTTP

**Target**: Ensure wiki files accessible via HTTP

**Steps**:
1. Test wiki file access:
   ```bash
   curl -s http://localhost:8082/wiki/INDEX.md
   curl -s http://localhost:8082/wiki/GRID-Infrastructure-Overview.md
   ```
2. Verify all wiki files accessible
3. Test wiki index endpoint:
   ```bash
   curl -s http://localhost:8082/api/wiki-index
   ```

**Verification**:
- All wiki files return 200
- Wiki index returns valid JSON
- No 404 errors

**Output Files**:
- `/srv/grid-wiki/wiki/` (deployed to CT120)

---

## Task 6.5: Update Project Manifest

**Target**: Mark Phase 6 complete in PROJECT-MANIFEST.md

**Steps**:
1. Read current `PROJECT-MANIFEST.md`
2. Update `current_goal` to "Phase 7: Maintenance Auto-Resolution"
3. Add Phase 6 to `completed_phases` list
4. Commit changes: `git add . && git commit -m "Phase 6 complete"`

**Verification**:
```bash
cat /Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md | grep -A 2 "current_goal"
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md` (updated)

---

## Task 6.6: Document Phase 6 Completion

**Target**: Create Phase 6 completion report

**Steps**:
1. Create `/srv/grid-wiki/raw/live-state/phase-6-completion.md`
2. Document:
   - Full Wiki Viewer in dashboard functional
   - Wiki Export feature working
   - Direct file access via SCP/SFTP
   - Wiki files accessible via HTTP
3. Commit to git: `git add . && git commit -m "Phase 6 completion report"`

**Verification**:
```bash
cat /srv/grid-wiki/raw/live-state/phase-6-completion.md
```

**Output Files**:
- `/srv/grid-wiki/raw/live-state/phase-6-completion.md`

---

## Summary

**Total Tasks**: 6
**Estimated Time**: 1-2 hours
**Files Created**: 0
**Directories Created**: 0
**Features Added**: 3

**Next Phase**: Phase 7 — Maintenance Auto-Resolution