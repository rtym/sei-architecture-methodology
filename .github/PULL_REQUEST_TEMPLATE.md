# What this changes

<!-- Two or three plain sentences: what changed and why. Link the issue if there is one. -->

# Checklist

Contributor rules live in [`CLAUDE.md`](../CLAUDE.md); the ones a PR most often trips on:

- [ ] `bash tests/run.sh` passes (or `--quick` plus a note on which render job CI must confirm)
- [ ] `claude plugin validate .` passes
- [ ] Behaviour changes update the **skill AND its template AND both worked examples** under
      `examples/` — they are the regression fixtures
- [ ] Re-rendered every diagram whose source changed (`scripts/render-all.sh <dir>`), opened the
      PNGs and checked them before committing
- [ ] Cross-file paths in commands / skills / templates / references are
      `${CLAUDE_PLUGIN_ROOT}`-anchored; PlantUML `!include`s are bare, assets-relative names
- [ ] `CHANGELOG.md` has a line under an *Unreleased* heading
- [ ] Release PRs only: version bumped in `.claude-plugin/plugin.json` **and both** fields in
      `.claude-plugin/marketplace.json`; *Unreleased* renamed to the version + date

# How it was verified

<!-- Paste the relevant test output tail, name the example files that act as fixtures for the
     change, or say which CI job proves it. -->
