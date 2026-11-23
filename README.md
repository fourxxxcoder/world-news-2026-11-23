# The Daily Orbit — world news of 23 November 2026 in one image

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123)

`main.py` draws a single 1024x1024 PNG broadsheet that sums up the
world news of Monday 23 November 2026. The hero story is the collapse
of the COP31 climate talks in Antalya — no deal after the words
"fossil fuels" vanished from the draft pact — and below it a
three-column gazette carries 15 more sourced stories from six
continents: missiles crossing into Poland, an Iranian strike on
Bahrain, 24 killed in South Sudan, an Ebola response under fire in
Congo, a factory fire in Indonesia, a cartel boss captured in Mexico,
and Liverpool's 4-0 rout of Manchester United, among others.

## How it works

- Pure Python 3.13 standard library — no third-party packages, no
  network, no randomness, no clock reads. Two runs are byte-identical.
- A hand-rolled RGB framebuffer, a 5x7 bitmap typeface defined in the
  source, greedy word wrap, and a height-balanced column-flow layout
  render the page; a small `zlib`/`struct` writer encodes the PNG.
- Every story was researched on the morning of 23 Nov 2026; the
  reporting behind each item is listed in `SOURCES.md`.

## Run

```sh
python3 main.py
```

Writes `poster.png` into `$MAKEFUN_OUTPUT_DIR` (default `/output`).

## License

MIT — see `LICENSE`.
