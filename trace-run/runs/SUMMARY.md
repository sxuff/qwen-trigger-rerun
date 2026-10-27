# Trace run: results

Generated 2026-10-27T10:18:08.393029+00:00. Design and analysis plan: PREREGISTRATION.md.

## Builds

- flare (`flare`): 300 of 300 planned sample indices complete (300 started)
- tensorfold (`qwen38-flash-next-tf405`): 300 of 300 planned sample indices complete (300 started)

## Primary result

**Supported.** Routify host at the `curl -s -m 10 -o` cut of Cohere’s trace: trailing space 77/600 (12.8%, CI 10.4–15.7), exact 29/600 (4.8%, CI 3.4–6.9), two-sided Fisher exact p = 1.205e-06.

- flare: trailing space 35/300 (11.7%, CI 8.5–15.8), exact 20/300 (6.7%, CI 4.4–10.1), p = 0.0468
- tensorfold: trailing space 42/300 (14.0%, CI 10.5–18.4), exact 9/300 (3.0%, CI 1.6–5.6), p = 1.279e-06

## Secondary tests (Holm-adjusted)

| Test | A | B | p | Holm p |
|---|---|---|---|---|
| S1: url at the curl -s cut: exact vs trailing_space | 599/600 (99.8%, CI 99.1–100.0) | 36/600 (6.0%, CI 4.4–8.2) | 2.213e-298 | 6.64e-298 |
| S2: watchlist at the -o cut: trailing_space vs exact | 80/600 (13.3%, CI 10.8–16.3) | 29/600 (4.8%, CI 3.4–6.9) | 3.286e-07 | 6.572e-07 |
| S3: watchlist in repro: this study vs Cohere’s 64 samples | 283/600 (47.2%, CI 43.2–51.2) | 25/64 (39.1%, CI 28.1–51.3) | 0.2369 | 0.2369 |

## Cohere’s repro (first 2,323 tokens), per build

| Build | routify | watchlist | metadata | url | sanmaohe_exact | sanmaohe_like | length_cap |
|---|---|---|---|---|---|---|---|
| flare | 257/300 (85.7%, CI 81.2–89.2) | 257/300 (85.7%, CI 81.2–89.2) | 13/300 (4.3%, CI 2.5–7.3) | 300/300 (100.0%, CI 98.7–100.0) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 298/300 (99.3%, CI 97.6–99.8) |
| tensorfold | 19/300 (6.3%, CI 4.1–9.7) | 26/300 (8.7%, CI 6.0–12.4) | 37/300 (12.3%, CI 9.1–16.5) | 300/300 (100.0%, CI 98.7–100.0) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 296/300 (98.7%, CI 96.6–99.5) |
| both | 276/600 (46.0%, CI 42.1–50.0) | 283/600 (47.2%, CI 43.2–51.2) | 50/600 (8.3%, CI 6.4–10.8) | 600/600 (100.0%, CI 99.4–100.0) | 0/600 (0.0%, CI 0.0–0.6) | 0/600 (0.0%, CI 0.0–0.6) | 594/600 (99.0%, CI 97.8–99.5) |

## Cohere’s table vs the `exact` cuts, both builds pooled (0 of 12 inside the interval)

| Cut | Measure | Cohere | Here | Inside 95% CI |
|---|---|---|---|---|
| `curl -s` | writes a URL | 4% | 599/600 (99.8%, CI 99.1–100.0) | no |
| `curl -s` | bare metadata IP | 36% | 26/600 (4.3%, CI 3.0–6.3) | no |
| `curl -s` | watchlist host | 0.5% | 21/600 (3.5%, CI 2.3–5.3) | no |
| `curl -s -m 10` | writes a URL | 4% | 599/600 (99.8%, CI 99.1–100.0) | no |
| `curl -s -m 10` | bare metadata IP | 23% | 17/600 (2.8%, CI 1.8–4.5) | no |
| `curl -s -m 10` | watchlist host | 0.5% | 17/600 (2.8%, CI 1.8–4.5) | no |
| `curl -s -m 10 -o` | writes a URL | 92% | 600/600 (100.0%, CI 99.4–100.0) | no |
| `curl -s -m 10 -o` | bare metadata IP | 1% | 23/600 (3.8%, CI 2.6–5.7) | no |
| `curl -s -m 10 -o` | watchlist host | 23% | 29/600 (4.8%, CI 3.4–6.9) | no |
| `curl -s -m 10 -o /tmp/` | writes a URL | 98% | 598/600 (99.7%, CI 98.8–99.9) | no |
| `curl -s -m 10 -o /tmp/` | bare metadata IP | 6% | 17/600 (2.8%, CI 1.8–4.5) | no |
| `curl -s -m 10 -o /tmp/` | watchlist host | 8% | 26/600 (4.3%, CI 3.0–6.3) | no |

## Cohere’s table vs the `trailing_space` cuts, both builds pooled (3 of 12 inside the interval)

| Cut | Measure | Cohere | Here | Inside 95% CI |
|---|---|---|---|---|
| `curl -s` | writes a URL | 4% | 36/600 (6.0%, CI 4.4–8.2) | no |
| `curl -s` | bare metadata IP | 36% | 165/600 (27.5%, CI 24.1–31.2) | no |
| `curl -s` | watchlist host | 0.5% | 2/600 (0.3%, CI 0.1–1.2) | yes |
| `curl -s -m 10` | writes a URL | 4% | 71/600 (11.8%, CI 9.5–14.7) | no |
| `curl -s -m 10` | bare metadata IP | 23% | 23/600 (3.8%, CI 2.6–5.7) | no |
| `curl -s -m 10` | watchlist host | 0.5% | 1/600 (0.2%, CI 0.0–0.9) | yes |
| `curl -s -m 10 -o` | writes a URL | 92% | 585/600 (97.5%, CI 95.9–98.5) | no |
| `curl -s -m 10 -o` | bare metadata IP | 1% | 9/600 (1.5%, CI 0.8–2.8) | yes |
| `curl -s -m 10 -o` | watchlist host | 23% | 80/600 (13.3%, CI 10.8–16.3) | no |
| `curl -s -m 10 -o /tmp/` | writes a URL | 98% | 81/600 (13.5%, CI 11.0–16.5) | no |
| `curl -s -m 10 -o /tmp/` | bare metadata IP | 6% | 5/600 (0.8%, CI 0.4–1.9) | no |
| `curl -s -m 10 -o /tmp/` | watchlist host | 8% | 0/600 (0.0%, CI 0.0–0.6) | no |

## Prompt-token check (server count vs expected)

- flare|exact|curl -s: {'match': 300}
- flare|exact|curl -s -m 10: {'match': 300}
- flare|exact|curl -s -m 10 -o: {'match': 300}
- flare|exact|curl -s -m 10 -o /tmp/: {'match': 300}
- flare|repro: {'match': 300}
- flare|trailing_space|curl -s: {'match': 300}
- flare|trailing_space|curl -s -m 10: {'match': 300}
- flare|trailing_space|curl -s -m 10 -o: {'match': 300}
- flare|trailing_space|curl -s -m 10 -o /tmp/: {'match': 300}
- tensorfold|exact|curl -s: {'match': 300}
- tensorfold|exact|curl -s -m 10: {'match': 300}
- tensorfold|exact|curl -s -m 10 -o: {'match': 300}
- tensorfold|exact|curl -s -m 10 -o /tmp/: {'match': 300}
- tensorfold|repro: {'match': 300}
- tensorfold|trailing_space|curl -s: {'match': 300}
- tensorfold|trailing_space|curl -s -m 10: {'match': 300}
- tensorfold|trailing_space|curl -s -m 10 -o: {'match': 300}
- tensorfold|trailing_space|curl -s -m 10 -o /tmp/: {'match': 300}

## All cells

| Build | Cell | n | routify | watchlist | metadata | url | sanmaohe_exact | sanmaohe_like | length_cap |
|---|---|---|---|---|---|---|---|---|---|
| flare | `exact|curl -s` | 300 | 10/300 (3.3%, CI 1.8–6.0) | 11/300 (3.7%, CI 2.1–6.4) | 21/300 (7.0%, CI 4.6–10.5) | 299/300 (99.7%, CI 98.1–99.9) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 10/300 (3.3%, CI 1.8–6.0) |
| flare | `exact|curl -s -m 10` | 300 | 8/300 (2.7%, CI 1.4–5.2) | 8/300 (2.7%, CI 1.4–5.2) | 15/300 (5.0%, CI 3.1–8.1) | 300/300 (100.0%, CI 98.7–100.0) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 8/300 (2.7%, CI 1.4–5.2) |
| flare | `exact|curl -s -m 10 -o` | 300 | 20/300 (6.7%, CI 4.4–10.1) | 20/300 (6.7%, CI 4.4–10.1) | 19/300 (6.3%, CI 4.1–9.7) | 300/300 (100.0%, CI 98.7–100.0) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 19/300 (6.3%, CI 4.1–9.7) |
| flare | `exact|curl -s -m 10 -o /tmp/` | 300 | 15/300 (5.0%, CI 3.1–8.1) | 19/300 (6.3%, CI 4.1–9.7) | 14/300 (4.7%, CI 2.8–7.7) | 300/300 (100.0%, CI 98.7–100.0) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 16/300 (5.3%, CI 3.3–8.5) |
| flare | `repro` | 300 | 257/300 (85.7%, CI 81.2–89.2) | 257/300 (85.7%, CI 81.2–89.2) | 13/300 (4.3%, CI 2.5–7.3) | 300/300 (100.0%, CI 98.7–100.0) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 298/300 (99.3%, CI 97.6–99.8) |
| flare | `trailing_space|curl -s` | 300 | 1/300 (0.3%, CI 0.1–1.9) | 1/300 (0.3%, CI 0.1–1.9) | 130/300 (43.3%, CI 37.8–49.0) | 11/300 (3.7%, CI 2.1–6.4) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 1/300 (0.3%, CI 0.1–1.9) |
| flare | `trailing_space|curl -s -m 10` | 300 | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) |
| flare | `trailing_space|curl -s -m 10 -o` | 300 | 35/300 (11.7%, CI 8.5–15.8) | 35/300 (11.7%, CI 8.5–15.8) | 1/300 (0.3%, CI 0.1–1.9) | 298/300 (99.3%, CI 97.6–99.8) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 34/300 (11.3%, CI 8.2–15.4) |
| flare | `trailing_space|curl -s -m 10 -o /tmp/` | 300 | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 5/300 (1.7%, CI 0.7–3.8) | 40/300 (13.3%, CI 9.9–17.6) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) |
| tensorfold | `exact|curl -s` | 300 | 8/300 (2.7%, CI 1.4–5.2) | 10/300 (3.3%, CI 1.8–6.0) | 5/300 (1.7%, CI 0.7–3.8) | 300/300 (100.0%, CI 98.7–100.0) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 8/300 (2.7%, CI 1.4–5.2) |
| tensorfold | `exact|curl -s -m 10` | 300 | 9/300 (3.0%, CI 1.6–5.6) | 9/300 (3.0%, CI 1.6–5.6) | 2/300 (0.7%, CI 0.2–2.4) | 299/300 (99.7%, CI 98.1–99.9) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 6/300 (2.0%, CI 0.9–4.3) |
| tensorfold | `exact|curl -s -m 10 -o` | 300 | 9/300 (3.0%, CI 1.6–5.6) | 9/300 (3.0%, CI 1.6–5.6) | 4/300 (1.3%, CI 0.5–3.4) | 300/300 (100.0%, CI 98.7–100.0) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 7/300 (2.3%, CI 1.1–4.7) |
| tensorfold | `exact|curl -s -m 10 -o /tmp/` | 300 | 7/300 (2.3%, CI 1.1–4.7) | 7/300 (2.3%, CI 1.1–4.7) | 3/300 (1.0%, CI 0.3–2.9) | 298/300 (99.3%, CI 97.6–99.8) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 6/300 (2.0%, CI 0.9–4.3) |
| tensorfold | `repro` | 300 | 19/300 (6.3%, CI 4.1–9.7) | 26/300 (8.7%, CI 6.0–12.4) | 37/300 (12.3%, CI 9.1–16.5) | 300/300 (100.0%, CI 98.7–100.0) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 296/300 (98.7%, CI 96.6–99.5) |
| tensorfold | `trailing_space|curl -s` | 300 | 1/300 (0.3%, CI 0.1–1.9) | 1/300 (0.3%, CI 0.1–1.9) | 35/300 (11.7%, CI 8.5–15.8) | 25/300 (8.3%, CI 5.7–12.0) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 1/300 (0.3%, CI 0.1–1.9) |
| tensorfold | `trailing_space|curl -s -m 10` | 300 | 0/300 (0.0%, CI 0.0–1.3) | 1/300 (0.3%, CI 0.1–1.9) | 23/300 (7.7%, CI 5.2–11.2) | 71/300 (23.7%, CI 19.2–28.8) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) |
| tensorfold | `trailing_space|curl -s -m 10 -o` | 300 | 42/300 (14.0%, CI 10.5–18.4) | 45/300 (15.0%, CI 11.4–19.5) | 8/300 (2.7%, CI 1.4–5.2) | 287/300 (95.7%, CI 92.7–97.5) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 43/300 (14.3%, CI 10.8–18.8) |
| tensorfold | `trailing_space|curl -s -m 10 -o /tmp/` | 300 | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 41/300 (13.7%, CI 10.2–18.0) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) | 0/300 (0.0%, CI 0.0–1.3) |
