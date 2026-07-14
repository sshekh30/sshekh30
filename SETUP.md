# sshekh30/sshekh30 — profile card

This repo powers the animated terminal card on my GitHub profile. The card is a
pair of themed SVGs (dark + light) generated from a single Python script.

> **Current mode: static.** The card shows fixed content that I edit and
> regenerate by hand. The live GitHub-stats automation is present but
> **disabled** — see [Optional: live stats](#optional-live-github-stats) to turn
> it back on.

## What's in here

| File | Purpose | Needed at runtime? |
|------|---------|--------------------|
| `README.md` | The profile page. Uses `<picture>` to auto-switch dark/light. | yes |
| `dark_mode.svg` / `light_mode.svg` | The two themed cards (the actual output). | yes |
| `generate_svg.py` | Source generator — edit this to change the card. | no (build-time) |
| `ascii_v2.txt` | The ASCII portrait characters, read by `generate_svg.py`. | no (build-time) |
| `update_stats.py` | Fetches GitHub stats into the SVGs. **Dormant** while stats are off. | only if stats on |
| `.github/workflows/update-stats.yml` | Scheduled runner for the stats script. **Disabled.** | only if stats on |
| `cache/` | Leftover LOC cache from when stats ran. Safe to delete. | no |
| `SETUP.md` | This file. | no |

## How it renders

GitHub shows the `README.md` of the repo named after my username on my profile.
`README.md` is just a `<picture>` block that serves `dark_mode.svg` to viewers on
dark theme and `light_mode.svg` to viewers on light theme:

```markdown
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./dark_mode.svg">
  <source media="(prefers-color-scheme: light)" srcset="./light_mode.svg">
  <img alt="Satyam Shekhar" src="./light_mode.svg">
</picture>
```

The typing/fade-in animation plays when the image loads. The card is embedded as
an image, so text inside it (including the Contact section) is **display-only —
not clickable** on GitHub. That's a GitHub sandbox limitation, not a bug.

## Editing the card (the normal loop)

All content lives in the `CONTENT` list near the top of `generate_svg.py`. Each
entry is one of:

```python
("field", "Label", "Value")      # a labelled row (wraps automatically)
("header", "Section Name")       # a "- Section -" divider
("spacer",)                      # a blank line
```

To change anything — add/reword a line, reorder sections, tweak colors — edit
`generate_svg.py`, then run the generator and push. **`ascii_v2.txt` must be in
the same folder** when you run it (the script reads the portrait from it):

```bash
cd path/to/repo            # folder with generate_svg.py + ascii_v2.txt
python generate_svg.py     # overwrites dark_mode.svg + light_mode.svg
git add dark_mode.svg light_mode.svg
git commit -m "update profile card"
git push
```

Then hard-refresh the profile (Cmd/Ctrl+Shift+R) — GitHub caches the image, so
changes can take a minute to appear.

### Handy tips
- **Comment out a line** instead of deleting it — prefix with `#`. Great for
  temporarily hiding a section (that's how the GitHub Stats block is parked).
- **Colors** live in the `THEMES` dict (`dark` and `light`). Change a hex value,
  regenerate, done.
- **Width / wrapping**: `MAX_VAL` controls how long a value gets before it wraps;
  the canvas auto-sizes with margin so lines don't clip.
- **Portrait**: to swap the face, replace `ascii_v2.txt` with new ASCII art of
  the same rough dimensions and regenerate.

## Optional: live GitHub stats

The card can show auto-updating Repos / Commits / Lines-of-Code, refreshed on a
schedule. It's currently **off**. To turn it back on:

1. **Uncomment the stats block** in `generate_svg.py`'s `CONTENT` list:
   ```python
   ("header", "GitHub Stats"),
   ("stat", "Repos", "repo_data"),
   ("stat", "Commits", "commit_data"),
   ("loc", "Lines of Code", None),
   ```
   Regenerate and push. The stat values will show `…` until the Action runs.
2. **Create a token**: GitHub → Settings → Developer settings → Personal access
   tokens → Tokens (classic). Scopes: `repo`, `read:user`. Copy it.
3. **Add the secret**: repo → Settings → Secrets and variables → Actions → New
   repository secret → name `STATS_TOKEN`, value = the token.
4. **Enable + run the workflow**: Actions tab → "Update profile stats" →
   Enable if needed → Run workflow. First run is slow (totals LOC across repos),
   later runs are cached. It re-runs every 12 hours and on push, committing the
   filled-in numbers.

To turn stats **off** again: comment the stats block back out, and Actions tab →
"Update profile stats" → `···` → Disable workflow. (Optionally delete the
`STATS_TOKEN` secret and revoke the token.)

## Want clickable contact links?

Text inside the card image can't be clickable on GitHub. Two ways to get links:
- **Badges below the card** — add a row of `shields.io` badges under the
  `<picture>` block in `README.md`. Functional, but they sit outside the card.
- **On my portfolio site** (`satyamshekhar.vercel.app`) — a webpage isn't
  sandboxed like GitHub, so the SVG's own `<a>` links work there.
