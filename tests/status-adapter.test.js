/**
 * Tests for status-adapter functionality.
 * Run with: node status-adapter.test.js
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

// Test monitoring status JSON files
test('GRID monitoring-status.json is valid', () => {
    const filepath = path.join(WIKI_CONTENT, 'sites', 'grid', 'monitoring-status.json');
    if (!fs.existsSync(filepath)) {
        throw new Error('monitoring-status.json missing');
    }
    const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
    if (!data.last_check) {
        throw new Error('Missing last_check field');
    }
    if (!data.services || !Array.isArray(data.services)) {
        throw new Error('Missing services array');
    }
    data.services.forEach(service => {
        if (!service.name || !service.status) {
            throw new Error(`Service missing required fields: ${JSON.stringify(service)}`);
        }
    });
});

test('FMSA monitoring-status.json is valid', () => {
    const filepath = path.join(WIKI_CONTENT, 'sites', 'fmsa', 'monitoring-status.json');
    if (!fs.existsSync(filepath)) {
        throw new Error('FMSA monitoring-status.json missing');
    }
    const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
    if (!data.last_check) {
        throw new Error('Missing last_check field');
    }
});

// Test drift report
test('Drift report is valid', () => {
    const driftDir = path.join(WIKI_CONTENT, 'sync', 'drift');
    const files = fs.readdirSync(driftDir).filter(f => f.endsWith('.json'));
    if (files.length === 0) {
        throw new Error('No drift reports found');
    }
    files.forEach(file => {
        const filepath = path.join(driftDir, file);
        const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
        if (!data.timestamp) {
            throw new Error(`Drift report ${file} missing timestamp`);
        }
        if (typeof data.drift_detected !== 'boolean') {
            throw new Error(`Drift report ${file} missing drift_detected boolean`);
        }
    });
});

// Test kanban cards
test('Change kanban cards are valid', () => {
    const statuses = ['pending', 'approved', 'merged'];
    statuses.forEach(status => {
        const dir = path.join(WIKI_CONTENT, 'change-kanban', status);
        if (!fs.existsSync(dir)) {
            throw new Error(`Change kanban directory missing: ${status}`);
        }
        const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
        files.forEach(file => {
            const filepath = path.join(dir, file);
            const content = fs.readFileSync(filepath, 'utf8');
            if (!content.includes('---')) {
                throw new Error(`${file} missing YAML frontmatter`);
            }
            if (!content.includes('title:')) {
                throw new Error(`${file} missing title in frontmatter`);
            }
        });
    });
});

// Test maintenance cards
test('Maintenance cards are valid', () => {
    const activeDir = path.join(WIKI_CONTENT, 'maintenance', 'active');
    if (!fs.existsSync(activeDir)) {
        throw new Error('Maintenance active directory missing');
    }
    const files = fs.readdirSync(activeDir).filter(f => f.endsWith('.md'));
    files.forEach(file => {
        const filepath = path.join(activeDir, file);
        const content = fs.readFileSync(filepath, 'utf8');
        if (!content.includes('---')) {
            throw new Error(`${file} missing YAML frontmatter`);
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
