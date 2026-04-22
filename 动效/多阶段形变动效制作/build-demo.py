#!/usr/bin/env python3
"""Build the prayer tree growth morphing demo.
Reads all 6 frame SVGs, fixes noise, inlines them, and generates demo.html
with real SVG path morphing (point sampling + interpolation).
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))

FRAMES = [
    ("F1-种子", "整颗 54.svg", 34, 4),
    ("F2-小芽", "整颗.svg", 65, 92),
    ("F3-分叉", "整颗.svg", 130, 153),
    ("F4-小树", "整颗.svg", 132, 226),
    ("F5-中树", "整颗.svg", 312, 384),
    ("F6-满开", "整颗.svg", 661, 527),
]

# Common coordinate space = F6 viewBox
CW, CH = 661, 527

def fix_noise(svg_text):
    """Reduce noise coarseness and opacity."""
    svg_text = re.sub(r'baseFrequency="10 10"', 'baseFrequency="0.65 0.65"', svg_text)
    # Reduce all flood-color opacities by ~60%
    def reduce_opacity(m):
        prefix = m.group(1)
        val = float(m.group(2))
        new_val = round(val * 0.4, 2)
        return f'flood-color="{prefix}{new_val})"'
    svg_text = re.sub(r'flood-color="(rgba\([^)]+,\s*)(\d+\.?\d*)\)"', reduce_opacity, svg_text)
    return svg_text

def prefix_ids(svg_text, prefix):
    """Namespace IDs to avoid conflicts when inlining multiple SVGs."""
    # Find all id="..." and url(#...)
    ids_found = set(re.findall(r'id="([^"]+)"', svg_text))
    for old_id in ids_found:
        new_id = f"{prefix}{old_id}"
        svg_text = svg_text.replace(f'id="{old_id}"', f'id="{new_id}"')
        svg_text = svg_text.replace(f'url(#{old_id})', f'url(#{new_id})')
    return svg_text

def read_svg(folder, filename):
    path = os.path.join(BASE, folder, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# Build SVG data
svg_contents = []
for i, (folder, filename, w, h) in enumerate(FRAMES):
    raw = read_svg(folder, filename)
    fixed = fix_noise(raw)
    prefixed = prefix_ids(fixed, f"f{i}_")
    svg_contents.append(prefixed)

# Calculate transforms (bottom-center align in CW x CH space)
transforms = []
for _, _, w, h in FRAMES:
    tx = (CW - w) / 2
    ty = CH - h
    transforms.append((tx, ty))

# Generate HTML
html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>祈祷树生长动画 — Path Morphing Demo</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: #F5F0E8;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  color: #5A4A3A;
}}
.stage {{
  position: relative;
  width: 500px; height: 420px;
}}
/* Resting-state images (full visual quality) */
.rest-frame {{
  position: absolute; bottom: 10px; left: 50%;
  transform-origin: bottom center;
  pointer-events: none;
  display: none;
}}
.rest-frame.visible {{ display: block; }}

/* Morph canvas */
#morphSvg {{
  position: absolute; bottom: 10px; left: 50%;
  width: 500px; height: 399px;
  margin-left: -250px;
  display: none;
}}

.ground {{
  position: absolute; bottom: 0; left: 50%;
  transform: translateX(-50%);
  width: 60px; height: 14px;
  background: radial-gradient(ellipse at center, rgba(123,89,83,0.15) 0%, transparent 70%);
  border-radius: 50%;
  transition: width 2s cubic-bezier(0.25,0.46,0.45,0.94);
}}

.controls {{
  margin-top: 20px;
  display: flex; flex-direction: column;
  align-items: center; gap: 10px;
}}
.day-buttons {{ display: flex; gap: 10px; }}
.day-btn {{
  padding: 10px 18px;
  background: transparent;
  border: 2px solid #C5B9A8;
  border-radius: 24px;
  font-size: 14px; font-weight: 500;
  color: #8B7355;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 56px;
  user-select: none;
}}
.day-btn:hover:not(:disabled):not(.active) {{
  border-color: #7B5953; color: #7B5953;
  background: rgba(123,89,83,0.05);
}}
.day-btn.active {{
  background: #7B5953; border-color: #7B5953; color: #F5F0E8;
}}
.day-btn:disabled {{ opacity: 0.3; cursor: not-allowed; }}
.info {{ font-size: 13px; color: #A89880; height: 18px; }}
</style>
</head>
<body>

<div class="stage" id="stage">
'''

# Add resting-state images using demo-assets (with noise fixed)
SCALE = 400 / CH  # F6 fills ~400px height
rest_sizes = []
for i, (folder, filename, w, h) in enumerate(FRAMES):
    dw = max(20, w * SCALE)
    dh = max(6, h * SCALE)
    rest_sizes.append((dw, dh))
    vis = ' visible' if i == 0 else ''
    html += f'''  <div class="rest-frame{vis}" id="rest{i}"
       style="width:{dw:.1f}px; height:{dh:.1f}px; margin-left:{-dw/2:.1f}px;">
    <img src="demo-assets/{folder}_{'整颗_54' if i==0 else '整颗'}.svg"
         style="width:100%;height:100%" draggable="false">
  </div>
'''

html += '''  <svg id="morphSvg" viewBox="0 0 661 527" preserveAspectRatio="xMidYMax meet"
       xmlns="http://www.w3.org/2000/svg"></svg>
  <div class="ground" id="ground"></div>
</div>

<div class="controls">
  <div class="day-buttons">
    <button class="day-btn" onclick="goToDay(0)">Mon</button>
    <button class="day-btn" onclick="goToDay(1)" disabled>Tue</button>
    <button class="day-btn" onclick="goToDay(2)" disabled>Wed</button>
    <button class="day-btn" onclick="goToDay(3)" disabled>Thu</button>
    <button class="day-btn" onclick="goToDay(4)" disabled>Fri</button>
  </div>
  <div class="info" id="info">种子</div>
</div>

<!-- Hidden SVGs for path parsing (display:none, not rendered) -->
<div id="hiddenSvgs" style="position:absolute;left:-9999px;top:-9999px;width:0;height:0;overflow:hidden;">
'''

# Add hidden SVGs with coordinate transforms
for i, ((folder, filename, w, h), (tx, ty)) in enumerate(zip(FRAMES, transforms)):
    content = svg_contents[i]
    # Wrap in a transformed group. Extract inner content from <svg>...</svg>
    inner = re.sub(r'<svg[^>]*>', '', content, count=1)
    inner = re.sub(r'</svg>\s*$', '', inner)
    html += f'''  <svg id="hiddenF{i}" viewBox="0 0 {CW} {CH}" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate({tx},{ty})">
      {inner}
    </g>
  </svg>
'''

html += '''</div>

<script>
// === Configuration ===
const FRAME_COUNT = 6;
const NAMES = ['种子','小芽','分叉','小树','中树','满开'];
const GROUND_W = [60, 80, 110, 130, 200, 340];
const DAY_TARGETS = [1, 2, 3, 4, 5];
const SAMPLE_POINTS = 120; // points per path for morphing

let currentFrame = 0;
let transitioning = false;
let morphData = []; // [{paths: [{points:[], color:''}]}]

const morphSvg = document.getElementById('morphSvg');
const buttons = document.querySelectorAll('.day-btn');
const info = document.getElementById('info');
const ground = document.getElementById('ground');

// === Initialization: parse paths from hidden SVGs ===
function init() {
  for (let i = 0; i < FRAME_COUNT; i++) {
    const svg = document.getElementById('hiddenF' + i);
    const pathEls = svg.querySelectorAll('path');
    const framePaths = [];

    pathEls.forEach(p => {
      const d = p.getAttribute('d');
      if (!d || d.trim().length < 5) return;

      // Get transformed points using getPointAtLength
      const totalLen = p.getTotalLength();
      if (totalLen < 1) return;

      const points = [];
      for (let j = 0; j < SAMPLE_POINTS; j++) {
        const t = j / (SAMPLE_POINTS - 1);
        const pt = p.getPointAtLength(t * totalLen);
        points.push([pt.x, pt.y]);
      }

      // Extract fill color
      let color = p.getAttribute('fill') || '#7B5953';
      if (color.startsWith('url(')) {
        // Resolve gradient - get first stop color
        const gradId = color.match(/url\\(#([^)]+)\\)/)?.[1];
        if (gradId) {
          const grad = svg.querySelector('#' + CSS.escape(gradId));
          if (grad) {
            const stop = grad.querySelector('stop');
            if (stop) color = stop.getAttribute('stop-color') || '#7B5953';
          }
        }
      }

      framePaths.push({ points, color, area: computeArea(points) });
    });

    // Sort paths by area (largest first = trunk first)
    framePaths.sort((a, b) => b.area - a.area);
    morphData.push({ paths: framePaths });
  }
}

function computeArea(pts) {
  let area = 0;
  for (let i = 0; i < pts.length; i++) {
    const j = (i + 1) % pts.length;
    area += pts[i][0] * pts[j][1];
    area -= pts[j][0] * pts[i][1];
  }
  return Math.abs(area) / 2;
}

// === Path matching between frames ===
function matchPaths(fromPaths, toPaths) {
  // Returns array of {from: points|null, to: points|null, fromColor, toColor}
  const pairs = [];
  const maxLen = Math.max(fromPaths.length, toPaths.length);

  for (let i = 0; i < maxLen; i++) {
    const fp = fromPaths[i] || null;
    const tp = toPaths[i] || null;

    if (fp && tp) {
      pairs.push({
        from: fp.points,
        to: tp.points,
        fromColor: fp.color,
        toColor: tp.color
      });
    } else if (fp && !tp) {
      // Source path shrinks to its centroid
      const cx = fp.points.reduce((s, p) => s + p[0], 0) / fp.points.length;
      const cy = fp.points.reduce((s, p) => s + p[1], 0) / fp.points.length;
      const vanishPts = fp.points.map(() => [cx, cy]);
      pairs.push({
        from: fp.points,
        to: vanishPts,
        fromColor: fp.color,
        toColor: fp.color
      });
    } else if (!fp && tp) {
      // Target path grows from its centroid
      const cx = tp.points.reduce((s, p) => s + p[0], 0) / tp.points.length;
      const cy = tp.points.reduce((s, p) => s + p[1], 0) / tp.points.length;
      const spawnPts = tp.points.map(() => [cx, cy]);
      pairs.push({
        from: spawnPts,
        to: tp.points,
        fromColor: tp.color,
        toColor: tp.color
      });
    }
  }
  return pairs;
}

// === Color interpolation ===
function parseColor(hex) {
  hex = hex.replace('#', '');
  if (hex.length === 3) hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
  return [parseInt(hex.slice(0,2),16), parseInt(hex.slice(2,4),16), parseInt(hex.slice(4,6),16)];
}

function lerpColor(c1, c2, t) {
  const a = parseColor(c1), b = parseColor(c2);
  const r = Math.round(a[0] + (b[0]-a[0])*t);
  const g = Math.round(a[1] + (b[1]-a[1])*t);
  const bl = Math.round(a[2] + (b[2]-a[2])*t);
  return `rgb(${r},${g},${bl})`;
}

// === Interpolate points ===
function lerpPoints(from, to, t) {
  return from.map((p, i) => [
    p[0] + (to[i][0] - p[0]) * t,
    p[1] + (to[i][1] - p[1]) * t,
  ]);
}

function pointsToPathD(pts) {
  if (pts.length === 0) return '';
  let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
  for (let i = 1; i < pts.length; i++) {
    d += ` L${pts[i][0].toFixed(1)},${pts[i][1].toFixed(1)}`;
  }
  return d + ' Z';
}

// === Render morphed frame ===
function renderMorph(pairs, t) {
  // Clear SVG
  while (morphSvg.firstChild) morphSvg.removeChild(morphSvg.firstChild);

  pairs.forEach(pair => {
    const pts = lerpPoints(pair.from, pair.to, t);
    const color = lerpColor(pair.fromColor, pair.toColor, t);
    const pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    pathEl.setAttribute('d', pointsToPathD(pts));
    pathEl.setAttribute('fill', color);
    morphSvg.appendChild(pathEl);
  });
}

// === Transition animation ===
function goToDay(dayIdx) {
  if (transitioning) return;
  const target = DAY_TARGETS[dayIdx];
  if (target <= currentFrame) return;

  buttons[dayIdx].classList.add('active');
  if (dayIdx + 1 < buttons.length) {
    buttons[dayIdx + 1].disabled = false;
  }

  chainTransition(currentFrame, target);
}

async function chainTransition(from, to) {
  transitioning = true;
  for (let i = from; i < to; i++) {
    await doMorphTransition(i, i + 1);
  }
  currentFrame = to;
  transitioning = false;
  info.textContent = NAMES[to];
}

function doMorphTransition(fromIdx, toIdx) {
  return new Promise(resolve => {
    const pairs = matchPaths(morphData[fromIdx].paths, morphData[toIdx].paths);
    const duration = 2000;

    // Hide resting images, show morph canvas
    document.querySelectorAll('.rest-frame').forEach(el => el.classList.remove('visible'));
    morphSvg.style.display = 'block';

    // Start at t=0 (show from frame)
    renderMorph(pairs, 0);

    const startTime = performance.now();

    function tick(now) {
      const elapsed = now - startTime;
      const rawT = Math.min(elapsed / duration, 1);
      // Ease: slow start, smooth middle, slow end
      const t = easeInOutCubic(rawT);

      renderMorph(pairs, t);

      // Update ground
      const gw = GROUND_W[fromIdx] + (GROUND_W[toIdx] - GROUND_W[fromIdx]) * t;
      ground.style.width = gw + 'px';

      if (rawT < 1) {
        requestAnimationFrame(tick);
      } else {
        // Morph done — show resting image for full visual quality
        morphSvg.style.display = 'none';
        document.getElementById('rest' + toIdx).classList.add('visible');
        resolve();
      }
    }

    requestAnimationFrame(tick);
  });
}

function easeInOutCubic(t) {
  return t < 0.5 ? 4*t*t*t : 1 - Math.pow(-2*t+2, 3)/2;
}

// === Start ===
init();
</script>
</body>
</html>
'''

# Write output
out_path = os.path.join(BASE, 'demo.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Generated: {out_path}")
print(f"Total size: {len(html)} bytes ({len(html)//1024} KB)")
