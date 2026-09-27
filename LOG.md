# Development log

This log records the development work on this repository. The newest entry
is at the bottom. All times are UTC.

## 2026-09-26

### Proof of concept: MPW on hosted runners

- We built the mps emulator from its public source, at commit e2b8c66e.
- mps installed MPW 3.5 from MPW-GM.img.bin. We checked the SHA-256 value
  against the value in mps.
- We compiled and linked `hello.c` as a PowerPC MPW tool and as a 68K MPW
  tool. The 68K tool ran in mps and wrote "Hello from MPW".
- The build passed on four runners: ubuntu-latest, ubuntu-24.04-arm,
  macos-15-intel and macos-latest.

Results:

- Of the six mirrors in mps, only two gave the MPW image. Thus we put the
  image on the 199x.online mirror.
- mps cannot open a folder whose name starts with a dot.
- In an mps command, a relative Mac path must start with a colon
  (`:out:file`). Without the colon, the first name is a volume.
- mps emulates a 68K Macintosh. It cannot run a PowerPC tool.

### Stage 1: the Taskfile

- We moved each step into `Taskfile.yml`. The workflow runs `task` only.
- `inputs.txt` lists each input with its SHA-256 value, its mirror path and
  a fallback URL. `fetch.sh` downloads an input and checks the value.
- The SHA-256 values of the toolchain images are the same as the values in
  the source release (`Toolchains/*/inputs.sha256`).
- `task ci` passed on the four runners.

### Stage 2: the classic toolchain

- We built mps with the patch in the source release
  (`Toolchains/mps/mps.patch`). The patch applied to commit e2b8c66e.
- The CD images of the toolchain are approximately 1.4 GB. The script
  `Toolchains/mps/deps.sh` in the source release uses only small parts of
  them. Thus we made a zip file for each part and put the zip files on the
  mirror. The six parts are 6.3 MB in total.
- After the unzip, the build checks each part against `deps.manifest` in
  the source release. All six parts agreed with the manifest.
- On a macOS computer, the nine classic programs built in 8 minutes 19
  seconds. The largest mps process used 220 MB of memory. Thus memory does
  not limit the number of parallel compiles.

### Stage 3: the classic programs on hosted runners

- The classic build uses three macOS jobs: 68K, PPC and Carbon.
- All three jobs passed. The 68K job used 7 minutes 47 seconds. The PPC and
  Carbon jobs used approximately 9 minutes.
- We removed the Actions cache. A job downloads 31 MB, and this is faster
  than a cache restore of the installed toolchain.

### Stage 4: the Mac OS X programs

- The script `Toolchains/xcode3/deps.sh` uses a small part of the Xcode
  3.2.6 image (4 GB). We made a zip file of this part (134 MB) and put it
  on the mirror.
- The part agreed with `Toolchains/xcode3/deps.manifest`. The part on our
  computer had two `.DS_Store` files that the manifest does not list. We
  removed them from the zip file.
- On a macOS computer, the four Mac OS X programs built in 2 minutes 55
  seconds. Each program has a ppc slice and an i386 slice.

### Stage 5: comparison with the published programs

- `compare.sh` downloads each published program and compares it with the
  program from the build.
- The build must use the build ID of the release (`r433-7ada06a`).
  Without the ID, the programs are different.
- Result for the classic programs: all nine programs are the same as the
  published programs, byte for byte, in the data fork and in the resource
  fork.
- Result for the Mac OS X programs: they are different. We found these
  causes:
  1. The release linked with `-Wl,-S`. The README in the source release
     does not show this flag. Without it, the linker keeps 28 debug symbols
     from `darwin-crt3.c`. We added the flag.
  2. The README tells you to set `MACOSX_DEPLOYMENT_TARGET=10.4`. This
     changes the PowerPC code from gcc 4.2. The release did not set it. We
     removed it.
  3. Make does not build a program again when a flag changes. After a flag
     change, you must delete the linked files.
- After these changes, the i386 slices are the same as the published
  slices. The PowerPC slices have approximately 20 different bytes. The
  differences are in the LC_UUID command and in four object files.
- One object file, compiled alone three times, gave the same bytes each
  time. But these bytes were different from the published object.
- We did two clean parallel builds on the same computer. Eight PowerPC
  object files were different between the two builds. No i386 object file
  was different. Thus the PowerPC output of gcc 4.2 changes from one build
  to the next build. The published PowerPC slices are one sample of this
  output. One of the two builds had only two object files that were
  different from the published objects.
- The first run with comparisons on hosted runners gave these results:
  - All nine classic programs are the same as the published programs, byte
    for byte, in both forks.
  - On macos-15-intel, gcc 4.2 runs natively. The Mac OS X programs have
    21 to 32 different bytes. This agrees with the result on our computer.
    Thus the difference does not come from Rosetta.
  - On macos-latest (arm), the manifest check failed. See "What did not
    work".
- The PowerPC differences are all of one type: gcc 4.2 uses a branch to a
  shared return (`b`) at one time and a direct return (`blr`) at a
  different time. This problem is open. The workflow shows the Mac OS X
  comparison but does not fail on it.
- We made the Xcode part again without the link
  `MacOSX10.4u.sdk/usr/local/lib`. The manifest does not list this link,
  and it points to `/usr/local/lib` on the host computer. The new part is
  `xc3-2.zip`. We gave it a new name, because the mirror keeps a file in
  cache for one year.

### Text style

- We wrote all text in this repository in ASD-STE100 Simplified Technical
  English.
- The ladder job now runs on Linux only. This keeps the number of macOS jobs
  at five, which is the maximum for the free plan.

### Run with the new Xcode part

- The Mac OS X job on macos-latest (arm) passed. gcc 4.2 runs with Rosetta
  there. The job used 13 minutes 45 seconds. On macos-15-intel, the same
  job used 6 minutes 32 seconds.
- On macos-15-intel, the Mac OS X server and tracker were the same as the
  published programs, byte for byte. Only the client was different (19
  bytes). Thus a build can give the published bytes. The difference comes
  from the unstable PowerPC output, not from a different source or
  toolchain.
- The 68K and PPC jobs gave all six programs byte for byte.

### Run with retries

- All seven jobs passed. The downloads gave no errors.
- All nine classic programs were the same as the published programs.
- On macos-latest (arm), the Mac OS X client was the same as the published
  client. On macos-15-intel, the server and the tracker were the same.
  Thus each of the twelve published programs has now come from a build on
  a hosted runner, byte for byte.
- The Mac OS X job on arm used 12 minutes 34 seconds. It was the longest
  job. It now runs only when you start the workflow manually. A run from a
  push now uses approximately 11 minutes.

### Mirror pages

- We added two index pages to the mirror, with the same layout as the
  Underline download page. https://199x.online/mirror/ lists the originals
  and the toolchain parts, with the size, the source and the SHA-256 value
  of each file. https://199x.online/mirror/underline-toolchain/ tells how
  the builds use the parts.
- `mirror/mkpages.py` makes the pages. It reads the SHA-256 values from
  `inputs.txt`.
- The pages tell you that the toolchain parts are not originals. The Xcode
  3.2.6 image is not on the mirror.
- `mirror/htaccess` now has a rule for the pages: browsers check them
  again each time, and the CDN keeps a copy for five minutes.
- All links on the two pages gave "200 OK".

### What runs on GitHub

- We added a "What runs on GitHub" section to the toolchain page and to
  this README. It tells when the workflow starts, which runners it uses,
  what it downloads, what GitHub keeps, and that the releases do not come
  from GitHub.
- After the upload, the origin server gave the new page at once. The CDN
  gave the old page until its five-minute copy expired.

### Where the originals came from

- The mirror page now shows two lines for each original: the publisher,
  and where our copy came from.
- The MPW 3.5 image and the Universal Interfaces 3.4 image came from a
  public mirror of ftp.apple.com. Both files are still there, with the
  same sizes.
- We think that the two CodeWarrior images came from Macintosh Garden. The
  page says this.
- The origin server also keeps a copy of a page for a short time. A request
  with a query string gave the new page at once.

- The page does not name the mirror that gave us the Apple files. We
  looked for these two files on archive.org. The item
  download.info.apple.com.2012.11 is a copy of the Apple support downloads,
  not of the developer files on ftp.apple.com. It does not have them. The
  archive.org search did not find them in a different item.

### The CodeWarrior discs on archive.org

- Our copies of the two CodeWarrior discs came from Macintosh Garden. The
  mirror page now says this without doubt.
- CodeWarrior Pro 5: the item CWPro5Mac has CWPro5MacTools.mdf. This file
  has raw sectors of 2448 bytes (2352 bytes and 96 bytes of subchannel
  data). We took the 2048 data bytes from each sector. The result is the
  same as our copy, byte for byte, with two more sectors at the end.
- CodeWarrior Pro 6: the item codewarrior-6.0 has CW_Tools_6.0_Mac.iso.
  Its HFS partition has the same size as our copy, but 2482 bytes in the
  volume information are different. `deps.sh` made the cw6 part from it,
  and the part agreed with `deps.manifest`. Thus the files are the same.
- The mirror page now gives the archive.org item for each disc and the
  result of the comparison.
- We did not find MPW 3.5 or Universal Interfaces 3.4 on archive.org.

### Archives for a try on a Mac

- `pack.sh` puts each program from the build into an archive: a StuffIt
  archive for a classic program, a zip file for a Mac OS X program. The
  archive has one folder, and the folder has the program with its
  published name. It uses stuffit 0.3.1, the tool of the Underline release.
- On our computer, a 68K client came out of the archive with its resource
  fork and its type and creator (APPL, HTLC).
- A manual start of the workflow now makes a GitHub pre-release, "1.9.6
  rebuild". It has the archives, a SHA256SUMS file and the results of the
  comparison. It has no signature, thus it is not a release of Underline.
- The published archives also have the Bookmarks, the server folders and
  other files. The packaging that adds them is not in the source release.
  Thus these archives have the programs only. The full packaging (the
  folders, the CD, the ISO and the diskettes) can come here when a source
  release has the packaging scripts.

### Experimental: the 64-bit Mac programs (branch supplement)

- The 1.9.6 source release has the `(64)` units, but it cannot build the
  64-bit Mac programs. Their build reads files that are not in the source
  release: the build folder, the POSIX file system units and some
  compatibility headers.
- A build supplement has these files. It has the layout of the Underline
  development repository. The build puts the 1.9.6 source release at
  `Vendor/underline` in it, and the Makefile operates without changes.
- The supplement is on the mirror. It is not a release. The next source
  release will contain these files.
- On our computer (Xcode 26.3, Apple clang 17.0.0), the client, the server
  and the tracker from 1.9.6 and the supplement were the same as the
  published programs: all eight files in each app bundle, byte for byte.

### Result: the 64-bit Mac programs on a hosted runner

- With supplement-2e151951.zip, the macos job on macos-latest built the
  client, the server and the tracker. All eight files in each app bundle
  were the same as the published files, byte for byte.
- Thus the 1.9.6 source release and the supplement give the published
  64-bit Mac programs on a computer that is not ours.

### Changes for the next source release

The results above show problems in the 1.9.6 source release. We changed
the Underline source for the next source release. These changes are not in
1.9.6.

- `treemanifest.py` does not list a link whose target is outside the tree.
  Thus a check gives the same result on each host computer.
- `Toolchains/xcode3/deps.manifest` does not list `libappshell.dylib`. This
  file is a link to a path on the host computer.
- The README shows `-Wl,-S` in the Apple Silicon command. It tells you to
  keep `MACOSX_DEPLOYMENT_TARGET` unset. It tells you to start from a clean
  `Objects` folder after a flag change.

These problems are still open:

- The classic build operates on macOS only. On other systems, mps keeps a
  resource fork in a `.rdump` file and the Finder information in a
  `.idump` file. `Makefile.mps` uses Apple Rez, SetFile and
  `..namedfork/rsrc`. It must have a different mode for these systems.
- The PowerPC output of gcc 4.2 changes between builds.

### What did not work

This section records each attempt that failed, and the cause.

- `mps -install` with its own mirror list failed. The first mirror gave an
  HTML "404 Not Found" page, and mps stopped with "Incorrect checksum".
  mps does not try the next mirror after a bad checksum. Of the six mirrors,
  three did not answer and one gave "403 Forbidden".
- The first build folder was below a folder whose name starts with a dot.
  mps then said "MPW not yet installed", although MPW was installed.
- The first link command used `out:hello.c.x`. MrC said "cannot open output
  file", because `out:` is a volume name. The correct path is
  `:out:hello.c.x`.
- The first `build.sh` ran the PowerPC tool in mps. ToolServer said that
  the tool "can only be used on a Power Macintosh".
- An upload with `rsync --chmod=F644` failed. The rsync on the Mac does not
  accept this form. We used `chmod 644` before the upload.
- A shell loop used a variable with the name `path`. In zsh, `path` is the
  same as `PATH`, thus the loop removed all commands from the search path.
  The loop wrote 17 bad lines into `inputs.txt`. We removed them and used
  `sh` for the loop.
- We did not send the full CD images (1.4 GB) and the Xcode image (4 GB)
  to each job. The download time was too long. We used small parts of the
  images.
- We added an Actions cache for the installed toolchain, then removed it.
  The installed MPW is 122 MB, and a restore is slower than the download of
  the parts.
- The first `compare.sh` run started outside `task`. `INPUTS` was not set,
  and `fetch.sh` stopped.
- The next `compare.sh` run found no programs. The release packages give
  new names to the programs, and `compare.sh` used the build names.
- The Carbon tracker was not found after that change. Its published name is
  "Underline HL Tracker Carbon", because the full name is longer than 31
  characters.
- We added `-Wl,-S`, but the Mac OS X programs stayed 592 bytes larger. Make
  did not link again, because the flag is not a dependency. The first time,
  we deleted only the universal programs. Make then used the old ppc and
  i386 programs in the object folder. The fix was to delete all three.
- We removed `MACOSX_DEPLOYMENT_TARGET` and linked again, but the PowerPC
  bytes did not change. The object files were from the first build, which
  had the variable. Only a clean build gave the new code.
- We compiled one object file (`HotlineTracker.o`) with
  `MACOSX_DEPLOYMENT_TARGET` set to 10.4, 10.5 and 10.6. No value gave the
  published bytes.
- We set fixed values for the gcc garbage collector
  (`--param ggc-min-expand=100 --param ggc-min-heapsize=131072`) and did
  two clean PowerPC builds. Two object files were different between the
  builds. Thus these values do not make the output stable.
- On the macos-latest runner, the manifest check of the Xcode part failed
  with "xc3/MacOSX10.4u.sdk/usr/local/lib: unexpected". This path is a link
  to `/usr/local/lib` on the host. `treemanifest.py` uses `os.walk`. If
  the target of the link exists, `os.walk` shows the link as a folder, and
  the check ignores it. The arm runner has no `/usr/local/lib`, thus the
  link is a file there, and the check fails. The result of the check
  therefore changes with the host computer. This is a problem in the
  source release.
- The Carbon job failed. The download of the source release from
  199x.online gave "403 Forbidden". One ladder job also got a 403 and then
  used the fallback mirror. Both errors occurred when seven jobs started
  their downloads at the same time. `curl --retry` does not try again after
  a 403. `fetch.sh` now uses `--retry-all-errors` with a delay of 10
  seconds.
- The first download of CW_Tools_6.0_Mac.iso stopped at 38 MB, and the
  first comparison was wrong. `curl -f` without `--retry` and without `-C -`
  did not continue. We downloaded it again and checked the MD5 value from
  archive.org.
- The first extraction of CWPro5MacTools.mdf used sectors of 2352 bytes.
  The result was not an HFS volume. The sectors are 2448 bytes.
- The first pre-release had file names with spaces in SHA256SUMS. GitHub
  put a dot for each space in the asset names. Thus `shasum -c` could not
  find the downloads. The release job now gives the files the names with
  dots before it calculates the SHA-256 values.
- A step with `task compare ... | tee compare.txt` passed when the
  comparison failed. The shell gave the exit status of `tee`, not of
  `task`. The steps now use `set -o pipefail`. The classic steps had the
  same problem, but their comparisons had passed.
- On the first run of the branch, the runner used Xcode 26.3 and Apple
  clang 17.0.0 (clang-1700.6.4.2), the same versions as our computer. But
  the executable file of each 64-bit program was different from the
  published file. All other files in the bundles were the same.
  `compare.sh` now shows the sizes, the number of different bytes, the
  UUID of each slice and the first different offsets.
- The difference was the ad hoc code signature. The published programs
  were signed with pages of 4096 bytes (for example 481 hashes in the
  client). The codesign tool on the runner (macOS 26) used pages of 16384
  bytes (121 hashes). The UUID of each slice was the same, thus the code was
  the same. Without the signature, the tracker was the same, byte for
  byte. The build now signs again with `--pagesize 4096`.
- The Makefile in the supplement now signs with `--pagesize 4096`. The new
  supplement is supplement-2e151951.zip. The build does not sign again.
