/* ReactHuman project page — small vanilla-JS helpers (no build step). */
(function () {
  'use strict';

  const isTouch = window.matchMedia('(hover: none)').matches;

  /* ---- hover-to-play cards (family grid, model comparison) -------------- */
  function bindHoverPlay(card) {
    const v = card.querySelector('video');
    if (!v) return;
    v.muted = true; v.loop = true; v.playsInline = true; v.preload = 'metadata';
    const start = () => { v.play().then(() => card.classList.add('is-playing')).catch(() => {}); };
    const stop = () => { v.pause(); v.currentTime = 0; card.classList.remove('is-playing'); };
    if (isTouch) {
      v.addEventListener('click', () => (v.paused ? start() : stop()));
    } else {
      card.addEventListener('mouseenter', start);
      card.addEventListener('mouseleave', stop);
      v.addEventListener('click', () => (v.paused ? start() : stop()));
    }
    card._start = start; card._stop = stop;
  }
  document.querySelectorAll('.vcard, .cmp').forEach(bindHoverPlay);

  /* ---- "play all / pause all" buttons ----------------------------------- */
  document.querySelectorAll('[data-playall]').forEach((btn) => {
    const sel = btn.getAttribute('data-playall');
    let on = false;
    btn.addEventListener('click', () => {
      on = !on;
      document.querySelectorAll(sel).forEach((c) => (on ? c._start && c._start() : c._stop && c._stop()));
      btn.textContent = on ? '⏸ Pause all' : '▶ Play all';
    });
  });

  /* ---- autoplay-when-visible (teaser + protocol demo) ------------------- */
  const auto = document.querySelectorAll('video[data-autoplay]');
  auto.forEach((v) => { v.muted = true; v.loop = true; v.playsInline = true; });
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        const v = e.target;
        if (e.isIntersecting) v.play().catch(() => {}); else v.pause();
      });
    }, { threshold: 0.25 });
    auto.forEach((v) => io.observe(v));
  } else {
    auto.forEach((v) => v.play().catch(() => {}));
  }

  /* ---- tabs ------------------------------------------------------------- */
  document.querySelectorAll('[role="tablist"]').forEach((list) => {
    const tabs = list.querySelectorAll('[role="tab"]');
    tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        tabs.forEach((t) => {
          const on = t === tab;
          t.setAttribute('aria-selected', on ? 'true' : 'false');
          const panel = document.getElementById(t.getAttribute('aria-controls'));
          if (panel) {
            panel.hidden = !on;
            if (!on) panel.querySelectorAll('.cmp').forEach((c) => c._stop && c._stop());
          }
        });
      });
    });
  });

  /* ---- copy BibTeX ------------------------------------------------------ */
  const copyBtn = document.querySelector('.copy');
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      const pre = document.getElementById('bibtex-text');
      try {
        await navigator.clipboard.writeText(pre.textContent);
        copyBtn.textContent = 'Copied ✓';
      } catch (_) {
        copyBtn.textContent = 'Select & copy';
      }
      setTimeout(() => (copyBtn.textContent = 'Copy'), 1600);
    });
  }
})();
