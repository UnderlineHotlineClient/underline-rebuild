#!/bin/sh
# fetch.sh NAME: download the input NAME from inputs.txt into $INPUTS.
# The script tries the mirror first, then the fallback URL.
# It checks the SHA-256 value and writes the path of the file.
# If the file is already in $INPUTS with the correct value, the script does
# not download it again.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
name=${1:?usage: fetch.sh NAME}
: "${INPUTS:?INPUTS names the download folder}"
MIRROR=${MIRROR:-https://199x.online/mirror}
line=$(awk -v n="$name" '$1 == n { print; exit }' "$HERE/inputs.txt")
[ -n "$line" ] || { echo "fetch: no input $name in inputs.txt" >&2; exit 1; }
set -- $line
sum=$2 path=$3 fallback=$4
f="$INPUTS/$(basename "$path" | sed 's/%20/ /g')"
mkdir -p "$INPUTS"
ok() { [ -f "$f" ] && [ "$(shasum -a 256 "$f" | cut -d' ' -f1)" = "$sum" ]; }
if ! ok; then
	case "$path" in http*) first=$path ;; *) first=$MIRROR/$path ;; esac
	for u in "$first" "$fallback"; do
		[ "$u" = - ] && continue
		echo "fetch: $name from $u" >&2
		curl -fsSL --retry 5 --retry-all-errors --retry-delay 10 -o "$f" "$u" && ok && break
		rm -f "$f"
	done
fi
ok || { echo "fetch: $name: no source gave sha256 $sum" >&2; exit 1; }
printf '%s\n' "$f"
