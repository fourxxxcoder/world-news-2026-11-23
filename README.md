# world-news-2026-11-23

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/fourxxxcoder/world-news-2026-11-23/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/fourxxxcoder/world-news-2026-11-23/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A single-file, standard-library-only Python program that draws one
1024×1024 broadsheet poster summing up the world news of Monday
23 November 2026 and writes it to `/output/entry.png`.

The front page leads with the Gulf war widening — Iran saying it
struck U.S. air defences in Bahrain, a Houthi missile aimed at Saudi
Arabia, tankers hit in the Strait of Hormuz — and the collapse of
the COP31 climate talks in Antalya. Around them: the war in Ukraine,
the EU–Indonesia trade deal, a South Korean minister resigning over
an AI exam-cheating scandal, Nepal's prime minister meeting Modi in
Delhi, a factory fire in Indonesia, India's record 720/9 Test total
in Wellington, a capsized boat in Nigeria, a cost-of-living march in
Lisbon, and Singapore's prime minister landing in Australia.
11 stories, 6 regions, one page.

No network and no dependencies: the picture is painted on a flat RGB
raster with a hand-built 5×7 bitmap typeface and saved by a small
hand-rolled PNG writer, so two runs give byte-identical output.
The reporting behind every line is listed in `SOURCES.md`.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=ck3acpkm&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
