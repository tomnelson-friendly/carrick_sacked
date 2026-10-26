# Has Carrick been sacked?

Checks BBC Sport's RSS feeds every 15 minutes and updates the page.

## Setup (about 10 minutes)

1. Create a new **public** repository on GitHub and upload all these files, keeping the `.github/workflows` folder.
2. **Settings → Pages**: set Source to "Deploy from a branch", branch `main`, folder `/ (root)`. Save.
3. **Actions** tab: enable workflows if asked, open "Check Carrick news" and click **Run workflow** once.
4. Your page is at `https://<your-username>.github.io/<repo-name>/`.

## How it decides

`check.py` reads the BBC feeds and keeps stories mentioning Carrick. It only flips to "Yes" when a headline says it has
happened ("sacked", "United sack", "leaves", "part company") and contains no hedging words ("could", "set to", "?", "fears").
Once it says yes it stays yes. Tweak the `CONFIRMED` and `HEDGES` patterns to change this.
