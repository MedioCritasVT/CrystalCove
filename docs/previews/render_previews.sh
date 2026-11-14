#!/usr/bin/env bash
# Generate small animated README previews from the Architect's four PUBLIC
# GitHub Release MP4s. No private files, autoplay, or extra Git downloads.
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
cd "$root"
mkdir -p docs/previews
source_dir="$(mktemp -d)"
trap 'rm -rf "$source_dir"' EXIT
release="https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-portal-tour-v0.1"

render() {
  local filename="$1" result="$2" expected="$3" start="$4" length="$5"
  curl --fail --location --silent --show-error --retry 3 --retry-all-errors \
    "$release/$filename" -o "$source_dir/$filename"
  local actual
  actual="$(sha256sum "$source_dir/$filename" | cut -d' ' -f1)"
  if [[ "$actual" != "$expected" ]]; then
    echo "Wrong asset hash for $filename; aborting." >&2
    exit 1
  fi
  # Single-pass in-memory palette optimization. Loop forever, seven frames
  # per second, 560-pixel width. Keep READMEs light and accessible.
  ffmpeg -hide_banner -loglevel error -nostdin -y -ss "$start" \
    -i "$source_dir/$filename" -t "$length" \
    -filter_complex 'fps=7,scale=560:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=48:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4' \
    -loop 0 "docs/previews/$result"
  echo "$result: $(wc -c < "docs/previews/$result") bytes"
}
render 01-threshold-welcome.mp4 01-threshold-preview.gif \
  d08efb4e6df209f1f16064ad2c13790549df762a84a264281dcaa7039ad5e20d 1 4
render 02-ledger-workspace.mp4 02-creative-workspace-preview.gif \
  d03f317d368074ac502e0757c76560f50927a7b8a270e5db1bcd42115837bb45 1 4
render 03-game-first-launch.mp4 03-gameplay-preview.gif \
  d4d0727d1162230683b7036c35a9e46698542258cf305cc295dcda3228f858fe 4 4
render 04-node-companions.mp4 04-library-music-preview.gif \
  163e1a326e4f70644344387769e9101cdeaa5849e19e72a2b0891d166562f2b9 1 4

python3 docs/previews/capture_nodes.py
echo "Ready: four small GIF previews and a real Node Companions screenshot."
