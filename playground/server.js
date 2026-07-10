#!/usr/bin/env node
/**
 * Omega Playground Backend Server
 * Dependency-free, runs on Node.js and Bun.
 * Exposes vault files, graph connections, and runs scripts.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec, execFile, spawn } = require('child_process');
const url = require('url');

const PORT = process.env.PORT || 8080;
const VAULT_DIR = path.resolve(__dirname, '..');
const PLAYGROUND_DIR = __dirname;

// Helper to determine content type
const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.md': 'text/markdown',
};

// Log helper
function log(msg) {
  console.log(`[OmegaServer] ${new Date().toISOString()} - ${msg}`);
}

// Read markdown files recursively
function getMarkdownFiles(dir, fileList = []) {
  if (!fs.existsSync(dir)) return fileList;
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    if (stat.isDirectory()) {
      if (['.git', '.obsidian', 'node_modules', 'dump', 'playground'].includes(file)) continue;
      getMarkdownFiles(filePath, fileList);
    } else if (file.endsWith('.md')) {
      fileList.push(filePath);
    }
  }
  return fileList;
}

// Build nodes and links for D3 Graph
function buildGraph() {
  const files = getMarkdownFiles(VAULT_DIR);
  const nodes = [];
  const links = [];
  const fileMap = new Map();

  // Create nodes
  for (const file of files) {
    const relPath = path.relative(VAULT_DIR, file);
    const name = path.basename(file, '.md');
    let group = 'other';
    const folder = relPath.split(path.sep)[0];
    
    if (folder === 'indici') group = 'index';
    else if (folder === 'progetti') group = 'project';
    else if (folder === 'CANTIERI') group = 'cantiere';
    else if (folder === 'sessioni') group = 'session';
    else if (folder === 'scoperte e processi') group = 'protocol';
    else if (folder === 'informazioni generali') group = 'kb';

    fileMap.set(name.toLowerCase(), { id: name, label: name, group, path: relPath });
    nodes.push({ id: name, label: name, group, path: relPath });
  }

  // Find links
  const wikilinkRegex = /\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]/g;
  for (const file of files) {
    const sourceName = path.basename(file, '.md');
    const content = fs.readFileSync(file, 'utf8');
    let match;
    const seenLinks = new Set();

    while ((match = wikilinkRegex.exec(content)) !== null) {
      const targetName = match[1].trim();
      const targetKey = targetName.toLowerCase();
      
      if (fileMap.has(targetKey) && targetName !== sourceName && !seenLinks.has(targetKey)) {
        seenLinks.add(targetKey);
        links.push({
          source: sourceName,
          target: fileMap.get(targetKey).id
        });
      }
    }
  }

  return { nodes, links };
}

// Serve static files or API endpoints
const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  let pathname = parsedUrl.pathname;

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // --- API ROUTING ---

  // Get Vault File Tree
  if (pathname === '/api/files' && req.method === 'GET') {
    try {
      const files = getMarkdownFiles(VAULT_DIR).map(f => {
        const rel = path.relative(VAULT_DIR, f);
        return {
          name: path.basename(f),
          path: rel,
          dir: path.dirname(rel)
        };
      });
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(files));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end(`Error reading files: ${err.message}`);
    }
    return;
  }

  // Read File Content
  if (pathname === '/api/file' && req.method === 'GET') {
    const fileRelPath = parsedUrl.query.path;
    if (!fileRelPath) {
      res.writeHead(400, { 'Content-Type': 'text/plain' });
      res.end('Missing file path');
      return;
    }
    const fullPath = path.join(VAULT_DIR, fileRelPath);
    // Path traversal prevention
    if (!fullPath.startsWith(VAULT_DIR)) {
      res.writeHead(403, { 'Content-Type': 'text/plain' });
      res.end('Access denied');
      return;
    }

    if (!fs.existsSync(fullPath)) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('File not found');
      return;
    }

    try {
      const content = fs.readFileSync(fullPath, 'utf8');
      res.writeHead(200, { 'Content-Type': 'text/markdown; charset=utf-8' });
      res.end(content);
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end(`Error reading file: ${err.message}`);
    }
    return;
  }

  // Write File Content
  if (pathname === '/api/file' && req.method === 'POST') {
    const fileRelPath = parsedUrl.query.path;
    if (!fileRelPath) {
      res.writeHead(400, { 'Content-Type': 'text/plain' });
      res.end('Missing file path');
      return;
    }
    const fullPath = path.join(VAULT_DIR, fileRelPath);
    if (!fullPath.startsWith(VAULT_DIR)) {
      res.writeHead(403, { 'Content-Type': 'text/plain' });
      res.end('Access denied');
      return;
    }

    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        fs.writeFileSync(fullPath, body, 'utf8');
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end('File saved successfully');
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(`Error saving file: ${err.message}`);
      }
    });
    return;
  }

  // Get WikiLink Graph data
  if (pathname === '/api/graph' && req.method === 'GET') {
    try {
      const graphData = buildGraph();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(graphData));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end(`Error building graph: ${err.message}`);
    }
    return;
  }

  // Run Vault Guardrails
  if (pathname === '/api/guardrails' && req.method === 'GET') {
    const scriptPath = path.join(VAULT_DIR, 'scripts', 'vault_guardrails.py');
    const jsonOut = path.join(VAULT_DIR, 'dump', 'guardrails_report.json');
    
    // Ensure dump dir exists
    fs.mkdirSync(path.join(VAULT_DIR, 'dump'), { recursive: true });

    execFile('python3', [scriptPath, '--json-output', jsonOut], { cwd: VAULT_DIR }, (err, stdout, stderr) => {
      try {
        if (fs.existsSync(jsonOut)) {
          const report = fs.readFileSync(jsonOut, 'utf8');
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(report);
        } else {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Guardrail script did not generate JSON', stdout, stderr }));
        }
      } catch (e) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(`Error running guardrails: ${e.message}`);
      }
    });
    return;
  }

  // Run Token Optimizer
  if (pathname === '/api/optimize' && req.method === 'GET') {
    const scriptPath = path.join(VAULT_DIR, 'scripts', 'token_optimizer.py');
    execFile('python3', [scriptPath], { cwd: VAULT_DIR }, (err, stdout, stderr) => {
      if (err) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(`Optimizer failed: ${stderr || err.message}`);
        return;
      }
      try {
        const summaryFile = path.join(VAULT_DIR, 'context_summary.md');
        const summary = fs.readFileSync(summaryFile, 'utf8');
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ summary, stdout }));
      } catch (e) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(`Error reading summary: ${e.message}`);
      }
    });
    return;
  }

  // Swarm Agent Recommendation
  if (pathname === '/api/swarm/recommend' && req.method === 'GET') {
    const task = parsedUrl.query.task;
    if (!task) {
      res.writeHead(400, { 'Content-Type': 'text/plain' });
      res.end('Missing task parameter');
      return;
    }
    const scriptPath = path.join(VAULT_DIR, 'scripts', 'swarm_orchestrator.py');
    execFile('python3', [scriptPath, 'recommend', '--task', task], { cwd: VAULT_DIR }, (err, stdout, stderr) => {
      if (err) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(`Swarm recommend failed: ${stderr || err.message}`);
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end(stdout);
    });
    return;
  }

  // Swarm Check Agents
  if (pathname === '/api/swarm/check-agents' && req.method === 'GET') {
    const scriptPath = path.join(VAULT_DIR, 'scripts', 'swarm_orchestrator.py');
    execFile('python3', [scriptPath, 'check-agent', '--all'], { cwd: VAULT_DIR }, (err, stdout, stderr) => {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end(stdout + (stderr ? '\n' + stderr : ''));
    });
    return;
  }

  // Swarm Dispatch Agent (triggers background or foreground process)
  if (pathname === '/api/swarm/dispatch' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const params = JSON.parse(body);
        const agent = params.agent;
        const project = params.project || VAULT_DIR;
        const task = params.task;
        const extra = params.extra || '';

        if (!agent || !task) {
          res.writeHead(400, { 'Content-Type': 'text/plain' });
          res.end('Missing agent or task');
          return;
        }

        const scriptPath = path.join(VAULT_DIR, 'scripts', 'swarm_orchestrator.py');
        const args = [
          scriptPath,
          'dispatch',
          '--agent', agent,
          '--project', project,
          '--task', task
        ];
        if (extra) {
          args.push('--extra', extra);
        }

        log(`Spawning swarm: python3 ${args.join(' ')}`);
        const proc = spawn('python3', args, { cwd: VAULT_DIR, detached: true, stdio: 'pipe' });

        let output = '';
        proc.stdout.on('data', data => { output += data.toString(); });
        proc.stderr.on('data', data => { output += data.toString(); });

        proc.on('close', code => {
          log(`Swarm dispatch finished with code ${code}. Output: ${output.trim()}`);
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({
            code,
            output: output.trim(),
            run_id: output.split('\n')[0].trim() // The script prints run_id as first output line
          }));
        });
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(`Dispatch failed: ${err.message}`);
      }
    });
    return;
  }

  // Swarm Run list
  if (pathname === '/api/swarm/runs' && req.method === 'GET') {
    const runsDir = path.join(VAULT_DIR, 'dump', 'swarm_runs');
    if (!fs.existsSync(runsDir)) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify([]));
      return;
    }
    try {
      const dirs = fs.readdirSync(runsDir).filter(f => fs.statSync(path.join(runsDir, f)).isDirectory());
      const runs = dirs.map(d => {
        const metadataFile = path.join(runsDir, d, 'metadata.json');
        if (fs.existsSync(metadataFile)) {
          return JSON.parse(fs.readFileSync(metadataFile, 'utf8'));
        }
        return { run_id: d, state: 'unknown' };
      }).sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''));
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(runs));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end(`Error reading runs: ${err.message}`);
    }
    return;
  }

  // Swarm Run Logs
  if (pathname === '/api/swarm/logs' && req.method === 'GET') {
    const runId = parsedUrl.query.run_id;
    if (!runId) {
      res.writeHead(400, { 'Content-Type': 'text/plain' });
      res.end('Missing run_id');
      return;
    }
    const logPath = path.join(VAULT_DIR, 'dump', 'swarm_runs', runId, 'agent.log');
    if (!fs.existsSync(logPath)) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Log not found yet');
      return;
    }
    try {
      const content = fs.readFileSync(logPath, 'utf8');
      res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end(content);
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end(`Error reading log: ${err.message}`);
    }
    return;
  }

  // --- STATIC FILE SERVING ---
  
  // Default to index.html
  if (pathname === '/' || pathname === '/index.html') {
    pathname = '/index.html';
  }

  const filePath = path.join(PLAYGROUND_DIR, pathname);
  
  if (!filePath.startsWith(PLAYGROUND_DIR)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Forbidden');
    return;
  }

  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    const ext = path.extname(filePath);
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });
    fs.createReadStream(filePath).pipe(res);
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('File not found');
  }
});

server.listen(PORT, () => {
  log(`Omega Playground server running on: http://localhost:${PORT}`);
});
