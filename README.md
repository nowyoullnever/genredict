# RYM Atlas

Unofficial visualization of Rate Your Music taxonomy data. This project is not affiliated with Rate Your Music.

RYM Atlas is a static, GitHub Pages-compatible explorer for genres, subgenres, descriptors, and Scenes & Movements. It preserves the source taxonomy as a directed graph, including nodes with multiple parents.

## Features

- Graph, Tree, Metro, and A–Z Dictionary browsing modes
- Fuzzy global search (`/` focuses search), deep links (`?genre=<id>&mode=<mode>`), and browser history
- Shared inspector with parent/child relationships and safe RYM links where a deterministic ASCII slug is available
- Type and multiple-parent filters, mobile bottom-sheet inspector, keyboard escape handling
- Static JSON data generated from `FlakyBlueJay/mb-rym-hierarchy`; no runtime RYM scraping

## Architecture

`external hierarchy → scripts/refresh_data.py → public/data/*.json → Vite React frontend`

The parser normalizes indentation into directed parent edges, merges identical typed names, uses deterministic collision IDs, and validates nonempty names, IDs, edge targets, duplicated edges, and a minimum node threshold before replacing generated data.

## Development

```bash
npm install
npm run dev
npm run build
python scripts/refresh_data.py
python scripts/validate_data.py
```

## Automation and deployment

`.github/workflows/update-data.yml` runs at minute 17 every six hours and on manual dispatch. It fetches, hashes, parses, diffs, validates, then commits changed generated data only after successful validation. `.github/workflows/deploy.yml` builds the static site and deploys it through GitHub Pages.

Enable **Settings → Pages → Build and deployment → GitHub Actions** once for the repository. The deployment URL will be `https://nowyoullnever.github.io/genredict/`.

## Source and limitations

Source: [FlakyBlueJay/mb-rym-hierarchy](https://github.com/FlakyBlueJay/mb-rym-hierarchy), `RateYourMusic Hierarchy.txt`. The upstream text does not encode all possible RYM metadata, aliases, or canonical URLs, so the atlas only generates an RYM link when conversion is conservative.