#!/bin/sh
# compare.sh KIND: compare the published programs of KIND with the programs
# in $WORK/Binary. KIND is 68k, ppc, carbon or macosx.
# For a classic program, the script compares the data fork and the resource
# fork. For a Mac OS X program, it compares the executable file.
# The script writes one line for each fork. It exits with 1 if a fork is
# different.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
kind=${1:?usage: compare.sh 68k|ppc|carbon|macosx}
: "${WORK:?}"
case $kind in 68k) dir=68K ;; ppc) dir=PPC ;; carbon) dir=Carbon ;; macosx) dir=MacOSX ;; *) exit 2 ;; esac
bad=0
for prog in client server tracker; do
	# The release packages give new names to the programs. For example,
	# "Underline" becomes "Underline Hotline Client 68K". If a name is longer
	# than 31 characters, "Hotline" becomes "HL".
	case $prog in client) name=Underline P=Client ;; server) name="Underline Server" P=Server ;; *) name="Underline Tracker" P=Tracker ;; esac
	a=$(sh "$HERE/fetch.sh" "pub-$kind-$prog")
	x="$WORK/published/$kind-$prog"
	rm -rf "$x" && mkdir -p "$x"
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
