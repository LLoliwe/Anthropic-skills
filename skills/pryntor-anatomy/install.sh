#!/usr/bin/env bash
# Install the official Anatomy agent skill into a project for Claude Code and Codex.
# No remote script execution; the requested upstream commit is checked before copying.
set -euo pipefail

PIN="e9488296a44211c42701ff71705b7901470ec78f"
SOURCE="https://github.com/wheresryan22/anatomy.git"
PROJECT="${1:-.}"

command -v git >/dev/null || { echo "Git is required" >&2; exit 2; }
command -v tar >/dev/null || { echo "tar is required" >&2; exit 2; }
PROJECT="$(cd "$PROJECT" && pwd)"
for folder in "$PROJECT/.agents/skills/anatomy" "$PROJECT/.claude/skills/anatomy"; do
  if [ -e "$folder" ] || [ -L "$folder" ]; then
    echo "REFUSING to overwrite existing $folder; inspect/backup it first" >&2
    exit 3
  fi
done

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
git clone --quiet --no-checkout "$SOURCE" "$scratch/source"
git -C "$scratch/source" checkout --quiet --detach "$PIN"
actual="$(git -C "$scratch/source" rev-parse HEAD)"
[ "$actual" = "$PIN" ] || { echo "Upstream SHA mismatch" >&2; exit 4; }
test -s "$scratch/source/SKILL.md"
test -s "$scratch/source/LICENSE"
test -s "$scratch/source/kit/iso-kit.mjs"
test -s "$scratch/source/examples/dial-indicator/build.mjs"
# Stage both installations completely before exposing them.
mkdir -p "$scratch/staged/claude" "$scratch/staged/codex"
for target in claude codex; do
  tar -C "$scratch/source" --exclude='.git' -cf - . | tar -C "$scratch/staged/$target" -xf -
  printf '%s\n' "$PIN" > "$scratch/staged/$target/PRYNTOR_UPSTREAM_SHA"
done
mkdir -p "$PROJECT/.agents/skills" "$PROJECT/.claude/skills"
mv "$scratch/staged/codex" "$PROJECT/.agents/skills/anatomy"
mv "$scratch/staged/claude" "$PROJECT/.claude/skills/anatomy"
test "$(cat "$PROJECT/.agents/skills/anatomy/PRYNTOR_UPSTREAM_SHA")" = "$PIN"
test "$(cat "$PROJECT/.claude/skills/anatomy/PRYNTOR_UPSTREAM_SHA")" = "$PIN"
echo "INSTALLED Anatomy $PIN into both project-local agent skill folders"
