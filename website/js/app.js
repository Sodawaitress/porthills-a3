/* ============================================================
   Port Hills 2017 — site behaviour
   scroll reveals · animated counters · correlation chart · lang toggle
   ============================================================ */

/* ---------- 1. reveal on scroll ---------- */
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

/* ---------- 2. animated counters ---------- */
function animateCount(el) {
  const target = parseFloat(el.dataset.count);
  const suffix = el.dataset.suffix || '';
  const decimals = (String(el.dataset.count).split('.')[1] || '').length;
  const dur = 1400, t0 = performance.now();
  function tick(now) {
    const p = Math.min((now - t0) / dur, 1);
    const eased = 1 - Math.pow(1 - p, 3);            // easeOutCubic
    const val = (target * eased).toFixed(decimals);
    el.textContent = Number(val).toLocaleString('en-US', {
      minimumFractionDigits: decimals, maximumFractionDigits: decimals
    }) + suffix;
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
const countIO = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { animateCount(e.target); countIO.unobserve(e.target); } });
}, { threshold: 0.5 });
document.querySelectorAll('[data-count]').forEach(el => countIO.observe(el));

/* ---------- 3. correlation chart (Pearson / Spearman toggle) ---------- */
// dNBR correlations, n = 186. Real values from 04e / report R4.
const CORR = {
  labels:   ['NDVI', 'BSI', 'pre_B5', 'northness', 'slope', 'pre_B4', 'elev'],
  pearson:  [ 0.475, -0.460,  0.254,     0.127,     0.019,  -0.210,  -0.014],
  spearman: [ 0.452, -0.441,  0.230,     0.238,     0.041,  -0.134,  -0.031],
  // pre_B4 is the one whose significance verdict flips between methods
  flip: 5
};

let corrChart;
function drawCorr(method) {
  const data = CORR[method];
  const colors = data.map((v, i) =>
    i === CORR.flip ? '#f2b705' : (v >= 0 ? '#ff6b35' : '#4aa3df'));
  if (!corrChart) {
    const ctx = document.getElementById('corrChart');
    if (!ctx) return;
    corrChart = new Chart(ctx, {
      type: 'bar',
      data: { labels: CORR.labels, datasets: [{ data, backgroundColor: colors, borderRadius: 4 }] },
      options: {
        indexAxis: 'y',
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: c => `r = ${c.raw.toFixed(3)}` } }
        },
        scales: {
          x: { min: -0.6, max: 0.6, grid: { color: '#2b211b' },
               ticks: { color: '#7c6d60', font: { family: 'monospace' } } },
          y: { grid: { display: false },
               ticks: { color: '#b8a99b', font: { family: 'monospace', size: 13 } } }
        },
        animation: { duration: 600 }
      }
    });
  } else {
    corrChart.data.datasets[0].data = data;
    corrChart.data.datasets[0].backgroundColor = colors;
    corrChart.update();
  }
}
drawCorr('pearson');
document.querySelectorAll('#corr-controls button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#corr-controls button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    drawCorr(btn.dataset.corr);
  });
});

/* ---------- 4. offset drift histogram (83.6 → 0) ---------- */
const OFF = (() => {
  const xs = [], raw = [], corr = [];
  const g = (x, m, s) => Math.exp(-((x - m) ** 2) / (2 * s * s));
  for (let x = -150; x <= 405; x += 15) { xs.push(x); raw.push(g(x, 83.6, 64.4)); corr.push(g(x, 0, 64.4)); }
  const mx = Math.max(...raw, ...corr);
  return { xs, raw: raw.map(v => v / mx * 100), corr: corr.map(v => v / mx * 100) };
})();
let offChart;
function drawOffset(mode) {
  const data = OFF[mode];
  const colour = mode === 'raw' ? '#d7263d' : '#3ddc84';
  if (!offChart) {
    const ctx = document.getElementById('offsetChart'); if (!ctx) return;
    offChart = new Chart(ctx, {
      type: 'bar',
      data: { labels: OFF.xs, datasets: [{ data, backgroundColor: colour, barPercentage: 1, categoryPercentage: 1 }] },
      options: {
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        scales: {
          x: { grid: { display: false },
               ticks: { color: '#7c6d60', font: { family: 'monospace', size: 10 },
                        callback: (v, i) => OFF.xs[i] % 60 === 0 ? OFF.xs[i] : '' } },
          y: { display: false, max: 112 }
        },
        animation: { duration: 950, easing: 'easeInOutCubic' }
      }
    });
  } else {
    offChart.data.datasets[0].data = data;
    offChart.data.datasets[0].backgroundColor = colour;
    offChart.update();
  }
}
drawOffset('raw');
document.querySelectorAll('#offset-controls button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#offset-controls button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    drawOffset(btn.dataset.off);
  });
});

/* ---------- 5. threshold sensitivity slider ---------- */
(function () {
  const s = document.getElementById('tSlider'); if (!s) return;
  const covered = 1594.1;
  const pts = [[68.7, 1344], [118.7, 1268], [168.7, 1177]];   // grid: centre real (1,268), ends approx — rerun pending
  function burnedAt(t) {
    if (t <= pts[0][0]) return pts[0][1];
    if (t >= pts[2][0]) return pts[2][1];
    const seg = t <= pts[1][0] ? [pts[0], pts[1]] : [pts[1], pts[2]];
    const [x0, y0] = seg[0], [x1, y1] = seg[1];
    return y0 + (y1 - y0) * (t - x0) / (x1 - x0);
  }
  const fmt = n => Math.round(n).toLocaleString('en-US');
  function upd() {
    const t = parseFloat(s.value), b = burnedAt(t);
    document.getElementById('tBurned').textContent = fmt(b) + ' ha';
    document.getElementById('tUnburned').textContent = fmt(covered - b) + ' ha unburnt';
    document.getElementById('tVal').textContent = 'T = ' + t.toFixed(1);
  }
  s.addEventListener('input', upd); upd();
})();

/* ---------- 5b. true-colour timeline: crossfade + burn-spread ---------- */
(function () {
  const base = document.getElementById('tlBase'), top = document.getElementById('tlTop');
  if (!base || !top) return;
  const TL = [
    { img: 'fire_pre_truecolour.png',          date: '24 Jan 2017 · Sentinel-2', title: 'Before',
      text: 'Green hills — farms, homes and native bush, exactly as everyone knew them.' },
    { img: '2017-02-13_truecolour.png',        date: '13 Feb 2017 · Sentinel-2', title: 'The day it started',
      text: 'Fire breaks out. The grey smoke plume is so big you can see it from space.' },
    { img: '2017-02-23_S2_10m_truecolour.png', date: '13–23 Feb 2017 · Sentinel-2', title: 'The fire spreads',
      text: 'From two ignition points the fire raced up the ridges at 30 m a minute — 230 hectares black by 9 pm on the first night, and still spreading for days.' },
    { img: 'fire_recovery_truecolour.png',     date: '3 Feb 2018 · Sentinel-2', title: 'A year later',
      text: 'Slowly growing back — but a year on, you can still see the mark the fire left.' }
  ];
  const IGNITION = '52% 58%';   // Point of Origin (Early Valley) in-frame, drives the burn spread
  const elDate = document.getElementById('tlDate'), elTitle = document.getElementById('tlTitle'),
        elText = document.getElementById('tlText'), bar = document.getElementById('tlBar'),
        btns = [...document.querySelectorAll('#tlControls button[data-i]')],
        playBtn = document.getElementById('tlPlay');
  let cur = 0, timer = null, busy = false;

  TL.forEach(f => { const i = new Image(); i.src = 'assets/' + f.img; });

  function setCaption(i) {
    const f = TL[i];
    elDate.textContent = f.date; elTitle.textContent = f.title; elText.textContent = f.text;
    btns.forEach(b => b.classList.toggle('active', +b.dataset.i === i));
    bar.style.width = ((i + 1) / TL.length * 100) + '%';
  }

  const WIPE = 1100;   // ms, consistent for every step
  function go(i) {
    if (busy || i === cur) return;
    busy = true;
    top.src = 'assets/' + TL[i].img;
    setCaption(i);
    // always the same left → right wipe, so the direction of change reads clearly
    top.style.transition = 'none';
    top.style.opacity = '1';
    top.style.clipPath = 'inset(0 100% 0 0)';
    requestAnimationFrame(() => requestAnimationFrame(() => {
      top.style.transition = 'clip-path ' + WIPE + 'ms cubic-bezier(.4,0,.2,1)';
      top.style.clipPath = 'inset(0 0 0 0)';
    }));
    setTimeout(() => finish(i), WIPE + 60);
  }
  function finish(i) {
    base.src = 'assets/' + TL[i].img;
    top.style.transition = 'none';
    top.style.clipPath = 'inset(0 100% 0 0)';
    cur = i; busy = false;
  }

  btns.forEach(b => b.addEventListener('click', () => { stop(); go(+b.dataset.i); }));

  function stop() { if (timer) { clearTimeout(timer); timer = null; playBtn.textContent = '▶ play'; } }
  function step() {
    const next = (cur + 1) % TL.length;
    go(next);
    timer = setTimeout(step, 2600);   // same dwell on every frame

  }
  function play() {
    if (timer) { stop(); return; }
    playBtn.textContent = '❚❚ pause';
    step();
  }
  playBtn.addEventListener('click', play);
  setCaption(0);
})();

/* ---------- 6. image compare sliders (make maps legible) ---------- */
document.querySelectorAll('.compare').forEach(c => {
  const top = c.querySelector('.cmp-top');
  const range = c.querySelector('.cmp-range');
  const div = c.querySelector('.cmp-divider');
  function set(v) { top.style.clipPath = `inset(0 0 0 ${v}%)`; div.style.left = v + '%'; }
  range.addEventListener('input', () => set(range.value));
  set(50);
});

/* ---------- 7. language toggle (EN ready; 中 scaffold) ---------- */
// Chinese strings get filled in next pass. English is the live content.
document.querySelectorAll('#lang button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#lang button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.documentElement.lang = btn.dataset.lang === 'zh' ? 'zh' : 'en';
    // i18n swap hooks here once zh copy lands.
  });
});
