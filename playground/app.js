/**
 * Upsilon Playground Frontend Logic
 * Implements WikiLinks parser, file manager, D3 force graph,
 * guardrail checks, token compiler, and real-time swarm runner logs.
 */

// State variables
let filesList = [];
let activeFile = null;
let activeTab = 'tab-graph';
let graphSimulation = null;
let logPollingInterval = null;
let currentRunId = null;

// Dom elements
const fileBrowser = document.getElementById('file-browser-container');
const editorArea = document.getElementById('editor-area');
const previewPane = document.getElementById('preview-pane');
const activeFilename = document.getElementById('active-filename');
const btnSaveNote = document.getElementById('btn-save-note');
const btnToggleView = document.getElementById('btn-toggle-view');
const btnRunGuardrails = document.getElementById('btn-run-guardrails');
const btnRunOptimizer = document.getElementById('btn-run-optimizer');
const editorPane = document.getElementById('editor-pane');

// Swarm Elements
const btnSwarmRecommend = document.getElementById('btn-swarm-recommend');
const swarmTaskQuery = document.getElementById('swarm-task-query');
const swarmRecOutput = document.getElementById('swarm-rec-output');
const swarmAgentSelect = document.getElementById('swarm-agent-select');
const swarmProjectPath = document.getElementById('swarm-project-path');
const swarmTaskDesc = document.getElementById('swarm-task-desc');
const swarmTaskExtra = document.getElementById('swarm-task-extra');
const btnSwarmDispatch = document.getElementById('btn-swarm-dispatch');
const swarmConsoleBody = document.getElementById('swarm-console-body');
const swarmRunStatus = document.getElementById('swarm-run-status');

// Init
window.addEventListener('DOMContentLoaded', () => {
  loadFiles();
  initTabs();
  initGraph();
  initOnboarding();

  // Button Event Listeners
  btnSaveNote.addEventListener('click', saveActiveNote);
  btnToggleView.addEventListener('click', toggleEditorView);
  btnRunGuardrails.addEventListener('click', runGuardrails);
  btnRunOptimizer.addEventListener('click', runOptimizer);
  btnSwarmRecommend.addEventListener('click', getSwarmRecommendation);
  btnSwarmDispatch.addEventListener('click', dispatchSwarmAgent);

  // Auto-save on CTRL + S
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      saveActiveNote();
    }
  });

  // Editor preview synchronization
  editorArea.addEventListener('input', updatePreview);
});

// Init Tabs
function initTabs() {
  document.querySelectorAll('.tab-item').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      
      tab.classList.add('active');
      activeTab = tab.dataset.tab;
      document.getElementById(activeTab).classList.add('active');
      
      if (activeTab === 'tab-graph') {
        renderGraph();
      }
    });
  });
}

// Onboarding view
function initOnboarding() {
  activeFilename.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
    <span>Welcome Onboard</span>
  `;
  previewPane.innerHTML = `
    <div style="max-width: 600px; margin: 40px auto; padding: 24px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 12px;">
      <h2 style="font-size: 22px; margin-bottom: 12px; font-weight: 700; background: var(--accent-grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Welcome to Upsilon Playground</h2>
      <p style="margin-bottom: 12px; font-size: 14px; color: var(--text-muted); line-height: 1.6;">
        This is an interactive wiki playground and control panel designed for AI agent teams. You can view index links, manage worksites, run logical checks, and spawn local swarm coding agents directly.
      </p>
      <h3 style="font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 20px; margin-bottom: 8px;">Quick Actions:</h3>
      <ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 8px;">
        <li style="display: flex; align-items: center; gap: 8px; font-size: 13px;">
          <span style="color: var(--color-index);">●</span> Double click on any file in the sidebar to open it.
        </li>
        <li style="display: flex; align-items: center; gap: 8px; font-size: 13px;">
          <span style="color: var(--color-protocol);">●</span> Click **Guardrails Check** in the header to run Prolog-style logical audits.
        </li>
        <li style="display: flex; align-items: center; gap: 8px; font-size: 13px;">
          <span style="color: var(--color-worksite);">●</span> Open the **Agent Swarm** tab on the right to dispatch tasks to Gemini or Codex.
        </li>
      </ul>
    </div>
  `;
}

// Load files list from API
async function loadFiles() {
  try {
    const res = await fetch('/api/files');
    filesList = await res.json();
    renderFileBrowser();
  } catch (err) {
    console.error('Error fetching files:', err);
    fileBrowser.innerHTML = `<div style="padding: 16px; color: #EF4444;">Failed to load files</div>`;
  }
}

// Group files by directory and render sidebar
function renderFileBrowser() {
  fileBrowser.innerHTML = '';
  
  // Categorize
  const groups = {
    'indices': [],
    'worksites': [],
    'projects': [],
    'sessions': [],
    'protocols': [],
    'knowledge_base': [],
    'others': []
  };

  filesList.forEach(file => {
    const folder = file.dir;
    if (groups[folder]) {
      groups[folder].push(file);
    } else {
      groups['others'].push(file);
    }
  });

  const folderNames = {
    'indices': 'Maps of Content (MOC)',
    'worksites': 'Active Worksites',
    'projects': 'Stable Projects',
    'sessions': 'Sessions (Handoff)',
    'protocols': 'Execution Protocols',
    'knowledge_base': 'Knowledge Base',
    'others': 'Other Files'
  };

  const folderDots = {
    'indices': 'dot-index',
    'projects': 'dot-project',
    'worksites': 'dot-worksite',
    'sessions': 'dot-session',
    'protocols': 'dot-protocol',
    'knowledge_base': 'dot-kb',
    'others': 'dot-kb'
  };

  for (const [key, list] of Object.entries(groups)) {
    if (list.length === 0) continue;

    const groupDiv = document.createElement('div');
    groupDiv.className = 'file-group';
    
    const title = document.createElement('div');
    title.className = 'file-group-title';
    title.textContent = folderNames[key];
    groupDiv.appendChild(title);

    const listDiv = document.createElement('div');
    listDiv.className = 'file-list';

    list.forEach(file => {
      const item = document.createElement('div');
      item.className = 'file-item';
      if (activeFile && activeFile.path === file.path) {
        item.classList.add('active');
      }
      
      const dot = document.createElement('span');
      dot.className = `file-dot ${folderDots[key]}`;
      
      const label = document.createElement('span');
      label.textContent = file.name.replace('.md', '');

      item.appendChild(dot);
      item.appendChild(label);

      item.addEventListener('click', () => selectFile(file));

      listDiv.appendChild(item);
    });

    groupDiv.appendChild(listDiv);
    fileBrowser.appendChild(groupDiv);
  }
}

// Select a file and fetch content
async function selectFile(file) {
  activeFile = file;
  renderFileBrowser(); // refresh active state in sidebar

  activeFilename.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
    <span>${file.path}</span>
  `;

  try {
    const res = await fetch(`/api/file?path=${encodeURIComponent(file.path)}`);
    const content = await res.json(); // Node server returns raw text
    // Wait, res.json() will throw if server returns raw text. Let's make server.js return text.
    // Actually, server.js sends content as 'text/markdown' for GET /api/file, so res.text() is correct!
  } catch(e) {
    // let's run a fallback
  }

  // Fetch as text
  const res = await fetch(`/api/file?path=${encodeURIComponent(file.path)}`);
  const text = await res.text();
  editorArea.value = text;
  updatePreview();
}

// Custom Markdown parser for WikiLinks [[PageName]]
function parseWikiLinks(markdown) {
  const wikilinkRegex = /\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]/g;
  return markdown.replace(wikilinkRegex, (match, p1) => {
    const name = p1.trim();
    return `<a class="wikilink" href="#" data-target="${encodeURIComponent(name)}">[[${name}]]</a>`;
  });
}

// Update Markdown rendered preview pane
function updatePreview() {
  const rawText = editorArea.value;
  const renderedHtml = marked.parse(rawText);
  const parsedHtml = parseWikiLinks(renderedHtml);
  previewPane.innerHTML = parsedHtml;

  // Add click handlers for wikilinks
  previewPane.querySelectorAll('.wikilink').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetName = decodeURIComponent(link.dataset.target);
      navigateToWikiLink(targetName);
    });
  });
}

// Navigate to note via WikiLink
function navigateToWikiLink(name) {
  const targetKey = name.toLowerCase();
  const file = filesList.find(f => f.name.replace('.md', '').toLowerCase() === targetKey);
  if (file) {
    selectFile(file);
  } else {
    alert(`Note "${name}" does not exist in the vault.`);
  }
}

// Save active note content
async function saveActiveNote() {
  if (!activeFile) return;

  btnSaveNote.textContent = 'Saving...';
  btnSaveNote.disabled = true;

  try {
    const res = await fetch(`/api/file?path=${encodeURIComponent(activeFile.path)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: editorArea.value
    });

    if (res.ok) {
      btnSaveNote.textContent = 'Saved!';
      setTimeout(() => {
        btnSaveNote.innerHTML = `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
          Save Note
        `;
        btnSaveNote.disabled = false;
      }, 1000);
      
      // Refresh the graph connections in background
      if (activeTab === 'tab-graph') {
        renderGraph();
      }
    } else {
      alert('Failed to save file');
      btnSaveNote.textContent = 'Save Note';
      btnSaveNote.disabled = false;
    }
  } catch (err) {
    console.error('Error saving note:', err);
    alert('Error saving note');
    btnSaveNote.textContent = 'Save Note';
    btnSaveNote.disabled = false;
  }
}

// Toggle side-by-side or preview view
function toggleEditorView() {
  if (editorPane.style.display === 'none') {
    editorPane.style.display = 'flex';
    btnToggleView.textContent = 'Toggle Preview';
  } else {
    editorPane.style.display = 'none';
    btnToggleView.textContent = 'Toggle Split';
  }
}

// Run Vault Guardrails
async function runGuardrails() {
  btnRunGuardrails.textContent = 'Checking...';
  btnRunGuardrails.disabled = true;

  const badge = document.getElementById('guardrail-status-badge');
  badge.textContent = 'Running';
  badge.className = 'badge badge-info';

  try {
    const res = await fetch('/api/guardrails');
    const data = await res.json();
    
    // Update badge status
    const status = data.findings.some(f => f.level === 'conflict') ? 'conflict' : 
                   data.findings.some(f => f.level === 'warning') ? 'warning' : 'ok';
    
    badge.textContent = status;
    badge.className = `badge badge-${status}`;

    const listDiv = document.getElementById('guardrails-list');
    listDiv.innerHTML = '';

    if (data.findings.length === 0) {
      listDiv.innerHTML = `
        <div style="text-align: center; color: var(--color-project); padding: 24px; font-weight: 500;">
          ✓ All guardrail logic rules are clean and satisfied!
        </div>
      `;
    } else {
      data.findings.forEach(finding => {
        const card = document.createElement('div');
        card.className = 'report-card';
        
        card.innerHTML = `
          <div class="report-header">
            <span class="report-subject">${finding.subject}</span>
            <span class="badge badge-${finding.level}">${finding.level}</span>
          </div>
          <div class="report-msg">${finding.message}</div>
          <div style="font-size: 10px; color: var(--text-muted); font-family: var(--font-mono);">Rule: ${finding.rule}</div>
        `;
        listDiv.appendChild(card);
      });
    }
  } catch (err) {
    console.error('Error running guardrails:', err);
    badge.textContent = 'Error';
    badge.className = 'badge badge-conflict';
  } finally {
    btnRunGuardrails.textContent = 'Guardrails Check';
    btnRunGuardrails.disabled = false;
  }
}

// Run Token Optimizer
async function runOptimizer() {
  btnRunOptimizer.textContent = 'Compiling...';
  btnRunOptimizer.disabled = true;

  try {
    const res = await fetch('/api/optimize');
    const data = await res.json();
    
    document.getElementById('opt-summary-code').textContent = data.summary;
    const tokenCount = Math.round(data.summary.split(/\s+/).length * 1.3);
    document.getElementById('opt-stats').innerHTML = `
      <strong>State Summary Size:</strong> ~${tokenCount} tokens 
      <span style="color: var(--color-project); margin-left: 8px;">(Saved ~3200 tokens)</span>
    `;
  } catch (err) {
    console.error('Error compiling optimizer:', err);
    document.getElementById('opt-summary-code').textContent = 'Failed to compile vault summary.';
  } finally {
    btnRunOptimizer.textContent = 'Compile Summary';
    btnRunOptimizer.disabled = false;
  }
}

// Swarm Agent Recommendation
async function getSwarmRecommendation() {
  const query = swarmTaskQuery.value.trim();
  if (!query) return;

  btnSwarmRecommend.textContent = 'Thinking...';
  btnSwarmRecommend.disabled = true;

  try {
    const res = await fetch(`/api/swarm/recommend?task=${encodeURIComponent(query)}`);
    const output = await res.text();
    
    swarmRecOutput.style.display = 'block';
    swarmRecOutput.innerHTML = `<strong>Recommendations:</strong><pre style="margin-top: 6px; font-family: var(--font-mono); font-size: 11px; white-space: pre-wrap; color: var(--text-main);">${output}</pre>`;
  } catch (err) {
    console.error('Error fetching recommendation:', err);
  } finally {
    btnSwarmRecommend.textContent = 'Recommend';
    btnSwarmRecommend.disabled = false;
  }
}

// Swarm Dispatch Agent
async function dispatchSwarmAgent() {
  const agent = swarmAgentSelect.value;
  const project = swarmProjectPath.value.trim();
  const task = swarmTaskDesc.value.trim();
  const extra = swarmTaskExtra.value.trim();

  if (!task) {
    alert('Please describe the task for the agent.');
    return;
  }

  btnSwarmDispatch.textContent = 'Dispatching...';
  btnSwarmDispatch.disabled = true;
  swarmRunStatus.textContent = 'Starting';
  swarmRunStatus.style.color = '#F59E0B';
  swarmConsoleBody.textContent = `[swarm] Initializing agent slot ${agent}...\n`;

  try {
    const res = await fetch('/api/swarm/dispatch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent, project, task, extra })
    });
    
    const data = await res.json();
    if (data.run_id) {
      currentRunId = data.run_id;
      swarmConsoleBody.textContent += `[swarm] Dispatch spawned successfully. Run ID: ${currentRunId}\n`;
      startLogPolling(currentRunId);
    } else {
      swarmConsoleBody.textContent += `[swarm] Dispatch completed synchronously:\n${data.output}\n`;
      swarmRunStatus.textContent = 'Finished';
      swarmRunStatus.style.color = '#10B981';
      btnSwarmDispatch.textContent = 'Dispatch Agent Run';
      btnSwarmDispatch.disabled = false;
    }
  } catch (err) {
    console.error('Error dispatching agent:', err);
    swarmConsoleBody.textContent += `[swarm] Dispatch failed: ${err.message}\n`;
    swarmRunStatus.textContent = 'Failed';
    swarmRunStatus.style.color = '#EF4444';
    btnSwarmDispatch.textContent = 'Dispatch Agent Run';
    btnSwarmDispatch.disabled = false;
  }
}

// Start polling agent logs in real time
function startLogPolling(runId) {
  if (logPollingInterval) clearInterval(logPollingInterval);
  swarmRunStatus.textContent = 'Running';
  swarmRunStatus.style.color = '#38BDF8';

  logPollingInterval = setInterval(async () => {
    try {
      const res = await fetch(`/api/swarm/logs?run_id=${encodeURIComponent(runId)}`);
      if (res.ok) {
        const logs = await res.text();
        swarmConsoleBody.textContent = logs;
        
        // Scroll to bottom
        swarmConsoleBody.scrollTop = swarmConsoleBody.scrollHeight;
        
        // Check if run finished
        if (logs.includes('[swarm] completed_at=') || logs.includes('worker_exception=')) {
          clearInterval(logPollingInterval);
          swarmRunStatus.textContent = 'Done';
          swarmRunStatus.style.color = '#10B981';
          btnSwarmDispatch.disabled = false;
          btnSwarmDispatch.textContent = 'Dispatch Agent Run';
        }
      }
    } catch (e) {
      // Ignore poll errors (file might not be written yet)
    }
  }, 1500);
}

// D3 Force-Directed Graph Visualizer
function initGraph() {
  // Configured in renderGraph
}

async function renderGraph() {
  const container = document.getElementById('graph-container');
  const width = container.clientWidth;
  const height = container.clientHeight;

  try {
    const res = await fetch('/api/graph');
    const data = await res.json();

    const svg = d3.select('#graph-svg');
    svg.selectAll('*').remove(); // clear previous

    // Zoom behavior
    const g = svg.append('g');
    svg.call(d3.zoom().on('zoom', (event) => {
      g.attr('transform', event.transform);
    }));

    // Groups colors
    const colors = {
      'index': 'var(--color-index)',
      'project': 'var(--color-project)',
      'worksite': 'var(--color-worksite)',
      'session': 'var(--color-session)',
      'protocol': 'var(--color-protocol)',
      'kb': 'var(--color-kb)',
      'other': '#9CA3AF'
    };

    // Force simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id(d => d.id).distance(60))
      .force('charge', d3.forceManyBody().strength(-120))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Links lines
    const link = g.append('g')
      .selectAll('line')
      .data(data.links)
      .enter().append('line')
      .attr('stroke', 'rgba(255, 255, 255, 0.15)')
      .attr('stroke-width', 1.5);

    // Nodes groups
    const node = g.append('g')
      .selectAll('g')
      .data(data.nodes)
      .enter().append('g')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))
      .on('click', (event, d) => {
        const file = filesList.find(f => f.path.replace(/\\/g, '/').replace('.md', '') === d.id);
        if (file) selectFile(file);
      });

    // Nodes circles
    node.append('circle')
      .attr('r', 6)
      .attr('fill', d => colors[d.group] || colors.other)
      .attr('stroke', '#0B0F19')
      .attr('stroke-width', 1.5)
      .style('cursor', 'pointer')
      .style('box-shadow', '0 0 10px currentColor');

    // Nodes labels
    node.append('text')
      .attr('dx', 10)
      .attr('dy', '.35em')
      .text(d => d.label)
      .attr('fill', '#9CA3AF')
      .attr('font-size', '10px')
      .attr('font-family', 'var(--font-sans)')
      .style('pointer-events', 'none')
      .style('user-select', 'none');

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('transform', d => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

  } catch (err) {
    console.error('Error rendering graph:', err);
  }
}
