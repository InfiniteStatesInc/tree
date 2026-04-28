#!/usr/bin/env python3
"""
Assemble tree-sway-12.html from exports/tree-N.svg files.
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent
EXPORTS = ROOT / "exports"

TREES = []
for n in range(1, 13):
    svg_path = EXPORTS / f"tree-{n}.svg"
    text = svg_path.read_text()
    m_w = re.search(r'width="(\d+)"', text)
    m_h = re.search(r'height="(\d+)"', text)
    m_vb = re.search(r'viewBox="([^"]+)"', text)
    width = int(m_w.group(1)) if m_w else 963
    height = int(m_h.group(1)) if m_h else 600
    inner = re.sub(r'^\s*<svg[^>]*>', '', text, count=1).rsplit('</svg>', 1)[0]
    TREES.append({
        "n": n,
        "width": width,
        "height": height,
        "viewBox": m_vb.group(1) if m_vb else f"0 0 {width} {height}",
        "inner": inner,
    })

# Tree with the largest height — use as canonical stage height
MAX_H = max(t["height"] for t in TREES)
STAGE_W = 963  # all trees share width=963

# Petal-dropping trees
PETAL_TREES = [9, 10, 11, 12]

# ----- Build HTML -----

HEAD = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>樱花树 · 12 阶段成长 · 骨骼摇摆 + 花瓣飘落</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #efe8e2;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    min-height: 100vh;
    font-family: -apple-system, "PingFang SC", sans-serif;
    color: #555;
    padding: 24px 16px 40px;
  }
  h3 {
    margin-bottom: 16px;
    font-weight: 400;
    font-size: 14px;
    color: #998a84;
    letter-spacing: 0.5px;
  }
  .stage-wrap {
    width: min(560px, 92vw);
    aspect-ratio: __STAGE_W__ / __STAGE_H__;
    position: relative;
    overflow: visible;
    display: flex;
    align-items: flex-end;
    justify-content: center;
  }
  .floating-island {
    width: 100%;
    height: 100%;
    position: relative;
    transform-origin: center bottom;
    /* magnetic levitation: subtle up-down */
    animation: levitate 6.4s ease-in-out infinite;
  }
  @keyframes levitate {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-6px); }
  }
  .tree-stage {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    display: none;
  }
  .tree-stage.active { display: block; }
  .tree-stage > svg {
    width: 100%;
    height: auto;
    display: block;
    overflow: visible;
  }
  /* sway-group rotation is applied via SVG attribute transform with explicit pivot */

  .petal-layer {
    position: absolute;
    left: 0;
    bottom: 0;
    width: 100%;
    height: auto;
    pointer-events: none;
    display: none;
    overflow: visible;
  }
  .petal-layer.active { display: block; }

  .controls {
    margin-top: 20px;
    width: min(640px, 96vw);
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .tree-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: center;
  }
  .tree-buttons button {
    padding: 6px 12px;
    border: 1px solid #c9bdb9;
    background: #f8f3ef;
    color: #6b5a55;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    min-width: 36px;
    font-variant-numeric: tabular-nums;
  }
  .tree-buttons button:hover { background: #efe6e0; }
  .tree-buttons button.active { background: #C18184; color: #fff; border-color: #C18184; }

  .petal-control-group {
    display: none;
    flex-direction: column;
    gap: 10px;
    padding: 14px 18px;
    border: 1px solid #e3d7d2;
    border-radius: 8px;
    background: #fbf6f3;
  }
  .petal-control-group.active { display: flex; }
  .petal-control-group .group-title {
    font-size: 12px;
    color: #998a84;
    letter-spacing: 0.5px;
  }
  .control-row {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .control-row label {
    width: 64px;
    font-size: 13px;
    text-align: right;
    flex-shrink: 0;
    color: #7a6e69;
  }
  .control-row input[type="range"] {
    flex: 1;
    accent-color: #C18184;
  }
  .control-row .value {
    width: 56px;
    font-size: 13px;
    text-align: left;
    font-variant-numeric: tabular-nums;
    color: #555;
  }
  .global-controls {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-top: 4px;
  }
  .global-controls button {
    padding: 6px 14px;
    border: 1px solid #c9bdb9;
    background: #f8f3ef;
    color: #6b5a55;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
  }
  .global-controls button:hover { background: #efe6e0; }
  .global-controls button.on { background: #C18184; color: #fff; border-color: #C18184; }
</style>
</head>
<body>
<h3>樱花树 · 12 阶段成长 · 骨骼摇摆 + 花瓣飘落</h3>
<div class="stage-wrap">
  <div class="floating-island" id="floatBox">
"""

TAIL = """  </div>
</div>

<div class="controls">
  <div class="tree-buttons" id="treeButtons">
__TREE_BUTTONS__
  </div>

__PETAL_CONTROLS__

  <div class="global-controls">
    <button id="swayBtn" class="on">摇摆 ON</button>
    <button id="petalToggle" class="on">花瓣开关 ON</button>
    <button id="resetBtn">重置花瓣</button>
  </div>
</div>

<svg width="0" height="0" style="position:absolute;visibility:hidden">
  <defs>
    <linearGradient id="pGradA" x1="5" y1="0" x2="5" y2="14" gradientUnits="userSpaceOnUse">
      <stop stop-color="#E56B67"/><stop offset="1" stop-color="#DF9895"/>
    </linearGradient>
    <linearGradient id="pGradB" x1="0.515961" y1="4.21881" x2="9.01596" y2="8.71881" gradientUnits="userSpaceOnUse">
      <stop stop-color="#DB7B7B"/><stop offset="1" stop-color="#E7B3B3"/>
    </linearGradient>
  </defs>
</svg>

<script>
__SCRIPT__
</script>
</body>
</html>
"""

# Generate per-tree button HTML
btn_lines = []
for n in range(1, 13):
    cls = ' class="active"' if n == 1 else ''
    btn_lines.append(f'    <button data-tree="{n}"{cls}>{n}</button>')
TREE_BUTTONS = '\n'.join(btn_lines)

# Generate per-tree petal control panels (9, 10, 11, 12)
def petal_panel(n):
    return f'''  <div class="petal-control-group" data-tree="{n}">
    <div class="group-title">第 {n} 棵 · 花瓣控制</div>
    <div class="control-row"><label>风向</label><input type="range" data-param="wind" data-tree="{n}" min="0" max="200" value="100"><span class="value" data-val="wind" data-tree="{n}">100%</span></div>
    <div class="control-row"><label>速度</label><input type="range" data-param="speed" data-tree="{n}" min="30" max="200" value="100"><span class="value" data-val="speed" data-tree="{n}">1.0×</span></div>
    <div class="control-row"><label>密度</label><input type="range" data-param="density" data-tree="{n}" min="0" max="50" value="14"><span class="value" data-val="density" data-tree="{n}">14/s</span></div>
    <div class="control-row"><label>大小</label><input type="range" data-param="size" data-tree="{n}" min="20" max="200" value="60"><span class="value" data-val="size" data-tree="{n}">0.6×</span></div>
  </div>'''

PETAL_CONTROLS = '\n'.join(petal_panel(n) for n in PETAL_TREES)

# Generate tree stages
stage_html = []
for t in TREES:
    n = t["n"]
    cls = ' active' if n == 1 else ''
    # Wrap inner SVG content in sway-group
    inner = t["inner"]
    # Add petal-layer overlay for trees 9, 10, 11, 12 — same viewBox so coordinates match
    if n in PETAL_TREES:
        petal_overlay = f'''
    <svg class="petal-layer{(" active" if n == 1 else "")}" data-tree="{n}" viewBox="{t["viewBox"]}" preserveAspectRatio="xMidYMax meet">
      <g class="petal-container" data-tree="{n}"></g>
    </svg>'''
    else:
        petal_overlay = ''
    stage_html.append(f'''    <div class="tree-stage{cls}" data-tree="{n}" data-w="{t["width"]}" data-h="{t["height"]}">
      <svg viewBox="{t["viewBox"]}" preserveAspectRatio="xMidYMax meet" class="tree-svg" data-tree="{n}">
        <g class="sway-group" data-tree="{n}">{inner}</g>
      </svg>{petal_overlay}
    </div>''')

STAGES = '\n'.join(stage_html)

SCRIPT = """
// ============================================================
// 樱花树 · 12 阶段成长 · 主控制脚本
// ============================================================
const TREES = __TREE_META__;
const PETAL_TREES = [9, 10, 11, 12];
const TREE_HEIGHTS = {};
TREES.forEach(t => TREE_HEIGHTS[t.n] = { w: t.width, h: t.height });

let activeTree = 1;
let SWAY_ON = true;
let PETALS_GLOBAL_ON = true;

// Per-tree petal state
const petalState = {};
PETAL_TREES.forEach(n => {
  petalState[n] = {
    wind: 1.0,
    speed: 1.0,
    spawnRate: 14,
    sizeMul: 0.6,        // user-controllable petal size multiplier (default 0.6×)
    spawnDebt: 0,
    petals: [],
    freePool: [],
    container: null,
  };
});

// Global RNG
function mulberry32(seed) {
  return function() {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
const rng = mulberry32(20260428);
const rand = (lo, hi) => lo + (hi - lo) * rng();
const now = () => performance.now();

// Per-tree sway parameters — varied so each tree feels alive but consistent
// Smaller trees (1-4): less amplitude, faster
// Medium (5-8): moderate
// Large (9-12): more amplitude, slower / more graceful
const SWAY_PARAMS = {};
TREES.forEach(t => {
  const sizeRatio = t.height / 972;  // 1.0 for tree 12 (biggest)
  // base amplitude grows with size for visible canopy motion
  const amp = 0.6 + sizeRatio * 1.4;          // 0.6° — 2.0°
  const freq = 0.30 - sizeRatio * 0.10;       // 0.30 — 0.20 Hz (bigger = slower)
  const phase = rng() * Math.PI * 2;
  // canopy gets extra amplitude on top of base
  const canopyAmp = amp * 1.4;
  const canopyFreq = freq * 1.15;
  // Pivot for sway: bottom-center of viewBox (whole tree+island base).
  // The island is at the bottom, so it barely moves; canopy at top moves most.
  const pivotX = t.width / 2;
  const pivotY = t.height;       // very bottom of viewBox
  SWAY_PARAMS[t.n] = { amp, freq, phase, canopyAmp, canopyFreq, pivotX, pivotY };
});

// Cache DOM refs
const floatBox = document.getElementById('floatBox');
const stages = {};
const swayGroups = {};
const petalLayers = {};
TREES.forEach(t => {
  const stage = document.querySelector(`.tree-stage[data-tree="${t.n}"]`);
  stages[t.n] = stage;
  swayGroups[t.n] = stage.querySelector('.sway-group');
  if (PETAL_TREES.includes(t.n)) {
    petalLayers[t.n] = document.querySelector(`.petal-layer[data-tree="${t.n}"]`);
    petalState[t.n].container = document.querySelector(`.petal-container[data-tree="${t.n}"]`);
  }
});

// ============================================================
// Build sway hierarchy per tree:
//   sway-group  (static, only CSS levitate)
//     ├ <island elements>     (don't move horizontally)
//     └ tree-sway              (rotates by base sway amount)
//          ├ <trunk elements>
//          └ canopy-sway       (rotates by extra canopy amount, trees 4+)
//                └ <canopy elements>
//
// Heuristic for splitting:
//   * island vs tree:   bbox center y >= 60% of viewBox → island (stays put)
//   * canopy vs trunk:  bbox center y < 55% of viewBox → canopy (extra sway)
// ============================================================
const SVG_NS_LOC = 'http://www.w3.org/2000/svg';

function setupSwayGroups(treeN) {
  const sway = swayGroups[treeN];
  const svg = sway.closest('svg');
  const vb = svg.viewBox.baseVal;
  const islandSplitY = vb.y + vb.height * 0.60; // bottom 40% is island
  const canopySplitY = vb.y + vb.height * 0.55; // top 55% is canopy

  // Step 1: Move all non-island elements into tree-sway group
  const treeSway = document.createElementNS(SVG_NS_LOC, 'g');
  treeSway.classList.add('tree-sway');
  treeSway.setAttribute('data-tree', treeN);

  const kids = Array.from(sway.children);
  for (const el of kids) {
    if (el.tagName.toLowerCase() === 'defs') continue;
    let bb;
    try { bb = el.getBBox(); } catch (e) { continue; }
    const cy = bb.y + bb.height / 2;
    if (cy < islandSplitY) {
      // Tree element (trunk/canopy/sprout) → moves into tree-sway
      treeSway.appendChild(el);
    }
    // else: island element, stays as direct child of sway-group → static
  }
  // Append tree-sway last so it draws on top of the island
  sway.appendChild(treeSway);

  // Step 2: For larger trees (4+), additionally split a canopy-sway sub-group
  if (treeN <= 3) return;

  const canopyGroup = document.createElementNS(SVG_NS_LOC, 'g');
  canopyGroup.classList.add('canopy-sway');
  canopyGroup.setAttribute('data-tree', treeN);

  let canopyMinY = Infinity, canopyMaxY = -Infinity, canopyMinX = Infinity, canopyMaxX = -Infinity;
  const treeKids = Array.from(treeSway.children);
  for (const el of treeKids) {
    if (el.tagName.toLowerCase() === 'defs') continue;
    let bb;
    try { bb = el.getBBox(); } catch (e) { continue; }
    const cy = bb.y + bb.height / 2;
    if (cy < canopySplitY) {
      canopyGroup.appendChild(el);
      canopyMinY = Math.min(canopyMinY, bb.y);
      canopyMaxY = Math.max(canopyMaxY, bb.y + bb.height);
      canopyMinX = Math.min(canopyMinX, bb.x);
      canopyMaxX = Math.max(canopyMaxX, bb.x + bb.width);
    }
  }
  treeSway.appendChild(canopyGroup);

  if (canopyMinY !== Infinity) {
    SWAY_PARAMS[treeN].canopyPivotX = (canopyMinX + canopyMaxX) / 2;
    SWAY_PARAMS[treeN].canopyPivotY = canopyMaxY;
  }
}

// ============================================================
// Refine noise filters globally
//  - lower flood-color alpha (more subtle)
//  - sparser tableValues (fewer noise pixels)
//  - higher baseFrequency where it's still 5 5 (finer grain)
// ============================================================
function refineNoise() {
  const filters = document.querySelectorAll('filter');
  // sparse pattern: ~25% on instead of 50%
  const SPARSE = '1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 ' +
                 '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ' +
                 '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ' +
                 '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ';
  filters.forEach(f => {
    if (!/_n_/.test(f.id || '')) return;
    // tableValues — sparser
    const fa = f.querySelector('feFuncA');
    if (fa) fa.setAttribute('tableValues', SPARSE);
    // flood-color alpha — halve
    const floodColors = f.querySelectorAll('feFlood[flood-color]');
    floodColors.forEach(fc => {
      const v = fc.getAttribute('flood-color') || '';
      const m = v.match(/rgba?\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*([\\d.]+)\\s*\\)/);
      if (m) {
        const r = m[1], g = m[2], b = m[3];
        const a = Math.max(0.04, parseFloat(m[4]) * 0.45);
        fc.setAttribute('flood-color', `rgba(${r}, ${g}, ${b}, ${a.toFixed(3)})`);
      }
    });
    // baseFrequency: bump to 8 8 if currently 5 5 (finer grain)
    const turb = f.querySelector('feTurbulence');
    if (turb) {
      const bf = turb.getAttribute('baseFrequency');
      if (bf === '5 5') turb.setAttribute('baseFrequency', '8 8');
      // existing 10 10 noise stays — already fine
    }
  });
}

// ============================================================
// Sway tick — rotate tree-sway (the trunk/canopy) but NOT the island
// ============================================================
function applySway(tSec) {
  for (const t of TREES) {
    const stage = stages[t.n];
    if (!stage.classList.contains('active')) continue;
    const p = SWAY_PARAMS[t.n];
    const sway = swayGroups[t.n];

    let baseRot = 0;
    if (SWAY_ON) {
      const w = 2 * Math.PI * p.freq;
      const flutter = 0.25 * Math.sin(w * 2.4 * tSec + p.phase * 1.7);
      baseRot = p.amp * (Math.sin(w * tSec + p.phase) + flutter);
    }

    // Apply base rotation to tree-sway (NOT sway-group) so the island stays put
    const treeSway = sway.querySelector(':scope > g.tree-sway');
    if (treeSway) {
      treeSway.setAttribute('transform', `rotate(${baseRot.toFixed(3)} ${p.pivotX} ${p.pivotY})`);
    }

    // Additional rotation for canopy (trees 4+)
    const canopy = treeSway && treeSway.querySelector(':scope > g.canopy-sway');
    if (canopy) {
      let canopyRot = 0;
      if (SWAY_ON) {
        const w2 = 2 * Math.PI * p.canopyFreq;
        canopyRot = p.canopyAmp * Math.sin(w2 * tSec + p.phase + 0.6);
      }
      const cx = p.canopyPivotX !== undefined ? p.canopyPivotX : t.width / 2;
      const cy = p.canopyPivotY !== undefined ? p.canopyPivotY : t.height * 0.55;
      canopy.setAttribute('transform', `rotate(${canopyRot.toFixed(3)} ${cx} ${cy})`);
    }
  }
}

// ============================================================
// Petal system — per dropping tree (independent)
// ============================================================
const SVGNS = 'http://www.w3.org/2000/svg';
const PETAL_A_D = "M10 4.27707C10 -0.585797 5.49102 -0.327917 3.23653 0.40888C-2.62514 2.17716 0.794169 9.61886 3.23653 13.1187C8.64731 16.6553 10 8.69787 10 4.27707Z";
const PETAL_B_D = "M9.22566 0.288806C-2.63738 -1.755 -0.79764 7.49108 2.3878 14.0918C2.98665 15.3327 4.65132 15.4704 5.48642 14.3744C12.1307 5.65496 10.8494 1.37637 9.22566 0.288806Z";
const PETAL_A_CX = 5,   PETAL_A_CY = 7;
const PETAL_B_CX = 5.5, PETAL_B_CY = 8;
const MAX_PETALS_PER_TREE = 60;

function createPetalNode(treeN) {
  const c = petalState[treeN].container;
  const g = document.createElementNS(SVGNS, 'g');
  const path = document.createElementNS(SVGNS, 'path');
  g.appendChild(path);
  g.setAttribute('transform', 'translate(-1000 -1000)');
  g.style.opacity = '0';
  c.appendChild(g);
  return { g, path, active: false };
}

function resetPetal(p, treeN) {
  const meta = TREES.find(t => t.n === treeN);
  const W = meta.width;
  const H = meta.height;
  // Spawn from upper portion (canopy area)
  p.x = rand(W * 0.10, W * 0.90);
  p.y = rand(0, H * 0.45);
  // Petal display size in viewBox units — scale so 12px tall ~ feels right
  // Vibma exports use 962-wide native (vs old 661), so adjust scale by ratio
  // baseScale 1.6–3.2 multiplied by per-tree sizeMul (0.2–2.0)
  const _sizeMul = petalState[treeN].sizeMul;
  p.scale = rand(1.6, 3.2) * _sizeMul;
  p.rot = rand(0, 360);
  p.spinSpeed = rand(25, 90) * (rng() < 0.5 ? -1 : 1);
  p.fallSpeed = rand(40, 95);
  p.driftBase = rng() < 0.85 ? rand(8, 50) : rand(-36, -8);
  p.swayFreq  = rand(0.4, 1.1);
  p.swayAmp   = rand(20, 45);
  p.swayPhase = rand(0, Math.PI * 2);
  p.age = 0;
  p.fadeIn = rand(0.5, 1.2);
  if (rng() < 0.5) {
    p.path.setAttribute('d', PETAL_A_D);
    p.path.setAttribute('fill', 'url(#pGradA)');
    p.cx = PETAL_A_CX; p.cy = PETAL_A_CY;
  } else {
    p.path.setAttribute('d', PETAL_B_D);
    p.path.setAttribute('fill', 'url(#pGradB)');
    p.cx = PETAL_B_CX; p.cy = PETAL_B_CY;
  }
  p.baseOpacity = rand(0.75, 1.0);
  p.active = true;
}

function spawnPetal(treeN) {
  const st = petalState[treeN];
  let p = st.freePool.pop();
  if (!p) {
    if (st.petals.length >= MAX_PETALS_PER_TREE) return;
    p = createPetalNode(treeN);
    st.petals.push(p);
  }
  resetPetal(p, treeN);
}

function recyclePetal(p, treeN) {
  p.active = false;
  p.g.setAttribute('transform', 'translate(-1000 -1000)');
  p.g.style.opacity = '0';
  petalState[treeN].freePool.push(p);
}

function tickSpawn(dt, treeN) {
  if (!PETALS_GLOBAL_ON) return;
  if (treeN !== activeTree) return;
  const st = petalState[treeN];
  st.spawnDebt += dt * st.spawnRate;
  while (st.spawnDebt >= 1) {
    spawnPetal(treeN);
    st.spawnDebt -= 1;
  }
}

function updatePetals(dt, tSec, treeN) {
  const meta = TREES.find(t => t.n === treeN);
  const H = meta.height;
  const st = petalState[treeN];
  const WIND = st.wind;
  const SPEED = st.speed;
  for (const p of st.petals) {
    if (!p.active) continue;
    p.age += dt;
    const sway = Math.sin(tSec * 2 * Math.PI * p.swayFreq + p.swayPhase) * p.swayAmp;
    const vx = (p.driftBase + sway * 0.6) * WIND;
    const vy = p.fallSpeed * (0.7 + 0.5 * WIND);
    p.x += vx * dt * SPEED;
    p.y += vy * dt * SPEED;
    p.rot += p.spinSpeed * dt * SPEED;
    let op = p.baseOpacity;
    if (p.age < p.fadeIn) op *= (p.age / p.fadeIn);
    if (p.y > H * 0.86) op *= Math.max(0, 1 - (p.y - H * 0.86) / (H * 0.10));
    p.g.style.opacity = op.toFixed(3);
    p.g.setAttribute('transform',
      `translate(${p.x.toFixed(2)} ${p.y.toFixed(2)}) ` +
      `rotate(${p.rot.toFixed(1)} ${p.cx} ${p.cy}) ` +
      `translate(${p.cx} ${p.cy}) scale(${p.scale.toFixed(3)}) translate(${-p.cx} ${-p.cy})`);
    if (p.y > H + 30 || p.x < -50 || p.x > meta.width + 50) {
      recyclePetal(p, treeN);
    }
  }
}

// ============================================================
// Tree switcher
// ============================================================
function switchTree(n) {
  activeTree = n;
  for (const t of TREES) {
    stages[t.n].classList.toggle('active', t.n === n);
  }
  // Recycle petals on previously active dropping trees (we only run active tree's petals)
  PETAL_TREES.forEach(pn => {
    const layer = petalLayers[pn];
    if (!layer) return;
    layer.classList.toggle('active', pn === n && PETALS_GLOBAL_ON);
    if (pn !== n) {
      // Recycle all to keep clean state
      petalState[pn].petals.forEach(p => { if (p.active) recyclePetal(p, pn); });
      petalState[pn].spawnDebt = 0;
    }
  });
  // Show only this tree's petal control panel (if it has one)
  document.querySelectorAll('.petal-control-group').forEach(g => {
    g.classList.toggle('active', +g.dataset.tree === n);
  });
  // Update button highlighting
  document.querySelectorAll('.tree-buttons button').forEach(btn => {
    btn.classList.toggle('active', +btn.dataset.tree === n);
  });
}

// ============================================================
// Main loop
// ============================================================
let last = now();
function tick() {
  const t = now();
  const dt = Math.min(0.05, (t - last) / 1000);
  last = t;
  const tSec = t / 1000;
  applySway(tSec);
  PETAL_TREES.forEach(pn => {
    if (pn === activeTree && PETALS_GLOBAL_ON) {
      tickSpawn(dt, pn);
      updatePetals(dt, tSec, pn);
    }
  });
  requestAnimationFrame(tick);
}

// ============================================================
// Init: setup canopy split + noise refine + bind controls
// ============================================================
function init() {
  // Refine noise globally
  refineNoise();
  // Setup canopy split for medium+ trees.
  // getBBox() requires the element to be visible — temporarily reveal each stage.
  TREES.forEach(t => {
    const stage = stages[t.n];
    const wasActive = stage.classList.contains('active');
    if (!wasActive) stage.style.display = 'block';
    setupSwayGroups(t.n);
    if (!wasActive) stage.style.display = '';
  });

  // Tree buttons
  document.querySelectorAll('.tree-buttons button').forEach(btn => {
    btn.addEventListener('click', () => switchTree(+btn.dataset.tree));
  });

  // Petal control sliders (per tree)
  document.querySelectorAll('.control-row input[type="range"]').forEach(input => {
    const treeN = +input.dataset.tree;
    const param = input.dataset.param;
    const valEl = document.querySelector(`.value[data-val="${param}"][data-tree="${treeN}"]`);
    input.addEventListener('input', () => {
      const v = +input.value;
      if (param === 'wind') {
        petalState[treeN].wind = v / 100;
        valEl.textContent = v + '%';
      } else if (param === 'speed') {
        petalState[treeN].speed = v / 100;
        valEl.textContent = (v / 100).toFixed(1) + '×';
      } else if (param === 'density') {
        petalState[treeN].spawnRate = v;
        valEl.textContent = v + '/s';
      } else if (param === 'size') {
        petalState[treeN].sizeMul = v / 100;
        valEl.textContent = (v / 100).toFixed(1) + '×';
      }
    });
  });

  // Global toggles
  document.getElementById('swayBtn').addEventListener('click', (e) => {
    SWAY_ON = !SWAY_ON;
    e.target.textContent = '摇摆 ' + (SWAY_ON ? 'ON' : 'OFF');
    e.target.classList.toggle('on', SWAY_ON);
  });
  document.getElementById('petalToggle').addEventListener('click', (e) => {
    PETALS_GLOBAL_ON = !PETALS_GLOBAL_ON;
    e.target.textContent = '花瓣开关 ' + (PETALS_GLOBAL_ON ? 'ON' : 'OFF');
    e.target.classList.toggle('on', PETALS_GLOBAL_ON);
    // Update visibility of active petal layer
    PETAL_TREES.forEach(pn => {
      const layer = petalLayers[pn];
      if (layer) layer.classList.toggle('active', pn === activeTree && PETALS_GLOBAL_ON);
      if (!PETALS_GLOBAL_ON) {
        petalState[pn].petals.forEach(p => { if (p.active) recyclePetal(p, pn); });
        petalState[pn].spawnDebt = 0;
      }
    });
  });
  document.getElementById('resetBtn').addEventListener('click', () => {
    PETAL_TREES.forEach(pn => {
      petalState[pn].petals.forEach(p => { if (p.active) recyclePetal(p, pn); });
      petalState[pn].spawnDebt = 0;
    });
  });

  switchTree(1);
  requestAnimationFrame(tick);
}

document.addEventListener('DOMContentLoaded', init);
"""

# Tree metadata for JS
import json
tree_meta_js = json.dumps([{"n": t["n"], "width": t["width"], "height": t["height"]} for t in TREES])
SCRIPT = SCRIPT.replace("__TREE_META__", tree_meta_js)

HEAD = HEAD.replace("__STAGE_W__", str(STAGE_W))
HEAD = HEAD.replace("__STAGE_H__", str(MAX_H))
TAIL = TAIL.replace("__TREE_BUTTONS__", TREE_BUTTONS)
TAIL = TAIL.replace("__PETAL_CONTROLS__", PETAL_CONTROLS)
TAIL = TAIL.replace("__SCRIPT__", SCRIPT)

OUTPUT = ROOT / "tree-sway-12.html"
OUTPUT.write_text(HEAD + STAGES + TAIL)
print(f"Wrote {OUTPUT}, {OUTPUT.stat().st_size} bytes")
