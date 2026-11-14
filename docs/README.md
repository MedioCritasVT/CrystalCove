# Conflux Portal — GitHub Pages entry point (static website)

This is a **static, read-only portal** originally prepared for Architect review. PR #3 was subsequently merged into `main`; GitHub Pages deployment itself has not been verified in this review. It links to the project’s already published game release, books, source records, Node routing, and platform foundations.

For a clean, first-time Linux/Bazzite experience, use the [first-time setup walkthrough](FIRST_TIME_SETUP.md). It explains both the **game download (no Git required)** and the **optional Git clone/local Portal preview**, without confusing either with hosting the public site.

## Publication boundary

- These files are present on `main` after the merged PR #3. Their presence does **not** establish that GitHub Pages has been enabled or that a service has been deployed; it grants no authority to a Node.
- To publish **after explicit approval**, the repository owner can visit **Settings → Pages**, choose **Deploy from a branch**, and set branch **main** with folder **/docs**. Then visit `https://mediocritasvt.github.io/CrystalCove/` and confirm it renders before describing it as live.
- The repository's top-level `README.md` has a Conflux Portal section after PR #3 was merged.
- The website contains a small read-only soundtrack script that fetches the public GitHub catalog and release metadata to show only genuine MP3 download links. It uses no forms, analytics, authentication, API keys, personal-data collection, agent calls or writable GitHub endpoints. The page still works with static track names when the fetch is unavailable.
- The sanctuary image is requested from the **public main branch** at `raw.githubusercontent.com` and requires network connectivity; the page remains readable if the image is unavailable.
- Outbound links point to the published public repo and existing v0.1 release. When files or releases change, review and update links.
- GitHub Pages is static hosting only. It cannot itself run the Unreal Linux build, Ollama agents, Python services, or VOS.

## Review checklist

1. Verify that the page renders on desktop and mobile and all sections, including the soundtrack, remain keyboard-navigable.
2. Confirm external links and V0.1 Linux-only status; verify that soundtrack download links appear only for actually published GitHub release assets.
3. Check manuscript titles, Book V WIP labeling, authorship notes, and distinction between archived sources and working systems.
4. Confirm that the README placement and eventual Pages URL are acceptable.
5. Only then merge and enable Pages. Verify the live URL before telling visitors it is operational.

**Status: merged source; live GitHub Pages deployment not verified.** The separately running Python Portal application is located under `conflux/portal-app/` and is not deployed by this static website.
