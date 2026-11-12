# CrystalCove public-front-page link audit — 2026-11-12 UTC

**Scope:** GitHub repository front page (`README.md`) and portal HTML source (`docs/index.html`) on the `main` branch. This check examined Markdown `[...](...)` links, HTML `href` and image `src` targets, and internal `#fragment` navigation. This is a source/target audit, **not** a claim that all links were opened successfully in every visitor's browser.

## Audit totals after corrections

| Surface | Link references | Unique targets | Local fragment failures |
| --- | ---: | ---: | ---: |
| `README.md` | 25 | 24 | N/A |
| `docs/index.html` | 28 | 24 | 0 |

## Confirmed problems and corrections

1. **Old portal website URL was premature.** `https://mediocritasvt.github.io/CrystalCove/` was linked from the README even though publication was never verified. GitHub's repository metadata currently reports `has_pages: false`. The README now points to the actual `docs/index.html` source instead; the inaccessible Pages URL is not offered as a working entrance. A site administrator can choose to enable GitHub Pages under Settings → Pages, `main` / `docs`, then verify a live response before reinstating the public-site link.
2. **Harness candidate ZIP was not initially hosted.** PR #11 published documentation but no downloadable archive. The v0.4.1 ZIP has now been uploaded to `conflux/platforms/agent-harness/releases/` on `main`. The Git tree reports 50,924 bytes with blob SHA `4ffbeaeb17b5e7a8a98dfb0752b9d274144eb73a`. This matches the original local Git blob SHA, and the original local SHA-256 is `961929174a824f7d0615c2f0d8f04b53f00f16bc4f7c22fc061783d0492ed832`. The README and portal source now both point to this hosted ZIP.

## Other links examined

- **Game release:** GitHub's official release record for tag `v0.1` contains `Conflux-V0.1-Linux-x86_64.tar.gz`, `Conflux-V0.1-Source.tar.gz`, the release notes, checksums and verification metadata.
- **Project files and book links:** GitHub's contents API finds the README-referenced project index, changelog, books, book V WIP path, mailroom, downloads, platform records, concept art, portal-app and soundtrack catalog.
- **Portal page:** GitHub's contents API finds the book I–IV source manuscripts, book V chapter directory, Architect inbox, realm proposal wave, offline browser study, sanctuary image, and platform directories. The sanctuary image is binary, so its file presence was checked through directory metadata rather than attempting a text read.
- **Same-page navigation:** All six referenced HTML fragment IDs resolve to an element on the current portal source.

## Remaining verification boundaries

- A successful GitHub file listing verifies a target exists on `main`; it does not simulate a human browser downloading a release asset or running the ZIP.
- The separate GitHub Pages site is **not** confirmed live; metadata says Pages is disabled. Publishing source under `docs/` is not itself website deployment.
- The harness remains a **public candidate**: successful packaging checks are not comprehensive Podman/GPU/security acceptance.
- Recheck all public links after renames, release changes and GitHub Pages configuration changes. Do not advertise a new download URL until the corresponding file is present in a release or repository tree.
