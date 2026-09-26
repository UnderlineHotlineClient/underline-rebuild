# underline-rebuild

This repository builds the Underline 1.9.6 source release again from public
inputs. It then compares each program with the published program.

## What it does

1. It downloads the source release.
2. It downloads each part of the toolchain from a mirror.
3. It checks each download against the SHA-256 value in `inputs.txt`.
4. It builds the programs with the Makefiles in the source release.
5. It compares each program, byte for byte, with the published program.

The workflow in `.github/workflows` does these steps on hosted runners. It
does not keep or upload the downloads.

## How to use it on your computer

You must have Go and [task](https://taskfile.dev).

1. Set `WORK` to a folder for the downloads and the build.
2. Make sure that no folder in the `WORK` path has a name that starts with
   a dot. The mps emulator cannot open such a folder.
3. Type `task --list` to see the tasks.
4. Type `task ci` to do all the steps that your computer can do.

The classic and Mac OS X builds operate on macOS only.

## What runs on GitHub

- The workflow starts after each push, and when you start it manually.
- It uses the free hosted runners: two Linux jobs and four macOS jobs. A
  manual start adds a fifth macOS job, the Mac OS X build on Apple silicon.
- It downloads the published source release and the files on the mirror.
  It checks the SHA-256 value of each file.
- GitHub keeps the logs, for 90 days. The workflow does not keep or upload
  the toolchain. It does not use a cache, and it has no secrets.
- A manual start also puts the programs from the build on the GitHub
  pre-release "1.9.6 rebuild": one archive for each program, the SHA-256
  values and the results of the comparison. The archives have no
  signature, thus they are not a release of Underline. Only the job that
  makes the pre-release can write to the repository.
- The Underline releases do not come from GitHub. Each release is built on
  our own computer. This workflow only shows that the published source
  gives the published programs.

## The ladder

The `ladder` folder has small test programs. Each program tests one part of
the toolchain. If a part is bad, the ladder shows the part before you build
the source release.

## The mirror pages

The `mirror` folder has the source of the index pages of the mirror at
https://199x.online/mirror/.

1. Type `python3 mirror/mkpages.py OUTDIR` to make the pages.
2. Copy the pages to the mirror.
3. Copy `mirror/htaccess` to the mirror as `.htaccess`.
