#!/usr/bin/env bash
# Explicit opt-in upload. Requires an original screen recording.
# Does not alter game installs, overwrite assets, or push commits.
set -euo pipefail
if [[ $# -lt 1 || ! -f "$1" ]]; then
  echo 'Usage: bash conflux/video-tour/publish_from_recording.sh "/path/to/2026-11-14 02-38-32.mp4"' >&2
  exit 2
fi
for command_name in gh ffmpeg ffprobe; do
  command -v "$command_name" >/dev/null || { echo "Missing command: $command_name" >&2; exit 2; }
done
source_video="$(realpath "$1")"
work="$HOME/Conflux/SourceFiles/Videos/PortalTour"
if [[ -n "$(printenv CONFLUX_TOUR_OUTPUT_DIR || true)" ]]; then work="$CONFLUX_TOUR_OUTPUT_DIR"; fi
mkdir -p "$work"
repo='MedioCritasVT/CrystalCove'
tag='conflux-portal-tour-v0.1'
printf 'Source: %s\nOutput: %s\n' "$source_video" "$work"
printf 'Creates four 720p excerpts without modifying Portal or game installs.\n'
# Refuse silent replacement on subsequent runs.
if compgen -G "$work/*.mp4" >/dev/null; then
  echo "Existing clips found in $work. Review or move them before regenerating." >&2
  exit 2
fi
create_clip() {
  local file="$1" start="$2" length="$3"
  ffmpeg -nostdin -hide_banner -loglevel error -n \
    -ss "$start" -i "$source_video" -t "$length" \
    -vf 'scale=1280:-2,fps=30' -c:v libx264 -preset veryfast -crf 28 \
    -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart \
    "$work/$file"
}
create_clip 01-threshold-welcome.mp4 7 13
create_clip 02-ledger-workspace.mp4 29 13
create_clip 03-game-first-launch.mp4 40 16
create_clip 04-node-companions.mp4 67 11
( cd "$work" && sha256sum ./*.mp4 > VIDEO_SHA256SUMS.txt )
echo
echo "Review all four clips locally for visuals, audio, and private information."
gh auth status >/dev/null
read -r -p "Publish these four clips publicly to GitHub Releases? [y/N] " answer
if [[ "$answer" != [yY] && "$answer" != [yY][eE][sS] ]]; then
  echo "Clips remain local; nothing published."
  exit 0
fi
if gh release view "$tag" --repo "$repo" >/dev/null 2>&1; then
  gh release upload "$tag" "$work/"*.mp4 --repo "$repo"
else
  gh release create "$tag" "$work/"*.mp4 \
    --repo "$repo" --target main \
    --title 'Conflux Portal · Four Short Tour Clips' \
    --notes 'Four excerpts from the original Conflux Portal screen recording: Threshold, Ledger, first game launch, and the Node familiars. Preview footage, not a finished-game guarantee.'
fi
echo "Published release:"
gh release view "$tag" --repo "$repo" --web
