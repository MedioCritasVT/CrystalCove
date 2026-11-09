# Conflux V0.1 — Linux preview

**Published Linux preview · V0.1 · 2026-11-09**

The current native game compiled, cooked, staged and packaged successfully using Unreal Engine 5.8.4. This is an early Linux x86_64 Development preview, not final art or campaign acceptance.

## Downloads

Download from [GitHub Release v0.1](https://github.com/MedioCritasVT/CrystalCove/releases/tag/v0.1). All five uploaded files match local SHA-256 fingerprints. Release assets:

- `Conflux-V0.1-Linux-x86_64.tar.gz` — standalone game, 1,177,106,741 bytes. Extract and run `PlayConflux.sh`; no editor required.
- `Conflux-V0.1-Source.tar.gz` — packaging source project/inputs, 583,604,356 bytes. Requires a separately installed Unreal Engine 5.8.4 to rebuild. Full engine and upstream Blender authoring archives excluded.
- `SHA256SUMS` and `VERIFICATION.json` — integrity and bounded test results.

See [BUILD.json](BUILD.json) for fingerprints and actual test limits. The game source snapshot is local and shipped as a separate source-input archive; a coordination commit must not be described as its original Git commit.

## Start and save

Use Begin a new journey for local play. No account service is required. WASD moves, right-drag orbits, wheel zooms, E interacts, Shift hover-sprints. Use Menu/Escape to save/load. Default runtime data: `~/.local/share/Conflux/V0.1` (or XDG_DATA_HOME). The launcher supports `CONFLUX_USER_DIR` override and isolates data from the working developer project.

Journey saves remain manual. Settings, personal photo pages and app workspaces retain their own persistence. Owner profiles, notes, saves and screenshots were not shipped.

## Evidence

Standalone title and native city/HUD rendered from a relocated package. A valid disposable Starter fixture saved a named journey and photo, exited normally, and appeared on a fresh title launch without altering save bytes. This used offscreen rendering; no physical desktop input was automated. Earlier fallback-profile/dialog-state test failures are retained locally. Entire campaign, all character/realm/interior combinations, fresh-profile mouse flow and other machines were not certified.

The launcher preserves current fitted-Node and Medio Ready selection flags. Articulation01 remains an isolated candidate. Documentation-only Gate III/DLC direction was not newly implemented in this package. The authoritative working project and source inputs were preserved.

Use the attached `Conflux-V0.1-Source.tar.gz` for native Unreal project inputs. GitHub’s automatically generated “Source code” archives describe this coordination/browser repository at the tag, not the separate native project snapshot.
