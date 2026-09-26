#!/bin/sh
# pack.sh KIND: put each program of KIND (68k, ppc, carbon, macosx or macos) from
# $WORK/Binary into an archive in $WORK/pack, for a try on a Mac.
# A classic program goes into a StuffIt archive (.sit), a Mac OS X program
# into a zip file. Each archive holds one folder with the program in it,
# with the name of the published program. The folder name ends in
# "rebuild".
# The archives are not a release. They have no signature.
set -eu
kind=${1:?usage: pack.sh 68k|ppc|carbon|macosx|macos}
: "${WORK:?}"
STUFFIT=${STUFFIT:-stuffit}
case $kind in 68k) dir=68K ;; ppc) dir=PPC ;; carbon) dir=Carbon ;; macosx) dir=MacOSX ;; macos) dir=macOS ;; *) exit 2 ;; esac
out="$WORK/pack"
mkdir -p "$out"
for prog in client server tracker; do
	case $prog in client) name=Underline P=Client ;; server) name="Underline Server" P=Server ;; *) name="Underline Tracker" P=Tracker ;; esac
	# The published name of the program, from the published archive that
	# compare.sh unpacked.
	pub="$WORK/published/$kind-$prog"
	folder="UL HL $P 1.9.6 $dir rebuild"
	stage="$WORK/pack-stage/$kind-$prog/$folder"
	rm -rf "$WORK/pack-stage/$kind-$prog"
	mkdir -p "$stage"
	if [ "$kind" = macosx ] || [ "$kind" = macos ]; then
		app=$(find "$pub" -maxdepth 2 -name "*.app" -type d | head -1)
		[ -n "$app" ] || { echo "pack: no published $kind $prog; run compare first" >&2; exit 1; }
		if [ "$kind" = macos ]; then src=$(find "$WORK/build64/$prog" -maxdepth 1 -name "*.app" -type d | head -1)
		else src="$WORK/Binary/MacOSX/$name.app"; fi
		ditto "$src" "$stage/$(basename "$app")"
		archive="$out/$folder.zip"
		rm -f "$archive"
		(cd "$(dirname "$stage")" && ditto -c -k --sequesterRsrc --keepParent "$folder" "$archive")
	else
		p=$(find "$pub" -type f -name "Underline H* $P $dir" | head -1)
		[ -n "$p" ] || { echo "pack: no published $kind $prog; run compare first" >&2; exit 1; }
		ditto "$WORK/Binary/$dir/$name" "$stage/$(basename "$p")"
		archive="$out/$folder.sit"
		rm -f "$archive"
		"$STUFFIT" archive -o "$archive" "$stage" > /dev/null
	fi
	[ -s "$archive" ] || { echo "pack: no $archive" >&2; exit 1; }
	echo "pack: $(basename "$archive") ($(wc -c < "$archive" | tr -d ' ') bytes)"
done
