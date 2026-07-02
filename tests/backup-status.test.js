/**
 * Tests for backup-status functionality.
 * Run with: node backup-status.test.js
 */

const fs = require('fs');
const path = require('path');

const BASE_DIR = path.resolve(__dirname, '..');
const SYNC_DIR = path.join(BASE_DIR, 'wiki-content', 'sync');

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

// Test sync manifest
test('Sync manifest exists and is valid', () => {
    const filepath = path.join(SYNC_DIR, 'manifest.json');
    if (!fs.existsSync(filepath)) {
        throw new Error('Sync manifest missing');
    }
    const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
    if (!data.version) {
        throw new Error('Missing version field');
    }
    if (!data.last_sync) {
        throw new Error('Missing last_sync field');
    }
    if (!data.files || typeof data.files !== 'object') {
        throw new Error('Missing or invalid files field');
    }
});

// Test checksums file
test('Checksums file exists and is valid', () => {
    const filepath = path.join(SYNC_DIR, 'last-checksums.md5');
    if (!fs.existsSync(filepath)) {
        throw new Error('Checksums file missing');
    }
    const content = fs.readFileSync(filepath, 'utf8');
    const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('#'));
    if (lines.length === 0) {
        throw new Error('Checksums file is empty');
    }
    lines.forEach(line => {
        const parts = line.trim().split(/\s+/);
        if (parts.length !== 2) {
            throw new Error(`Invalid checksum line: ${line}`);
        }
        if (parts[0].length !== 32) {
            throw new Error(`Invalid checksum length: ${parts[0]}`);
        }
    });
});

// Test drift directory structure
test('Drift directory structure is valid', () => {
    const driftDir = path.join(SYNC_DIR, 'drift');
    if (!fs.existsSync(driftDir)) {
        throw new Error('Drift directory missing');
    }
    const files = fs.readdirSync(driftDir);
    files.forEach(file => {
        if (!file.endsWith('.json')) {
            throw new Error(`Invalid file in drift directory: ${file}`);
        }
        const filepath = path.join(driftDir, file);
        const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
        if (!data.timestamp) {
            throw new Error(`Drift report ${file} missing timestamp`);
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
