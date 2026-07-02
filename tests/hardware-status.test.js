/**
 * Tests for hardware-status functionality.
 * Run with: node hardware-status.test.js
 */

const fs = require('fs');
const path = require('path');

const BASE_DIR = path.resolve(__dirname, '..');
const WIKI_CONTENT = path.join(BASE_DIR, 'wiki-content');

let passed = 0;
let failed = 0;

function test(name, fn) {
    try {
        fn();
        console.log(`✓ ${name}`);
        passed++;
    } catch (e) {
        console.log(`✗ ${name}: ${e.message}`);
        failed++;
    }
}

// Test sites directory structure
test('Sites directory structure is valid', () => {
    const sitesDir = path.join(WIKI_CONTENT, 'sites');
    if (!fs.existsSync(sitesDir)) {
        throw new Error('Sites directory missing');
    }
    
    const siteDirs = fs.readdirSync(sitesDir).filter(d => {
        const stat = fs.statSync(path.join(sitesDir, d));
        return stat.isDirectory();
    });
    
    if (siteDirs.length === 0) {
        throw new Error('No site directories found');
    }
    
    siteDirs.forEach(site => {
        const sitePath = path.join(sitesDir, site);
        const files = fs.readdirSync(sitePath);
        
        if (!files.includes('monitoring-status.json')) {
            throw new Error(`Site ${site} missing monitoring-status.json`);
        }
        
        const monitoringFile = path.join(sitePath, 'monitoring-status.json');
        const data = JSON.parse(fs.readFileSync(monitoringFile, 'utf8'));
        if (!data.services) {
            throw new Error(`Site ${site} monitoring-status.json missing services`);
        }
    });
});

// Test wiki directory structure
test('Wiki directory structure is valid', () => {
    const wikiDir = path.join(BASE_DIR, 'wiki');
    if (!fs.existsSync(wikiDir)) {
        throw new Error('Wiki directory missing');
    }
    
    const files = fs.readdirSync(wikiDir);
    if (!files.includes('INDEX.md')) {
        throw new Error('Wiki INDEX.md missing');
    }
    
    files.forEach(file => {
        if (file.endsWith('.md')) {
            const filePath = path.join(wikiDir, file);
            const content = fs.readFileSync(filePath, 'utf8');
            if (!content.includes('---')) {
                throw new Error(`${file} missing YAML frontmatter`);
            }
        }
    });
});

// Test maintenance directory structure
test('Maintenance directory structure is valid', () => {
    const maintenanceDir = path.join(WIKI_CONTENT, 'maintenance');
    if (!fs.existsSync(maintenanceDir)) {
        throw new Error('Maintenance directory missing');
    }
    
    const subdirs = ['active', 'resolved', 'health-reports'];
    subdirs.forEach(subdir => {
        const subPath = path.join(maintenanceDir, subdir);
        if (!fs.existsSync(subPath)) {
            throw new Error(`Maintenance subdirectory missing: ${subdir}`);
        }
    });
});

// Summary
console.log(`\n${passed} passed, ${failed} failed`);
if (failed > 0) {
    process.exit(1);
} else {
    console.log('All tests passed!');
}
