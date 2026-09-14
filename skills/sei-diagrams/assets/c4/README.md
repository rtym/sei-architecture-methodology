# Vendored: C4-PlantUML

Third-party code. **Not** part of this plugin's own source — see [`LICENSE`](LICENSE).

| | |
|---|---|
| **Upstream** | <https://github.com/plantuml-stdlib/C4-PlantUML> |
| **Version** | `v2.10.0` (pinned) |
| **License** | MIT — © 2018 Ricardo Niepel ([`LICENSE`](LICENSE), copied verbatim from upstream) |
| **Modified?** | No. The five upstream files are byte-identical to the `v2.10.0` tag. |

## What's here

| File | Origin |
|------|--------|
| `C4.puml` | upstream `v2.10.0` — unmodified |
| `C4_Context.puml` | upstream `v2.10.0` — unmodified |
| `C4_Container.puml` | upstream `v2.10.0` — unmodified |
| `C4_Component.puml` | upstream `v2.10.0` — unmodified |
| `C4_Deployment.puml` | upstream `v2.10.0` — unmodified |
| `sei-c4-palette.puml` | **this project's own** — an SEI palette overlay, covered by the repository's own license |

## Why it's vendored rather than fetched

Upstream's documented include is `!include <C4/C4_Container.puml>`, which makes PlantUML fetch
the macros over the network at render time. Vendoring makes diagram rendering **offline,
reproducible and version-pinned** — a render can't change or break because upstream moved. The
upstream files support this directly: each one carries a `RELATIVE_INCLUDE` branch precisely so
the set can be used from a local copy.

## How to include them

`render-plantuml.sh` puts this directory's parent (`assets/`) on PlantUML's include path, so a
`.puml` anywhere on disk writes:

```
!include c4/C4_Container.puml     ' pick the level you need
!include c4/sei-c4-palette.puml   ' always AFTER the C4 include
```

Never `<C4/…>` (fetches from the network) and never with `../` (only resolves inside this repo).

## Updating to a newer upstream version

1. Replace the five upstream `.puml` files from the new tag — leave `sei-c4-palette.puml` alone.
2. Re-copy upstream's `LICENSE` verbatim (the copyright holder may have changed).
3. Update the version in the tables above **and** in the top-level `README.md`.
4. Run `bash tests/run.sh` — `validate.py --self` checks that the attribution is present and
   that the pinned version here matches the fallback URLs inside the vendored files.
