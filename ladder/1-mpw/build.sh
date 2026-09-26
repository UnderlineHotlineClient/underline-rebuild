#!/bin/sh
# Compile and link hello.c as a PowerPC MPW tool and as a 68K MPW tool.
# The script uses the Apple MPW 3.5 compilers in the mps emulator.
# mps does not give the exit status of a tool. Thus each step writes
# {Status}, and the script examines it.
set -eu
MPS=${MPS:-mps}
run() {
	out=$("$MPS" -c "Set Exit 0; $1; Echo status={Status}" 2>&1 | tr -d '\r')
	printf '%s\n' "$out"
	case "$out" in *status=0) ;; *) echo "build: failed: $1" >&2; exit 1 ;; esac
}
cd "$(dirname "$0")"; mkdir -p out
run 'MrC hello.c -o :out:hello.c.x'
run 'PPCLink -o :out:HelloPPC -t MPST -c "MPS " :out:hello.c.x "{SharedLibraries}StdCLib" "{SharedLibraries}InterfaceLib" "{PPCLibraries}StdCRuntime.o" "{PPCLibraries}PPCCRuntime.o"'
run 'SC hello.c -o :out:hello.c.o'
run 'Link -o :out:Hello68K -t MPST -c "MPS " -d :out:hello.c.o "{CLibraries}StdCLib.o" "{Libraries}Interface.o" "{Libraries}MacRuntime.o" "{Libraries}IntEnv.o"'
# Make sure that the data fork of the PowerPC tool is a PEF container.
head -c 12 out/HelloPPC | od -c | head -1
head -c 12 out/HelloPPC | grep -q 'Joy!peffpwpc' || { echo "build: HelloPPC is not PEF" >&2; exit 1; }
# Run the 68K tool. mps emulates a 68K Macintosh, thus it cannot run the PowerPC tool.
run ':out:Hello68K'
