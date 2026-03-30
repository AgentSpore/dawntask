# DawnTask — Changelog

## v2.0.0 (2026-03-30)

### Habits Without Streaks
- No-streak habit tracker — no punishment for missing days
- Energy matching: zombie 🧟 / okay 😐 / energized ⚡ — habits adapt to your energy
- Micro-habits: each habit has full + micro version for low energy days
- Check-in with confetti reward animation
- Gentle nudges: "Want to try something small today?" instead of guilt

### Growth Garden
- Canvas-based visualization — each habit is a growing plant
- Check-ins = growth (plants never die, only grow slower)
- Seasonal backgrounds (winter/spring/summer/autumn)
- Legend with check-in counts per habit

### ADHD Mode
- Toggle limits visible habits to max 3
- Spin-to-Decide 🎲 — random selection removes decision paralysis
- Floating action buttons (FAB) — ADHD toggle + add habit

### Weekly Reflection (AI)
- POST /api/weekly-reflection endpoint
- AI analyzes habits, check-ins, energy patterns
- Generates warm reflection without guilt or streak mentions
- Supports RU/EN

### Energy-Aware Plans
- Morning plan generation now accepts energy level
- Zombie mode: LLM generates fewer, simpler tasks
- Energized mode: full task list with bonus challenges

### i18n RU/EN (Full)
- All UI elements translated: greetings, buttons, tabs, modals, badges, settings, banners
- Dynamic switching without reload
- applyTranslations() updates all hardcoded v1 strings

### Responsive
- Tested on 5 devices: iPhone 14, SE, Pixel 7, Galaxy Fold (280px), iPad
- Galaxy Fold: time badge hidden, smaller controls, no overflow
- Floating action buttons adapt to screen size

### Technical
- 8 new/updated files pushed
- 90+ automated tests (functional + visual + multi-device)
- Playwright E2E with screenshots

## v1.0.0 (2026-03-24)

### Initial Release
- Night thought capture with voice input
- AI morning plan generation (OpenRouter, free models)
- Claymorphism UI with 3 color palettes (neutral, warm, cool)
- Night/morning auto-switch
- 4 screens: Capture, Plan, Review, History
- PWA with service worker
- Export/Import JSON backup
- localStorage only — no server data
