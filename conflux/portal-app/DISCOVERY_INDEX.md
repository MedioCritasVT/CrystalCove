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

Default database: `${XDG_STATE_HOME:-$HOME/.local/state}/conflux-portal/discovery/index.sqlite3`. Its dedicated directory and database require user-only permissions. The source tree and project files are not moved, edited, uploaded, opened for content extraction, or executed. No automatic scanning or launcher/startup change. No web endpoint exists in this first version. Keep the database, outputs and registered paths private; never commit them to a public repository. The commands print potentially private paths locally.

The scanner skips hidden entries, node_modules, __pycache__, symlinks, special files and entries on a different filesystem. It does not identify every possible sensitive non-hidden filename; select roots carefully. A root must not be the home directory, an ancestor of it, the filesystem root or an ancestor/descendant of the index directory. Limits: 20,000 encountered entries, 24 directory levels, 200 search results. Names and metadata only; case-insensitive search uses SQLite's built-in lowercase behavior (not complete Unicode case folding). No content search, automatic classification, change history, provenance receipts or file launching is claimed. SQLite schema v1; incompatible databases are refused. Forget removes database records only, not project files; it is not forensic secure deletion.

A project root is identified by its selected canonical path. Do not scan during active rearrangement; the filesystem is not a transactional snapshot. A renamed or unavailable root requires an explicit new registration after forgetting the old one. The index is rebuildable.

## Integration boundary

Portal integration is intentionally deferred until module tests and a disposable local trial pass. A future room can expose explicit root selection, refresh, search, last-scan status and forget using the Portal's loopback/Host/origin/token controls. It must not expose private locations through public or remotely accessible routes, start background services by default, accept arbitrary command execution, or couple its database to the existing Ledger or harness databases. No authority to classify files as approved is inferred from discovery. Local runtime acceptance is separate from CI.
