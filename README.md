# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Daniikhwan/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Daniikhwan/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A deterministic, standard-library-only Python program that draws one newspaper-style poster summing up the world news of Wednesday 25 November 2026: the CIA and ODNI cyber breach, the Australia–Solomon Islands defence pact, the UN femicide report (47,000 women killed by partners or family in 2025), Asia's tariff-driven market slide, the Houthi strike on Riyadh's tallest tower, and the WHO Ebola evacuation in Congo. Every story was first reported on 25 November 2026 and checked against Reuters, CNN, UN Women / UNODC and WHO reporting of that day. Run it and it writes `entry.png` — a 1024×1024 poster with the date up top and six stories across regions and beats.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program needs nothing but Python 3 and its standard library: no network, no randomness, no clocks, so two runs write identical bytes.

---

<sub>Entered on [make.fun](https://make.fun/?ref=vnsny7za&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
