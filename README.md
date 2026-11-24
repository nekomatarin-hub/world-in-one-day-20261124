# The World in One Day: Tuesday 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/nekomatarin-hub/world-in-one-day-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/nekomatarin-hub/world-in-one-day-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

An entry for make.fun's **news-image-20261124** bounty: sum up one day's
world news in a single image.

The image is a newspaper front page for **Tuesday 24 November 2026**.
Its lead story is Ukraine's sea-drone strike on a Russian warship off
Libya; around it sit the day's other big stories — Russian strikes on
the Kyiv region, NATO's space-defence vow, Nvidia's CEO shake-up, the
US Democrats' House majority, and briefs from the UN, Japan, Indonesia
and the world of sport.

## How it is built

- `compose.py` renders the front page with Pillow: masthead, date band,
  a dominant lead story, two columns of secondary stories, an
  around-the-world briefs grid and a ticker. It is deterministic — the
  same bytes come out of every run.
- `entry.png` is the rendered page (1024 × 1024).
- `main.ts` is the entrypoint the grader runs: it copies the committed
  `entry.png` into the output directory (`/output`, or
  `MAKEFUN_OUTPUT_DIR` when run locally). Node 22, standard library
  only, no network.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Regenerate the image with:

```sh
python3 compose.py entry.png
```
