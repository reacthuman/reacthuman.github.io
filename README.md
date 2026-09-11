# reacthuman.github.io

Project page for **ReactHuman: A Physics-Grounded Benchmark for Human-Like Reactive
Decision-Making in Embodied Multimodal LLMs**. Served by GitHub Pages at
https://reacthuman.github.io (plain static HTML, no build step; `.nojekyll` disables Jekyll).

## Layout

- `index.html` — the whole page (hero, teaser, abstract, protocol walkthrough, 17-family gallery,
  adversarial probes, pipeline, metrics, results, model comparison, corpus stats, BibTeX).
- `static/css/style.css`, `static/js/main.js` — styling and hover-to-play / tabs / copy-BibTeX.
- `static/video/` — 6 s, 720p, h264 clips cut from benchmark rollouts (third-person camera).
- `static/img/` — posters, taxonomy thumbnails, paper figures, model-input frames.
- `tools/build_assets.py` — regenerates everything under `static/video` and `static/img` from the
  local benchmark outputs (edit the `FAMILIES` / `COMPARE` / `DEMO` tables to swap clips).

## Links

- Paper / arXiv: https://arxiv.org/abs/2609.10895
- Dataset: https://huggingface.co/datasets/Alan123/reacthuman-benchmark-scaled
- The Code button currently points at the GitHub org; update it when the code repo is public.
