# CHANGELOG
## 2026-11-15 — Milestone 1
### Added
- Expo SDK 57 app in `apps/mobile` with 19 screens, design tokens (warm white, forest green), six-class badge system with icon+label, demo mock API, Zustand stores, TanStack Query hooks.
- Jest + RNTL tests (19), ESLint (expo config), strict TypeScript.
### Fixed during build
- Route conflict between splash and home tab (home is now `/home`).
- `Card` background override bug that hid the amber incomplete-list warning.
- Tab bar label clipping; input placeholder contrast (3.07 → 4.97:1).
- Components defined during render hoisted (lint).
## 2026-11-15 — Milestone 0
- Docs 01–11 and status files.
