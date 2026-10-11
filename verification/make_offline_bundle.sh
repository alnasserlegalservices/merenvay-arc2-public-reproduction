#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$REPO_ROOT/dist"
WORK="$DIST/offline-build"
BUNDLE="$DIST/merenvay-arc2-offline-bundle.tar.gz"
UPSTREAM_COMMIT="d117c699416692cac7ceb951b09f2cdb484a89a6"

rm -rf "$WORK"
mkdir -p "$WORK/package/runtime" "$WORK/package/app/Mentova/src/mentova/games" "$WORK/upstream" "$DIST"

"$REPO_ROOT/verification/build_portable_swi_bundle.sh" \
  "$WORK/package/runtime/swi-portable" \
  "$DIST/swi-prolog-portable.tar.gz"

# Build-time checkout only. The final runtime bundle does not include the corpus,
# Git history, reports, task walkthroughs, or other unnecessary upstream files.
git clone --quiet https://github.com/ai-university-aiu/Mentova.git "$WORK/upstream/Mentova"
git -C "$WORK/upstream/Mentova" checkout --quiet "$UPSTREAM_COMMIT"
git -C "$WORK/upstream/Mentova" apply "$REPO_ROOT/merenvay_dispatch_fix.patch"

cp "$WORK/upstream/Mentova/src/mentova/games/arc_benchmark_2.pl" \
   "$WORK/package/app/Mentova/src/mentova/games/arc_benchmark_2.pl"
cp "$WORK/upstream/Mentova/LICENSE" "$WORK/package/app/Mentova/LICENSE"
cp "$WORK/upstream/Mentova/LICENSE.txt" "$WORK/package/app/Mentova/LICENSE.txt"

cp "$REPO_ROOT/verification/challenges_to_prolog.py" "$WORK/package/app/"
cp "$REPO_ROOT/verification/build_submission.py" "$WORK/package/app/"
cp "$REPO_ROOT/verification/predict_unseen.pl" "$WORK/package/app/"
cp "$REPO_ROOT/verification/kaggle_entry.py" "$WORK/package/app/"
cp "$REPO_ROOT/verification/OFFLINE_BUNDLE_README.md" "$WORK/package/"

cat > "$WORK/package/manifest.json" <<EOF
{
  "bundle": "MERENVAY ARC-AGI-2 offline verification candidate",
  "upstream": "ai-university-aiu/Mentova",
  "upstream_commit": "$UPSTREAM_COMMIT",
  "runtime_scope": "patched arc_benchmark_2.pl only; no ARC public task/solution corpus bundled",
  "claim_boundary": "tooling/runtime package only; not ARC Prize Verified; not hidden-set performance"
}
EOF

# Fail closed if public benchmark corpus/solution files leak into the runtime package.
if find "$WORK/package" -type f \( -name 'arc_tasks_2.pl' -o -iname '*solutions*.json' -o -path '*/data/arc_agi_2/*' \) | grep -q .; then
  echo "Forbidden ARC corpus/solution material found in runtime bundle" >&2
  find "$WORK/package" -type f \( -name 'arc_tasks_2.pl' -o -iname '*solutions*.json' -o -path '*/data/arc_agi_2/*' \) >&2
  exit 10
fi

TMP_SUMS="$WORK/SHA256SUMS.tmp"
( cd "$WORK/package" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum ) > "$TMP_SUMS"
mv "$TMP_SUMS" "$WORK/package/SHA256SUMS"
tar -C "$WORK" -czf "$BUNDLE" package
sha256sum "$BUNDLE" > "$BUNDLE.sha256"
echo "Built $BUNDLE"
