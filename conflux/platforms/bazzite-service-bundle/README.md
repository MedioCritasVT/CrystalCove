# Conflux Bazzite Media Mirror — first service installer candidate

**State:** source candidate for local testing, not yet accepted on a real Bazzite host. **No server migration. No automatic backups or failover.** This package is independent of the CachyOS website/server design.

This is a deliberate secondary-installation path for **Jellyfin, Kavita and Navidrome** on a Bazzite desktop. It uses the rootless Podman and user-systemd/Quadlet facilities already available on a compatible Bazzite installation. The installer can be launched through the local Conflux Portal's **Media Mirror Setup** room after updating the Portal source checkout.

The workflow is **Check → review ports and plan → explicitly approve → Install new services → confirm the native Bazzite desktop dialog**. The last step may download container images and start newly created units. Do not click it until you have reviewed the installation's effects.

## What this candidate does and does not do

| Does | Does **not** |
| --- | --- |
| Reads Bazzite identity, executable availability, rootless Podman, user systemd, ports and collision destinations | Rebase, layer, or update Bazzite system packages |
| Creates a fresh set of user-local Quadlet files and empty folders, only after approval | Read, overwrite, import, or migrate your CachyOS services, databases, or libraries |
| Starts three localhost-bound media containers on explicit confirmation | Enable Tailscale Serve, advertise to your LAN or expose services to the internet |
| Supplies stop-first configuration/state backup helper and clear ports | Copy or sync media, provide failover, make an off-machine backup, or install Immich |
| Leaves all automatic container image updates disabled | Automatically upgrade containers when Bazzite or the Portal is updated |

**Important:** the source is in a public repository, but the generated local service configuration and user data must stay on the host. Do not commit service databases, credentials, backups, private Tailnet DNS names, private media, or local reports.

## Exactly which services and ports?

| Service | Container image used by first candidate | Local browser URL (host-side) | OPTIONAL Tailscale HTTPS listener |
| --- | --- | --- | --- |
| Jellyfin | `docker.io/jellyfin/jellyfin:latest` | `http://127.0.0.1:8096` | `8443` |
| Kavita | `ghcr.io/kareadita/kavita:latest` | `http://127.0.0.1:5000` | `8444` |
| Navidrome | `docker.io/navidrome/navidrome:latest` | `http://127.0.0.1:4533` | `8445` |

**These image tags are mutable.** Review the pulled versions and upstream release notes before trusting this candidate for important data. A subsequent release should pin tested versions/digests. The first installer deliberately does not enable registry autoupdates.

All three Quadlets publish to **127.0.0.1 only**, not `0.0.0.0`, and use user-local storage. Tailscale HTTPS ports in this table are an **optional manual mapping**, not opened by the installer. The local Portal normally occupies `127.0.0.1:8765`; the static public website proposal uses a separate loopback port `8088` on its intended server. Neither port is reassigned.

**Before you test:** if any local port is already in use or if the installer's destination files/directories exist, the preflight should refuse a new installation. This protects prior work and avoids two services fighting over a port.

## Open the one-button installer in the Portal

1. On the **Bazzite desktop itself**, open the existing Conflux Portal's **Updates & Setup** room. In a Git checkout, select **Check for Updates → Update → Relaunch**. The Git updater is not available to a repository ZIP without Git history.
2. Use the direct Bazzite desktop address **`http://127.0.0.1:8765`**. A Portal accessed through a phone's Tailscale URL is for viewing; it cannot use these installation controls.
3. Open **Media Mirror Setup** from the left navigation. Review the service names, localhost ports and optional Tailscale HTTPS ports.
4. Press **Check Bazzite dependencies**. This performs inspection and creates an expiring, single-use plan token only when its checks pass; it does not install.
5. Review every report line. Check the approval box only if a new, empty installation is wanted. Press **Install new services**.
6. Confirm the **native Bazzite desktop dialog** (KDialog or Zenity). Cancelling does not install. If no compatible local dialog is available, the service API refuses to install.
7. Starting a service may pull its container image and create first-run application configuration. Open each localhost URL, complete the application's own admin/password setup, and check its logs and data paths before adding personal media.

This is a **one-action install after inspection and confirmation**, not an unattended deployer. No `sudo` or `rpm-ostree` command is part of the installation.

### Read-only command-line alternative

From the repository root on the Bazzite machine:

```bash
python3 conflux/platforms/bazzite-service-bundle/service_manager.py --check
python3 -m unittest discover -s conflux/platforms/bazzite-service-bundle -p 'test_*.py' -v
```

The CLI only **checks**. Installation is intentionally restricted to the local Portal approval flow with a native desktop confirmation, rather than an unsigned shell script that can be run accidentally.

## Directory layout — intentionally new and separate

The installer creates only under the Bazzite user's home directory:

```text
~/.config/containers/systemd/
  conflux-media-jellyfin.container
  conflux-media-kavita.container
  conflux-media-navidrome.container

~/.local/share/conflux-media-mirror/
  state/
    jellyfin/config/
    jellyfin/cache/
    kavita/config/
    navidrome/data/
  media/
    video/
    books/
    comics/
    manga/
    music/
```

Media folders are **empty** at installation. Media mounts are read-only **inside the containers**, while the new state/configuration mounts are writable by the services. The application files may contain sensitive credentials. Protect access to them.

This is **not** a replica of CachyOS yet. To obtain redundant access to a media collection, you would still need a separately designed, verified transfer or synchronization plan, chosen media sources, and independent backup/restore tests. Never blindly map a production media folder or run destructive `rsync --delete` commands.

## First-run guide: adding media to the new containers

**You do not copy files *into* a container.** The Bazzite installer already binds new host folders to fixed paths *inside* each app. The folders start **empty**. Open them with Dolphin and copy a small sample there, then choose the container-side path in the application's library settings.

### One folder, two names

These are the **exact paths for this Conflux Bazzite candidate**, not general paths for every Jellyfin/Kavita/Navidrome installation.

| Application | Folder on Bazzite (Dolphin) | Path to choose inside app |
| --- | --- | --- |
| Jellyfin | `~/.local/share/conflux-media-mirror/media/video/` | `/media` |
| Jellyfin movies (optional subfolder) | `~/.local/share/conflux-media-mirror/media/video/Movies/` | `/media/Movies` |
| Jellyfin shows (optional subfolder) | `~/.local/share/conflux-media-mirror/media/video/Shows/` | `/media/Shows` |
| Navidrome | `~/.local/share/conflux-media-mirror/media/music/` | `/music` |
| Kavita books | `~/.local/share/conflux-media-mirror/media/books/` | `/books` |
| Kavita comics | `~/.local/share/conflux-media-mirror/media/comics/` | `/comics` |
| Kavita manga | `~/.local/share/conflux-media-mirror/media/manga/` | `/manga` |

**Try a small copy first:**

1. On Bazzite, open **Dolphin** and press **Ctrl+L**. Paste the appropriate Bazzite path from the table. The folder is under hidden `.local`; entering the full path avoids needing to reveal hidden folders.
2. Copy (do not move) one movie, one album, or one supported ebook/comic into the corresponding host folder. For separate movies and series, make `Movies` and `Shows` subfolders under `media/video`. Do not overwrite files with the same name without checking.
3. In **Jellyfin**, open `http://127.0.0.1:8096/web/`. During the wizard, choose **Add Media Library**, then browse or type `/media/Movies` (movies) or `/media/Shows` (shows). Once setup is complete, libraries can also be managed via **Admin → Dashboard → Libraries**.
4. In **Navidrome**, open `http://127.0.0.1:4533`. Its container's music folder is `/music`. Wait for the music scan or use its library scan controls. It must have read access to those files.
5. In **Kavita**, open `http://127.0.0.1:5000`, go to the admin **Libraries** settings and choose **Add Library**. Pick the correct library type and container directory (`/books`, `/comics` or `/manga`). In the folder picker, check the filesystem root `/` if the mount doesn't immediately appear.
6. Once a sample works, add more content. The container-side media mounts are **read-only**, protecting originals from app writes; the app state/database mounts remain writable.

**Permissions:** if a copied file doesn't appear, first confirm it exists under the correct Bazzite folder and is readable by the Bazzite user. Do not run `chmod -R 777`, `sudo chown -R`, or delete your service state to experiment with permissions. Some external drives and network mounts need their own carefully reviewed mapping.

### Jellyfin: wizard interrupted after creating an account

Creating an admin user does **not** finish Jellyfin's initial wizard. If you refreshed after creating the user, the server may be healthy even if the browser is at an unexpected screen.

1. Return to `http://127.0.0.1:8096/web/` on Bazzite, without going through the Portal or Tailscale.
2. Try **Ctrl+Shift+R**. If it offers login, try the administrator credentials you created; if the wizard resumes, proceed. The media-library step is optional and can be completed later.
3. Try the address in a **Firefox private window** to distinguish a stale browser session from server-side setup.
4. If it remains blocked, inspect status and logs **without resetting the service**:

   ```bash
   systemctl --user status conflux-media-jellyfin.service --no-pager
   journalctl --user -u conflux-media-jellyfin.service -n 60 --no-pager
   ```

5. Record the **exact screen or error text** and the relevant log messages, with passwords, authentication tokens, IPs and other private details removed. Do not erase `state/jellyfin/config`, edit its database, recreate the admin account, or change container images before understanding the cause.

Jellyfin's [official setup wizard](https://jellyfin.org/docs/general/post-install/setup-wizard/) and [library paths](https://jellyfin.org/docs/general/server/libraries/) explain the app-side steps. Navidrome's [Docker mount documentation](https://navidrome.org/docs/installation/docker/) and Kavita's [library guidance](https://wiki.kavitareader.com/guides/admin-settings/libraries/index.html) explain their container-side path selection.

**Backup reminder:** copying files into the new Bazzite media folders does not make them redundant unless another independent, restorable copy exists. The included `backup.py` saves the new services' **state/configuration**, not these media folders. Plan a separate media-file backup and test its restoration.

## Manage services on the Bazzite desktop

After a successful installation:

```bash
systemctl --user status conflux-media-jellyfin.service
systemctl --user status conflux-media-kavita.service
systemctl --user status conflux-media-navidrome.service

journalctl --user -u conflux-media-jellyfin.service -n 80 --no-pager
journalctl --user -u conflux-media-kavita.service -n 80 --no-pager
journalctl --user -u conflux-media-navidrome.service -n 80 --no-pager
```

To stop the new services before maintenance or a consistent backup:

```bash
systemctl --user stop conflux-media-jellyfin.service conflux-media-kavita.service conflux-media-navidrome.service
```

To start those same units again:

```bash
systemctl --user start conflux-media-jellyfin.service conflux-media-kavita.service conflux-media-navidrome.service
```

Bazzite's user Quadlet documentation explains systemd user units and optional login persistence. **Do not enable user lingering** or modify startup policy without deciding whether background services should continue when you log out. The generated Quadlets include `WantedBy=default.target` and may start in later user sessions. A present Quadlet file is not proof that its container is healthy.

## Private Tailscale viewing (manual; never part of Install)

First establish that each service works locally and has its initial account/security setup completed. Then check that the proposed Tailscale HTTPS listener ports are not already assigned and that your tailnet's HTTPS and access policies are appropriate.

**Examples for review**, not commands launched by the installer:

```bash
tailscale serve --bg --https=8443 8096    # Jellyfin localhost 8096
tailscale serve --bg --https=8444 5000    # Kavita localhost 5000
tailscale serve --bg --https=8445 4533    # Navidrome localhost 4533
tailscale serve status
```

Use the *actual* HTTPS address returned by Tailscale. On another authorized tailnet device, a resulting address may resemble:

```text
https://YOUR-BAZZITE-DEVICE.YOUR-TAILNET.ts.net:8443  (Jellyfin)
https://YOUR-BAZZITE-DEVICE.YOUR-TAILNET.ts.net:8444  (Kavita)
https://YOUR-BAZZITE-DEVICE.YOUR-TAILNET.ts.net:8445  (Navidrome)
```

These hostnames are placeholders, **not** your personal Tailnet details. Tailscale Serve is tailnet-limited; **Tailscale Funnel would instead create public exposure** and is deliberately excluded. Serve uses your existing tailnet HTTPS and access control rules. Adding Serve mappings changes your Tailscale configuration, so review `tailscale serve status` first and do not overwrite existing Portal routes. See the [official Serve reference](https://tailscale.com/docs/reference/tailscale-cli/serve).

### A backup is not the same as redundancy

A second service instance without your media, metadata, or a restore procedure is not a backup. This installer intentionally does not claim otherwise.

The included `backup.py` can create a **stop-first local archive of the new mirror's state/configuration only**. It does **not** include the `media/` folders, the CachyOS server's data, the Portal's browser-local Ledger or Atelier content, or Tailscale settings.

**Recommended minimum sequence:**

1. Log out of all three newly installed apps, and stop their user services using the command above.
2. Choose a private backup destination *outside* the mirror root, preferably an independent disk, e.g. a mounted backup drive. Avoid using a publicly synchronized folder.
3. Run:

```bash
python3 conflux/platforms/bazzite-service-bundle/backup.py --destination "$HOME/Backups/Conflux-media-mirror"
```

4. The helper creates a `.tar.gz` and adjacent SHA-256 file with user-only permissions and refuses symlinks in the state tree. It will not overwrite an existing archive.
5. Verify the archive and checksum yourself (`sha256sum -c <archive>.tar.gz.sha256`) and keep another copy on a separate physical device or trusted backup destination. Start the services again when ready.
6. Independently back up the actual **media files** you choose to supply. Merely mounting a live remote disk is not an independent backup.

**Restore rehearsal:** on a test host, stop services, verify the SHA-256 checksum, inspect the archive listing, and restore into an **empty, separately designated mirror**. Do not extract over running or existing production data. Validate the app versions and successful library/database startup before considering any recovery complete. Automated restore and server-to-server replication are intentionally not shipped.

## What about Immich and SearXNG?

- **Immich:** not installed by this package. Its official deployment has multiple coordinated services and a database. Photo/video library and PostgreSQL state require a version-matched backup/restore plan. Do not treat one generic container as a safe backup of Immich.
- **SearXNG:** not installed yet. The private search service and its configuration, upstream updates and Tailscale access need a separate opt-in review.

The CachyOS service inventory and source deployment remain a distinct, paused effort; the Bazzite mirror must never silently attach to or overwrite the server's production state.

## Updates: three different mechanisms

| Operation | What it changes | Does it update these services? |
| --- | --- | --- |
| Bazzite desktop / OS update | The host OS image and installed system components | **No automatic container image update guaranteed.** It may change Podman itself; inspect compatibility afterward. |
| Portal Updates & Setup | A clean CrystalCove Git checkout and the local Portal code | **No.** This updates the installer source/UI, not installed service containers, state, or databases. |
| Container update | The actual Jellyfin/Kavita/Navidrome images and potentially their app databases | **Separate, controlled operation.** Stop and back up service state; review target versions and release notes, pull/apply only with approval, then test restoration and service startup. |

No automatic `podman auto-update` is enabled. The moving `:latest` tags are not a substitute for a tested upgrade procedure.

## Troubleshooting and safety boundaries

- **Not on Bazzite:** the checker refuses to approve this stack. Use the distinct CachyOS project instead.
- **No native confirmation dialog:** install is blocked; install or configure `kdialog`/`zenity` only after reviewing the host environment. No privilege escalation is attempted by the Portal.
- **Existing service, directory or occupied port:** the checker blocks installation, and exclusive file creation prevents overwriting Quadlets. Do not delete existing service data just to make the check pass.
- **Rootless Podman / user systemd unavailable:** inspect `podman info` and `systemctl --user` on the Bazzite desktop. Do not run the installer as root.
- **Partial image pull/service startup failure:** the newly written Quadlet files may remain, but no existing services are replaced. Review `journalctl --user` output and image/permissions before changing anything. A failed startup is not a rollback of downloaded images.
- **Phone can view the Portal but not install:** intended. Use the Bazzite desktop's `http://127.0.0.1:8765`.
- **Storage/SELinux:** rootless Podman with `:Z` writable state and `:ro,z` readonly media mounts may behave differently depending on host permissions and media filesystems. Verify on real Bazzite before adding media.
- **Public site:** the static public Portal and private Sanctum never need the local container installer endpoint. Do not reverse-proxy this desktop management backend to the internet.

## Testing and publishing a GitHub Release

**Repository publication is sufficient to make the installer visible in an up-to-date Git checkout** after using the Portal's explicit updater. You **do not have to publish a GitHub Release** just to test the Portal's new room locally.

A versioned **GitHub Release is recommended only after actual Bazzite acceptance testing**, if you want a standalone downloadable ZIP with a stable version and checksum for people who are not running an updatable Git checkout. Do not call this a supported one-click public installer before verifying a fresh Bazzite desktop, the local native approval, three startup checks, media access, stop-first backup, checksum and restore test, and Tailscale routing. No Release asset is built or uploaded automatically by this source commit.

## References

- [Bazzite Quadlets documentation](https://docs.bazzite.gg/Installing_and_Managing_Software/Quadlet/)
- [Tailscale Serve CLI](https://tailscale.com/docs/reference/tailscale-cli/serve)
- [Kavita container installation reference](https://wiki.kavitareader.com/installation/docker/github/)
- [Conflux local Portal README](../../portal-app/README.md)
- [CachyOS static website proposal](../portal-deployment/README.md)
