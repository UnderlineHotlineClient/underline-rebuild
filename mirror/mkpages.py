#!/usr/bin/env python3
"""Make the index pages of the 199x.online mirror.

Usage: mkpages.py OUTDIR

The script reads the SHA-256 values from ../inputs.txt and writes
OUTDIR/index.html and OUTDIR/underline-toolchain/index.html. The layout is
the same as the layout of the Underline download page. All text is in
ASD-STE100 Simplified Technical English.
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = "/underline/web"

# name in inputs.txt: (title, size in bytes, publisher, where our copy came
# from (HTML), what it is)
ORIGINALS = [
    ("mpw", "MPW 3.5 Golden Master", 25109760,
     "Apple, ftp.apple.com, developer/Tool_Chest",
     'A public mirror of ftp.apple.com. The SHA-256 value is also in the source of the mps emulator.',
     "The Macintosh Programmer's Workshop. The mps emulator installs MPW from this image."),
    ("ui34", "Universal Interfaces 3.4", 9230080,
     "Apple, ftp.apple.com, developer/Development_Kits",
     'A public mirror of ftp.apple.com. The SHA-256 value is also in the source of the mps emulator.',
     "The Mac OS headers, Rez files and stub libraries."),
    ("cw5", "CodeWarrior Pro 5 Tools CD", 165249479,
     "Metrowerks, CodeWarrior Pro 5 Tools CD, in a zip file",
     'Macintosh Garden (<a href="https://macintoshgarden.org/">macintoshgarden.org</a>).',
     "The Metrowerks MPW compilers and linkers, the MSL libraries and the runtimes."),
    ("cw6", "CodeWarrior Pro 6 Tools CD", 598292480,
     "Metrowerks, CodeWarrior Tools 6.0 CD",
     'Macintosh Garden (<a href="https://macintoshgarden.org/">macintoshgarden.org</a>).',
     "The Carbon MSL libraries, the CFM-68K Open Transport libraries and MoreFiles."),
]

# The same disc on archive.org, and the result of the comparison (HTML).
ARCHIVE = {
    "cw5": 'Item <a href="https://archive.org/details/CWPro5Mac">CWPro5Mac</a>, file CWPro5MacTools.mdf. '
           'This file has raw sectors of 2448 bytes. Its data is the same as our copy, byte for byte, '
           'with two more sectors at the end.',
    "cw6": 'Item <a href="https://archive.org/details/codewarrior-6.0">codewarrior-6.0</a>, file '
           'CW_Tools_6.0_Mac.iso. This is a different image of the same disc. Some bytes in the volume '
           'information are different. The part that deps.sh makes from it agrees with deps.manifest, '
           'thus the files are the same.',
}

# name in inputs.txt: (title, size in bytes, made from, what it holds, used by)
PARTS = [
    ("part-mwtools", "mwtools", 2056238, "CodeWarrior Pro 5",
     "MWC68K, MWCPPC, MWLink68K and MWLinkPPC. The build puts these four tools into MPW.",
     "classic"),
    ("part-cw5", "cw5", 841837, "CodeWarrior Pro 5",
     "The MSL C and C++ headers and libraries for PowerPC and CFM-68K, the runtimes and the MacTCP headers.",
     "classic"),
    ("part-c68k", "c68k", 209308, "CodeWarrior Pro 5",
     "The 68K libraries (far model, 4-byte int, 8-byte double) and the Open Transport 68K glue.",
     "classic"),
    ("part-cw6", "cw6", 235060, "CodeWarrior Pro 6",
     "The Carbon MSL libraries, PLStringFuncs, the CFM-68K Open Transport libraries and MoreFiles 1.5.",
     "classic"),
    ("part-ui34", "ui34", 2876870, "Universal Interfaces 3.4",
     "CIncludes, RIncludes, the stub libraries and the PowerPC libraries.",
     "classic"),
    ("part-ui68k", "ui68k", 122441, "Universal Interfaces 3.4",
     "The classic 68K libraries.",
     "classic"),
    ("part-xc3", "xc3", 133550872, "Xcode 3.2.6 (not on this mirror)",
     "gcc 4.2 and the Mac OS X 10.4 Universal SDK. The part does not have the link "
     "MacOSX10.4u.sdk/usr/local/lib, because it points to a folder on the host computer.",
     "Mac OS X"),
]


def inputs():
    out = {}
    for line in open(os.path.join(HERE, "..", "inputs.txt")):
        f = line.split()
        if len(f) >= 3 and not f[0].startswith("#"):
            out[f[0]] = (f[1], f[2])
    return out


def e(s):
    return html.escape(s, quote=True)


def mb(n):
    return "%.1f MB" % (n / 1e6) if n >= 1e6 else "%d KB" % round(n / 1e3)


def page(title, nav, body):
    return """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html><head><meta http-equiv="Content-Type" content="text/html; charset=us-ascii">
<title>%(title)s</title><style>
body { margin: 0; font-family: Verdana, Geneva, Helvetica, Arial, sans-serif; color: #000; }
a { color: #333399; } a:hover, a:active { color: #6666FF; }
.links { font-size: 8pt; line-height: 1.5; }
.red { color: #8C1021; }
img.frame { display: block; }
p, li { font-size: 9pt; line-height: 1.4; }
.card { background: #f2f2f2; padding: 6px 8px; margin: 0 0 10px; }
.card:target { background: #dde9f9; }
.card h3 { color: #8C1021; font-size: 10pt; margin: 0 0 4px; }
table.rows { border-collapse: collapse; width: 100%%; }
table.rows th, table.rows td { padding: 2px 4px; vertical-align: top; text-align: left; font-size: 8pt; }
table.rows th { white-space: nowrap; width: 6.5em; }
code { font-size: 8pt; word-break: break-all; }
</style></head>
<body marginheight="0" marginwidth="0" leftmargin="0" topmargin="0" bgcolor="#7F99B3">
<table width="100%%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" valign="top">
<table width="760" cellpadding="0" cellspacing="0" border="0">
<tr><td><img class="frame" src="%(web)s/title_bar.gif" width="760" height="30" border="0" alt=""></td></tr>
<tr><td><img class="frame" src="%(web)s/hotline_home.jpg" width="760" height="118" border="0" alt="Hotline"></td></tr>
<tr><td bgcolor="#FFFFFF"><table width="760" cellspacing="0" cellpadding="0" border="0"><tr>
<td width="20">&nbsp;</td><td width="720" valign="top"><br>
<p class="links" align="center">%(nav)s</p>
%(body)s
<br></td><td width="20">&nbsp;</td></tr></table></td></tr>
<tr><td><table width="100%%" cellspacing="0" cellpadding="0" border="0"><tr>
<td width="16" bgcolor="#7F99B3"><img class="frame" src="%(web)s/btm_left.gif" width="16" height="30" border="0" alt=""></td>
<td width="100%%" align="center" bgcolor="#000000"><font color="#FFFFFF" size="2">%(title)s</font></td>
<td width="15" bgcolor="#7F99B3"><img class="frame" src="%(web)s/btm_right.gif" width="15" height="30" border="0" alt=""></td>
</tr></table></td></tr>
</table></td></tr></table>
</body></html>
""" % {"title": e(title), "nav": nav, "body": body, "web": WEB}


def card(anchor, title, rows):
    cells = "".join("<tr><th>%s</th><td>%s</td></tr>" % (k, v) for k, v in rows)
    return '<div class="card" id="%s"><h3>%s</h3><table class="rows">%s</table></div>' % (anchor, e(title), cells)


def link(path, prefix):
    rel = path[len(prefix):] if path.startswith(prefix) else path
    return '<a href="%s">%s</a>' % (e(rel), e(os.path.basename(path).replace("%20", " ")))


def mirror_page(inp):
    nav = ('<b><a href="#originals">Originals</a></b> &nbsp; <b><a href="#parts">Toolchain parts</a></b> '
           '&nbsp; <b><a href="underline-toolchain/">How the builds use them</a></b>')
    body = ['<p>This mirror keeps the files that the Underline builds download. Each build checks each '
            'file against its SHA-256 value. A file on this mirror does not change. A changed file gets '
            'a new name.</p>',
            '<h3 class="red" id="originals">Originals</h3>',
            '<p>These files are copies of the original images. Their SHA-256 values are the same as the '
            'values in <code>Toolchains/*/inputs.sha256</code> of the Underline source release.</p>']
    for name, title, size, source, got, what in ORIGINALS:
        sha, path = inp[name]
        extra = [("archive.org", ARCHIVE[name])] if name in ARCHIVE else []
        body.append(card(name, title, [("File", link(path, "")), ("Size", mb(size)),
                                       ("Publisher", e(source)), ("Our copy", got)] + extra +
                                      [("Contents", e(what)),
                                       ("SHA-256", "<code>%s</code>" % sha)]))
    body += ['<h3 class="red" id="parts">Toolchain parts</h3>',
             '<p>These files are not originals. Each part is a zip file with a folder that the scripts in '
             'the Underline source release make from an original. The zip files keep the resource forks. '
             'A build downloads the parts, not the originals, because the parts are much smaller. '
             '<a href="underline-toolchain/">How the builds use them</a>.</p>']
    for name, title, size, made, what, used in PARTS:
        sha, path = inp[name]
        body.append(card(name, title, [("File", link(path, "")), ("Size", mb(size)),
                                       ("Made from", e(made)), ("Contents", e(what)),
                                       ("Build", e(used)), ("SHA-256", "<code>%s</code>" % sha)]))
    return page("199x.online mirror", nav, "\n".join(body))


def toolchain_page(inp):
    nav = ('<b><a href="#classic">Classic build</a></b> &nbsp; <b><a href="#macosx">Mac OS X build</a></b> '
           '&nbsp; <b><a href="#github">GitHub</a></b> &nbsp; <b><a href="#check">Checks</a></b> &nbsp; <b><a href="../">All files</a></b>')
    pre = "underline-toolchain/"
    classic = [(n, t) for n, t, s, m, w, u in PARTS if u == "classic"]
    body = [
        '<p>The Underline source release has scripts that make its toolchains from original images. '
        'The files in this folder are the results of these scripts. With these files, a build does not '
        'download 1.4 GB of CD images or the 4 GB Xcode image.</p>',
        '<p>The <a href="https://github.com/UnderlineHotlineClient/underline-rebuild">underline-rebuild</a> '
        'project uses these files. It builds the published source release again and compares each program '
        'with the published program.</p>',
        card("classic", "Classic build: 68K, PPC and Carbon", [
            ("Emulator", "mps, with the patch <code>Toolchains/mps/mps.patch</code> from the source release"),
            ("Script", "<code>Toolchains/mps/deps.sh</code> makes the parts from the originals"),
            ("Steps", "<ol style=\"margin:0;padding-left:16px\">"
                      "<li>mps installs MPW from the MPW 3.5 image.</li>"
                      "<li>The build puts the four tools from <b>mwtools</b> into MPW.</li>"
                      "<li>The build unzips the other five parts.</li>"
                      "<li>The build checks each part against <code>Toolchains/mps/deps.manifest</code>.</li>"
                      "<li><code>Makefile.mps</code> builds the nine programs.</li></ol>"),
            ("Parts", ", ".join('<a href="%s">%s</a>' % (e(inp[n][1][len(pre):]), e(t)) for n, t in classic)),
            ("Result", "All nine programs are the same as the published 1.9.6 programs, byte for byte, in "
                       "the data fork and in the resource fork."),
        ]),
        card("macosx", "Mac OS X build: PowerPC and Intel", [
            ("Script", "<code>Toolchains/xcode3/deps.sh</code> makes the part from the Xcode 3.2.6 image"),
            ("Steps", "<ol style=\"margin:0;padding-left:16px\">"
                      "<li>The build unzips <b>xc3</b>.</li>"
                      "<li>The build checks it against <code>Toolchains/xcode3/deps.manifest</code>.</li>"
                      "<li><code>Makefile.macosx</code> builds the programs with gcc 4.2 and "
                      "<code>LDFLAGS=\"-Wl,-force_cpusubtype_ALL -Wl,-S\"</code>.</li></ol>"),
            ("Part", '<a href="%s">xc3</a>' % e(inp["part-xc3"][1][len(pre):])),
            ("Host", "gcc 4.2 is an Intel program. It runs natively on an Intel Mac and with Rosetta on "
                     "Apple silicon."),
            ("Result", "The i386 code is the same as the published code. The PowerPC code from gcc 4.2 "
                       "changes from one build to the next build. Each published program was the same as a "
                       "build in some runs, but not in all runs."),
        ]),
        card("github", "What runs on GitHub", [
            ("Project", 'One public repository, <a href="https://github.com/UnderlineHotlineClient/underline-rebuild">'
                        "underline-rebuild</a>, with one workflow."),
            ("When", "The workflow starts after each push, and when you start it manually."),
            ("Runners", "The free hosted runners: two Linux jobs and four macOS jobs. A manual start adds a "
                        "fifth macOS job, the Mac OS X build on Apple silicon."),
            ("Downloads", "The published source release and the files on this mirror. Each job checks the "
                          "SHA-256 value of each file."),
            ("Kept", "The logs of the runs, for 90 days. The workflow does not keep or upload the "
                     "toolchain, it does not use a cache, and it has no secrets."),
            ("Try it", "A manual start also puts the programs from the build on a GitHub pre-release, "
                       '<a href="https://github.com/UnderlineHotlineClient/underline-rebuild/releases">1.9.6 '
                       "rebuild</a>: one archive for each program, with SHA-256 values and the results of the "
                       "comparison. The archives have no signature. Thus they are not a release of "
                       "Underline. Only this job can write to the repository."),
            ("Not", "The releases do not come from GitHub. We build each release on our own computer. The "
                    "same tasks give the same result on any Mac. GitHub only shows that the published source "
                    "gives the published programs."),
            ("See", '<a href="https://github.com/UnderlineHotlineClient/underline-rebuild/actions">The runs</a> '
                    '&middot; <a href="https://github.com/UnderlineHotlineClient/underline-rebuild/blob/main/LOG.md">'
                    "The development log</a>"),
        ]),
        card("check", "Checks", [
            ("Download", "Each build checks the SHA-256 value of each file before it uses the file."),
            ("Contents", "After the unzip, each build checks each file in the part, both forks, against the "
                         "manifest in the source release. Thus a part must agree with the output of the "
                         "script in the source release."),
            ("Originals", 'The originals are on <a href="../#originals">the mirror page</a>. You can make the '
                          "parts again from them with <code>deps.sh</code>, and compare."),
        ]),
    ]
    return page("Underline toolchain parts", nav, "\n".join(body))


def main():
    out = sys.argv[1]
    inp = inputs()
    os.makedirs(os.path.join(out, "underline-toolchain"), exist_ok=True)
    with open(os.path.join(out, "index.html"), "w", encoding="ascii") as f:
        f.write(mirror_page(inp))
    with open(os.path.join(out, "underline-toolchain", "index.html"), "w", encoding="ascii") as f:
        f.write(toolchain_page(inp))


if __name__ == "__main__":
    main()
