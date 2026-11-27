# Discovery index — opt-in local prototype

This independent, standard-library Python/SQLite module is a first foundation for a possible Discovery room in the local Portal. It indexes file names, relative locations, byte sizes and modification times within explicitly selected project roots. No accounts, AI models, services or dependencies are required. It is not a public website feature.

## Try it with a disposable project

From `conflux/portal-app`, on Linux with Python 3.10+:

```bash
python3 discovery_index.py scan --project "Example" --root /absolute/path/to/test-project
python3 discovery_index.py projects
python3 discovery_index.py search "blend" --project "Example"
python3 discovery_index.py search --limit 20
python3 discovery_index.py forget --project "Example"
python3 -m unittest test_discovery_index.py -v
```

Choose a small disposable project for the first scan. The root must already exist. A scan is a snapshot, not a live watcher; repeat the scan to refresh it. Unavailable or over-limit scans fail without replacing the previous successful snapshot. Search results may be stale; do not infer the current existence, approval, or version of a file from its presence in the index.

## Storage and boundaries

Default database: `${XDG_STATE_HOME:-$HOME/.local/state}/conflux-portal/discovery/index.sqlite3`. Its dedicated directory and database require user-only permissions. The source tree and project files are not moved, edited, uploaded, opened for content extraction, or executed. No automatic scanning or launcher/startup change. The original CLI foundation remains usable; the local Portal provides authenticated endpoints for the same operations. Keep the database, outputs and registered paths private; never commit them to a public repository. The commands print potentially private paths locally.

The scanner skips hidden entries, node_modules, __pycache__, symlinks, special files and entries on a different filesystem. It does not identify every possible sensitive non-hidden filename; select roots carefully. A root must not be the home directory, an ancestor of it, the filesystem root or an ancestor/descendant of the index directory. Limits: 20,000 encountered entries, 24 directory levels, 200 search results. Names and metadata only; case-insensitive search uses SQLite's built-in lowercase behavior (not complete Unicode case folding). No content search, automatic classification, change history or provenance receipts are claimed. Explicit desktop handoff is described below. SQLite schema v2 supports additive migration from v1; other incompatible databases are refused. Forget removes database records only, not project files; it is not forensic secure deletion.

A project root is identified by its selected canonical path. Do not scan during active rearrangement; the filesystem is not a transactional snapshot. A renamed or unavailable root requires an explicit new registration after forgetting the old one. The index is rebuildable.

## Integration boundary

The Portal room exposes explicit root selection, refresh, search, last-scan status and forget using the Portal's loopback/Host/origin/token controls. Local acceptance is still required. It must not expose private locations through public or remotely accessible routes, start background services by default, accept arbitrary command execution, or couple its database to the existing Ledger or harness databases. No authority to classify files as approved is inferred from discovery. Local runtime acceptance is separate from CI.

## Local Portal room

The local Portal now includes Discovery under Create. Open it at the existing 127.0.0.1 address. Choose a folder using the native KDE/GTK picker (or enter its absolute path), name the project, and explicitly register and scan. Search by filename or project, refresh registered roots, and forget index records only. The room never scans on startup; opening an empty room does not create an index. The browser uses authenticated same-origin JSON POST requests, exact loopback Host and peer checks, and text-only rendering of filenames. No file-content routes, shell execution, remote website integration, or new services. Concurrent discovery requests are rejected while an operation is busy. Browser UI and actual native picker require a local acceptance trial; CI uses disposable folders and a mocked picker. 

## Bounded navigation and desktop handoff

Projects are collapsed by default after initial registration, and registration can be folded away. Browse folder branches and breadcrumbs derived from the existing index (empty directories are included after a schema 2 refresh). Search and folder pages return at most 25 entries; the result pane scrolls independently. No destructive database migration. Open sends an explicitly selected indexed, currently regular, non-executable file of a supported suffix to xdg-open; Reveal opens its containing directory. No arbitrary executable or user-supplied command, no browser file serving. Desktop associations are user-configured and may be missing or unsafe for untrusted documents. Only open trusted files; avoid active filesystem rearrangement during handoff. Actual application start is not verified by the request. Native desktop verification remains necessary; automated tests mock the opener. APKs, scripts and unsupported formats are reveal-only.

## Folder topology (schema 2)

The sidebar maps directories only, with lazy 25-branch pages, terminal-folder diamonds, endpoint totals and maximum depth (root = 0). A terminal folder has no traversed child folders; a root-only project has one endpoint. Folder count excludes the root. Empty traversed folders are included on a successful refresh; hidden paths, excluded dependencies, symlinks and other filesystems remain outside the map. Existing schema 1 data is migrated transactionally by adding a directory table; projects and file snapshots remain intact. Until each project is refreshed, its directory topology is inferred from its existing file paths and marked as such. No re-registration is needed. Refresh failures preserve existing directory and file snapshots. No automatic launch scan is included in this change.

The explorer-style sidebar uses a shared scroll region, separate expansion arrows and folder selection, themed folder glyphs, connecting rails and a selected row. Project maintenance controls are under Project details. No native KDE icon theme or file manager integration is required. The database and scan behavior are unchanged.
