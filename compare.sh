#!/bin/sh
# compare.sh KIND: compare the published programs of KIND with the programs
# in $WORK/Binary. KIND is 68k, ppc, carbon, macosx or macos.
# For a 64-bit macOS program, it compares all the files in the app bundle.
# For a classic program, the script compares the data fork and the resource
# fork. For a Mac OS X program, it compares the executable file.
# The script writes one line for each fork. It exits with 1 if a fork is
# different.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
kind=${1:?usage: compare.sh 68k|ppc|carbon|macosx|macos}
: "${WORK:?}"
case $kind in 68k) dir=68K ;; ppc) dir=PPC ;; carbon) dir=Carbon ;; macosx) dir=MacOSX ;; macos) dir=macOS ;; *) exit 2 ;; esac
bad=0
for prog in client server tracker; do
	# The release packages give new names to the programs. For example,
	# "Underline" becomes "Underline Hotline Client 68K". If a name is longer
	# than 31 characters, "Hotline" becomes "HL".
	case $prog in client) name=Underline P=Client ;; server) name="Underline Server" P=Server ;; *) name="Underline Tracker" P=Tracker ;; esac
	a=$(sh "$HERE/fetch.sh" "pub-$kind-$prog")
	x="$WORK/published/$kind-$prog"
	rm -rf "$x" && mkdir -p "$x"
	if [ "$kind" = macos ]; then
		ditto -x -k "$a" "$x"
		pubapp=$(find "$x" -maxdepth 2 -name "*.app" -type d | head -1)
		newapp=$(find "$WORK/build64/$prog" -maxdepth 1 -name "*.app" -type d | head -1)
		if [ -z "$pubapp" ] || [ -z "$newapp" ]; then
			echo "compare: $kind $prog: missing (published '${pubapp:-}', rebuilt '${newapp:-}')"; bad=1; continue
		fi
		if d=$(diff -rq "$pubapp" "$newapp" 2>&1); then
			echo "compare: $kind $prog bundle: same, $(find "$newapp" -type f | wc -l | tr -d ' ') files"
		else
			echo "compare: $kind $prog bundle: DIFFERS: $(echo "$d" | wc -l | tr -d ' ') files"; echo "$d" | head -5; bad=1
			# For a different executable: the sizes, the number of different
			# bytes, the UUID of each slice and the first differences.
			pe=$(find "$pubapp/Contents/MacOS" -type f | head -1); ne=$(find "$newapp/Contents/MacOS" -type f | head -1)
			if ! cmp -s "$pe" "$ne"; then
				echo "  executable: sizes $(wc -c < "$pe" | tr -d ' ') and $(wc -c < "$ne" | tr -d ' '), $(cmp -l "$pe" "$ne" 2>/dev/null | wc -l | tr -d ' ') bytes differ"
				for arch in arm64 x86_64; do
					echo "  $arch uuid: $(otool -arch $arch -l "$pe" | awk '/LC_UUID/{f=1} f&&/uuid/{print $2; exit}') and $(otool -arch $arch -l "$ne" | awk '/LC_UUID/{f=1} f&&/uuid/{print $2; exit}')"
				done
				cmp -l "$pe" "$ne" 2>/dev/null | head -8 | sed 's/^/  offset /'
				# The ad hoc signature is at the end of each slice. Compare
				# again without it.
				t=$(mktemp -d)
				cp "$pe" "$t/pub"; cp "$ne" "$t/new"
				codesign --remove-signature "$t/pub"; codesign --remove-signature "$t/new"
				if cmp -s "$t/pub" "$t/new"; then
					echo "  executable without its signature: same"
				else
					echo "  executable without its signature: DIFFERS, $(cmp -l "$t/pub" "$t/new" | wc -l | tr -d ' ') bytes"
				fi
				for f in "$pe" "$ne"; do codesign -dvvv "$f" 2>&1 | grep -E "^(Hash type|CandidateCDHash|CDHash|Format|Signature size|CodeDirectory v)" | sed 's/^/  /'; done
				rm -rf "$t"
			fi
		fi
		continue
	fi
	if [ "$kind" = macosx ]; then
		ditto -x -k "$a" "$x"
		pub=$(find "$x" -path "*/Contents/MacOS/*" -type f | head -1)
		new="$WORK/Binary/MacOSX/$name.app/Contents/MacOS/$(basename "$pub")"
		forks=data
	else
		unar -q -o "$x" "$a" > /dev/null
		pub=$(find "$x" -type f -name "Underline H* $P $dir" | head -1)
		new="$WORK/Binary/$dir/$name"
		forks="data rsrc"
	fi
	if [ -z "$pub" ] || [ -z "$new" ] || [ ! -e "$new" ]; then
		echo "compare: $kind $prog: missing (published '${pub:-}', rebuilt '${new:-}')"
		bad=1
		continue
	fi
	for f in $forks; do
		p=$pub n=$new
		if [ "$f" = rsrc ]; then p=$pub/..namedfork/rsrc n=$new/..namedfork/rsrc; fi
		ps=$(wc -c < "$p" | tr -d ' ') ns=$(wc -c < "$n" | tr -d ' ')
		if cmp -s "$p" "$n"; then
			echo "compare: $kind $prog $f: same, $ps bytes"
		else
			echo "compare: $kind $prog $f: DIFFERS, $(cmp -l "$p" "$n" 2>/dev/null | wc -l | tr -d ' ') bytes differ, sizes $ps and $ns"
			bad=1
		fi
	done
done
exit $bad
