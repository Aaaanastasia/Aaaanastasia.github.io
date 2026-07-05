/* =============================================================
   Anastasia — personal brand site, behavior layer.
   Input:  the static DOM from index.html.
   Output: (1) nav switches transparent → solid black on scroll,
           (2) sections fade/slide in once as they enter the
               viewport (skipped for reduced-motion users),
           (3) footer year stays current.
   No dependencies.
   ============================================================= */

// --- 1. Nav: transparent over the hero, solid black once scrolled ---
const nav = document.getElementById("nav");
const onScroll = () => nav.classList.toggle("is-scrolled", window.scrollY > 24);
window.addEventListener("scroll", onScroll, { passive: true });
onScroll(); // apply correct state on load (e.g. refresh mid-page)

// --- 2. Reveal-on-scroll via IntersectionObserver ---
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const revealables = document.querySelectorAll(".reveal");

if (reduceMotion || !("IntersectionObserver" in window)) {
  // Accessibility / fallback: show everything immediately
  revealables.forEach((el) => el.classList.add("in"));
} else {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target); // reveal once, then stop watching
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );
  revealables.forEach((el) => observer.observe(el));
}

// --- 3. Footer year ---
document.getElementById("year").textContent = new Date().getFullYear();

// --- 4. Hero data-constellation (index page only) ---
// Drifting points, connected when close — a live scatter plot as scenery.
// Skipped entirely for reduced-motion users; paused when the tab is hidden
// or the hero has scrolled out of view.
const canvas = document.getElementById("hero-canvas");
if (canvas && !reduceMotion) {
  const ctx = canvas.getContext("2d");
  const COLORS = ["#7089ba", "#7089ba", "#7089ba", "#57b3a1", "#e2b04a"]; // peri-weighted
  const LINK_DIST = 110;   // px distance under which two points connect
  let points = [];
  let running = true;      // false when hidden/off-screen
  let raf = 0;

  function resize() {
    // cap device-pixel-ratio at 1.5 — sharpness/perf tradeoff
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // point density scales with area, capped for perf
    const n = Math.min(90, Math.floor((rect.width * rect.height) / 16000));
    points = Array.from({ length: n }, () => ({
      x: Math.random() * rect.width,
      y: Math.random() * rect.height,
      vx: (Math.random() - 0.5) * 0.22,
      vy: (Math.random() - 0.5) * 0.22,
      c: COLORS[(Math.random() * COLORS.length) | 0],
    }));
  }

  function frame() {
    if (!running) return;
    const w = canvas.parentElement.clientWidth;
    const h = canvas.parentElement.clientHeight;
    ctx.clearRect(0, 0, w, h);

    // move + wrap at edges
    for (const p of points) {
      p.x = (p.x + p.vx + w) % w;
      p.y = (p.y + p.vy + h) % h;
    }
    // connecting lines first (under the dots)
    for (let i = 0; i < points.length; i++) {
      for (let j = i + 1; j < points.length; j++) {
        const dx = points[i].x - points[j].x;
        const dy = points[i].y - points[j].y;
        const d = Math.hypot(dx, dy);
        if (d < LINK_DIST) {
          ctx.strokeStyle = "rgba(112, 137, 186, " + (0.16 * (1 - d / LINK_DIST)).toFixed(3) + ")";
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(points[i].x, points[i].y);
          ctx.lineTo(points[j].x, points[j].y);
          ctx.stroke();
        }
      }
    }
    // dots
    for (const p of points) {
      ctx.globalAlpha = 0.65;
      ctx.fillStyle = p.c;
      ctx.fillRect(p.x - 1, p.y - 1, 2, 2); // square dots — drafting marks
      ctx.globalAlpha = 1;
    }
    raf = requestAnimationFrame(frame);
  }

  function setRunning(next) {
    if (next === running) return;
    running = next;
    if (running) frame();
    else cancelAnimationFrame(raf);
  }

  // pause when the tab is hidden or the hero scrolls away
  document.addEventListener("visibilitychange", () => {
    setRunning(!document.hidden);
  });
  new IntersectionObserver((entries) => {
    setRunning(entries[0].isIntersecting && !document.hidden);
  }).observe(canvas);

  let resizeTimer = 0;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(resize, 150);
  });

  resize();
  frame();
}
