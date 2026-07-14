# Setup — animated neofetch profile card

This makes your GitHub profile show an animated terminal card with a live
stats line that refreshes itself every 12 hours.

## What's in here

| File | Purpose |
|------|---------|
| `README.md` | The profile page. Auto-switches dark/light via `<picture>`. |
| `dark_mode.svg` / `light_mode.svg` | The two themed cards. |
| `update_stats.py` | Fetches your GitHub stats and writes them into both SVGs. |
| `.github/workflows/update-stats.yml` | Runs the script on a schedule. |
| `generate_svg.py` + `ascii_v2.txt` | Source used to regenerate the SVGs if you ever edit the content or portrait. Not needed at runtime. |

## Steps

### 1. Create the special repo
Create a **public** repo named exactly **`sshekh30`** (same as your username).
GitHub treats `sshekh30/sshekh30` as your profile repo and renders its README
on your profile page. Tick "Add a README file" so the default branch is `main`.

### 2. Add these files
Upload everything here into that repo, keeping the folder structure — the
workflow must live at `.github/workflows/update-stats.yml`. (Drag-and-drop in
the GitHub web UI works, or push with git.)

### 3. Create a Personal Access Token (PAT)
The built-in Actions token can't read your contribution/LOC data, so you need a
classic PAT:

1. GitHub → **Settings → Developer settings → Personal access tokens →
   Tokens (classic) → Generate new token (classic)**.
2. Scopes: check **`repo`** and **`read:user`**.
3. Generate and copy the token (you'll only see it once).

### 4. Add the token as a repo secret
In the `sshekh30/sshekh30` repo → **Settings → Secrets and variables →
Actions → New repository secret**:
- Name: **`STATS_TOKEN`**
- Value: the PAT you just copied

### 5. Run it once
Go to the repo's **Actions** tab → **Update profile stats** → **Run workflow**.
The first run walks every repo to total your lines of code, so it can take a
few minutes; later runs are fast because results are cached in `cache/`.

When it finishes it commits the filled-in numbers, and your profile card goes
live. It re-runs automatically every 12 hours (and on every push).

## Editing the content later

The card text is baked into the SVGs. To change a line, the portrait, colors,
or wrapping, edit `generate_svg.py`, then locally run:

```bash
python generate_svg.py          # rewrites dark_mode.svg + light_mode.svg
python update_stats.py          # (optional) re-fills the stats, needs GH_TOKEN + LOGIN
```

then commit the updated SVGs. The stats IDs (`repo_data`, `commit_data`,
`loc_data`, `loc_add_data`, `loc_del_data`) must stay intact so the Action can
keep updating them.

## Notes

- **Dark/light** follows each viewer's GitHub theme automatically.
- **Width**: the card is ~930px wide because of the longer lines (Experience,
  Stack.Data, Packages). GitHub scales it down to fit the page — if you ever
  want the text larger, shortening those lines in `generate_svg.py` is the lever.
- **Animation**: the typing cascade + blinking cursor play when the image loads.
  GitHub caches the SVG, so a hard refresh may be needed to see it replay.
