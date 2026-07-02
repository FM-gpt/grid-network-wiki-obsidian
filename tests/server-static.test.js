/**
 * Tests for server-static functionality.
 * Run with: node server-static.test.js
 */

const fs = require('fs');
const path = require('path');

const BASE_DIR = path.resolve(__dirname, '..');
const DASHBOARD_DIR = path.join(BASE_DIR, 'dashboard');
const KANBAN_DIR = path.join(DASHBOARD_DIR, 'kanban');
const CSS_DIR = path.join(DASHBOARD_DIR, 'css');
const JS_DIR = path.join(DASHBOARD_DIR, 'js');

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

// Test dashboard files exist
const DASHBOARD_FILES = [
    'index.html',
    'monitoring.html',
    'drift.html',
    'wiki-browser.html',
    'sites.html',
    'agents.html',
    'settings.html'
];

DASHBOARD_FILES.forEach(filename => {
    test(`Dashboard file exists: ${filename}`, () => {
        const filepath = path.join(DASHBOARD_DIR, filename);
        if (!fs.existsSync(filepath)) {
            throw new Error(`Dashboard file missing: ${filename}`);
        }
        const content = fs.readFileSync(filepath, 'utf8');
        if (!content.includes('<!DOCTYPE html>')) {
            throw new Error(`${filename} is not valid HTML`);
        }
    });
});

// Test kanban files exist
const KANBAN_FILES = ['change.html', 'maintenance.html'];
KANBAN_FILES.forEach(filename => {
    test(`Kanban file exists: ${filename}`, () => {
        const filepath = path.join(KANBAN_DIR, filename);
        if (!fs.existsSync(filepath)) {
            throw new Error(`Kanban file missing: ${filename}`);
        }
    });
});

// Test CSS files exist
const CSS_FILES = ['dashboard.css', 'sidebar.css'];
CSS_FILES.forEach(filename => {
    test(`CSS file exists: ${filename}`, () => {
        const filepath = path.join(CSS_DIR, filename);
        if (!fs.existsSync(filepath)) {
            throw new Error(`CSS file missing: ${filename}`);
        }
        const content = fs.readFileSync(filepath, 'utf8');
        if (content.length < 100) {
            throw new Error(`${filename} is too small (${content.length} chars)`);
        }
    });
});

// Test JS files exist
const JS_FILES = ['api.js', 'dashboard.js', 'sidebar.js', 'chatbox.js'];
JS_FILES.forEach(filename => {
    test(`JS file exists: ${filename}`, () => {
        const filepath = path.join(JS_DIR, filename);
        if (!fs.existsSync(filepath)) {
            throw new Error(`JS file missing: ${filename}`);
        }
        const content = fs.readFileSync(filepath, 'utf8');
        if (content.length < 100) {
            throw new Error(`${filename} is too small (${content.length} chars)`);
        }
    });
});

// Test wiki-index.json exists and is valid
test('wiki-index.json exists and is valid JSON', () => {
    const filepath = path.join(DASHBOARD_DIR, 'wiki-index.json');
    if (!fs.existsSync(filepath)) {
        throw new Error('wiki-index.json missing');
    }
    const content = fs.readFileSync(filepath, 'utf8');
    const data = JSON.parse(content);
    if (!data.pages || !Array.isArray(data.pages)) {
        throw new Error('wiki-index.json missing pages array');
    }
    if (!data.sites || !Array.isArray(data.sites)) {
        throw new Error('wiki-index.json missing sites array');
    }
});

// Test monitoring-status.json exists
test('monitoring-status.json exists and is valid', () => {
    const filepath = path.join(BASE_DIR, 'wiki-content', 'sites', 'grid', 'monitoring-status.json');
    if (!fs.existsSync(filepath)) {
        throw new Error('monitoring-status.json missing');
    }
    const content = fs.readFileSync(filepath, 'utf8');
    const data = JSON.parse(content);
    if (!data.services || !Array.isArray(data.services)) {
        throw new Error('monitoring-status.json missing services array');
    }
});

// Summary
console.log(`\n${passed} passed, ${failed} failed`);
if (failed > 0) {
    process.exit(1);
} else {
    console.log('All tests passed!');
}
