#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$REPO_ROOT/dist"
WORK="$DIST/offline-build"
BUNDLE="$DIST/merenvay-arc2-offline-bundle.tar.gz"
UPSTREAM_COMMIT="d117c699416692cac7ceb951b09f2cdb484a89a6"

rm -rf "$WORK"
mkdir -p "$WORK/package/runtime" "$WORK/package/app" "$DIST"

"$REPO_ROOT/verification/build_portable_swi_bundle.sh" \
  "$WORK/package/runtime/swi-portable" \
  "$DIST/swi-prolog-portable.tar.gz"

git clone --quiet https://github.com/ai-university-aiu/Mentova.git "$WORK/package/app/Mentova"
git -C "$WORK/package/app/Mentova" checkout --quiet "$UPSTREAM_COMMIT"
git -C "$WORK/package/app/Mentova" apply "$REPO_ROOT/merenvay_dispatch_fix.patch"

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
  "claim_boundary": "tooling/runtime package only; not ARC Prize Verified; not hidden-set performance"
}
EOF

TMP_SUMS="$WORK/SHA256SUMS.tmp"
( cd "$WORK/package" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum ) > "$TMP_SUMS"
mv "$TMP_SUMS" "$WORK/package/SHA256SUMS"
tar -C "$WORK" -czf "$BUNDLE" package
sha256sum "$BUNDLE" > "$BUNDLE.sha256"
echo "Built $BUNDLE"
