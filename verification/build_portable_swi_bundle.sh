#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-dist/swi-portable}"
ARCHIVE="${2:-dist/swi-prolog-portable.tar.gz}"

if ! command -v swipl >/dev/null 2>&1; then
  echo "swipl is required on the build host" >&2
  exit 2
fi

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/swi" "$OUT_DIR/lib" "$(dirname "$ARCHIVE")"

SWI_HOME="$(swipl --dump-runtime-variables | sed -n 's/^PLBASE="\(.*\)";$/\1/p')"
if [[ -z "$SWI_HOME" || ! -d "$SWI_HOME" ]]; then
  echo "Could not determine SWI-Prolog home" >&2
  exit 3
fi

cp -aL "$SWI_HOME"/. "$OUT_DIR/swi/"

copy_dep() {
  local src="$1"
  local base
  base="$(basename "$src")"
  case "$base" in
    libc.so.*|libm.so.*|libpthread.so.*|libdl.so.*|librt.so.*|ld-linux*.so.*|libgcc_s.so.*)
      return 0
      ;;
  esac
  [[ -f "$src" ]] && cp -L "$src" "$OUT_DIR/lib/$base"
}

scan_deps() {
  local target="$1"
  ldd "$target" 2>/dev/null | awk '/=> \/[^ ]+/ {print $3} /^\/[^( ]+/ {print $1}' | while read -r dep; do
    [[ -n "$dep" ]] && copy_dep "$dep"
  done
}

ARCH="$(swipl --dump-runtime-variables | sed -n 's/^PLARCH="\(.*\)";$/\1/p')"
SWI_BIN="$OUT_DIR/swi/bin/$ARCH/swipl"
if [[ ! -x "$SWI_BIN" ]]; then
  SWI_BIN="$(find "$OUT_DIR/swi/bin" -type f -name swipl -perm -111 | head -n1)"
fi
[[ -x "$SWI_BIN" ]] || { echo "Could not locate bundled swipl" >&2; exit 4; }

scan_deps "$SWI_BIN"
while IFS= read -r so; do
  scan_deps "$so" || true
done < <(find "$OUT_DIR/swi" -type f \( -name '*.so' -o -name '*.so.*' \))

cat > "$OUT_DIR/swipl-portable" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCH_DIR="$(find "$ROOT/swi/bin" -mindepth 1 -maxdepth 1 -type d | head -n1)"
export SWI_HOME_DIR="$ROOT/swi"
export LD_LIBRARY_PATH="$ROOT/lib:$ROOT/swi/lib/$(basename "$ARCH_DIR"):${LD_LIBRARY_PATH:-}"
exec "$ARCH_DIR/swipl" "$@"
EOF
chmod +x "$OUT_DIR/swipl-portable"

"$OUT_DIR/swipl-portable" --version
tar -C "$(dirname "$OUT_DIR")" -czf "$ARCHIVE" "$(basename "$OUT_DIR")"
sha256sum "$ARCHIVE" > "$ARCHIVE.sha256"
echo "Built $ARCHIVE"
