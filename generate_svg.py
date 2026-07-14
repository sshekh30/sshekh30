#!/usr/bin/env python3
"""Generates dark_mode.svg and light_mode.svg for Satyam's GitHub profile."""
from html import escape

# ---------- CONTENT ----------
USER, HOST = "satyam", "shekhar"
CONTENT = [
    ("field", "OS", "macOS, Ubuntu, Windows"),
    ("field", "Host", "Arizona State University"),
    ("field", "Kernel", "Software Development Engineer"),
    ("field", "Uptime", "26 years"),
    #("field", "Shell", "zsh, bash"),
    #("field", "IDE", "VS Code"),
    ("field", "Status", "Open to New-Grad SWE / backend roles (2026)"),
    ("field", "Location", "Tempe, AZ \u00b7 open to relocation"),
    ("spacer",),
    ("field", "Experience", "Instructional Assistant @ ASU \u00b7 Research Asst @ HEAL Lab \u00b7 Incedo (A10 Networks / ACOS) \u00b7 PharmEasy"),
    ("spacer",),
    ("field", "Languages.Programming", "Go, C, C++, Python, Java, JS / TS"),
    ("field", "Stack.Systems", "Distributed Systems, TCP/IP, epoll, pthreads, GDB, Wireshark"),
    ("field", "Stack.Backend", "Kafka, Gin, FastAPI, Node.js, REST"),
    ("field", "Stack.Cloud", "AWS, Docker, Jenkins, CI/CD, Grafana"),
    ("field", "Stack.Data", "PostgreSQL, MongoDB, Redis, MySQL, Redshift, Hive, Airflow"),
    ("field", "Languages.Real", "English, Hindi"),
    ("spacer",),
    # ("field", "Packages", "Contextual Auto-Response Messaging Agent (CARMA) \u00b7 Elastic Face Recognition \u00b7 Distributed File Discovery"),
    ("header", "Packages"),
    ("field", "CARMA", "Go/Gin backend for contextual reply generation \u2014 SHA-256 response caching, config-injected OpenRouter client (Llama 3.3 70B)"),
    ("field", "Face Recognition", "Elastic face-recognition pipeline on AWS \u2014 custom EC2 autoscaling on SQS queue depth (0-15 instances), MTCNN/FaceNet, Docker/ECR"),
    ("field", "File Discovery", "C++17 file-discovery server \u2014 edge-triggered epoll, pthread rwlocks, length-prefixed framing; 1,000+ concurrent connections"),
    ("field", "Metrics Orchestrator", "Full-stack metrics dashboard \u2014 FastAPI backend, Vue.js frontend, Dockerized with GitHub Actions CI/CD"),
    ("field", "SOPA", "Custom programming language in Prolog \u2014 DCG-based lexer/parser, AST, runtime evaluator with control flow, expressions, and type handling"),
    ("field", "Focus", "Production systems debugging, distributed systems, backend services"),
    ("spacer",),
     ("spacer",),
    ("header", "Contact"),
    ("field", "Email", "sshekh30@asu.edu"),
    ("field", "LinkedIn", "linkedin.com/in/satyam-shekhar22"),
    ("field", "Portfolio", "satyamshekhar.vercel.app"),
    ("field", "GitHub", "github.com/sshekh30"),
    # ("header", "GitHub Stats"),
    # ("stat", "Repos", "repo_data"),
    # ("stat", "Commits", "commit_data"),
    # ("loc", "Lines of Code", None),
]

THEMES = {
    "dark": dict(bg="#1a1b26", bar="#24283b", border="#2f334d",
                 text="#a9b1d6", key="#7aa2f7", leader="#3b4261",
                 header="#bb9af7", prompt="#9ece6a", at="#7dcfff",
                 add="#9ece6a", dele="#f7768e", accent="#e0af68",
                 portrait="#7dcfff", dot_r="#f7768e", dot_y="#e0af68", dot_g="#9ece6a",
                 title="#565f89"),
    "light": dict(bg="#ffffff", bar="#f2f3f7", border="#d5d8e0",
                  text="#343b58", key="#2959aa", leader="#c3c8da",
                  header="#7c3aed", prompt="#2e7d32", at="#0e7490",
                  add="#1a7f37", dele="#cf222e", accent="#8a6d00",
                  portrait="#0e7490", dot_r="#ec6a5e", dot_y="#f5bf4f", dot_g="#61c554",
                  title="#8a90a6"),
}

# ---------- LAYOUT ----------
FS_A = 10.5          # portrait font-size
ADV_A = FS_A * 0.60  # portrait char advance
LH_A = FS_A * 1.06   # portrait line height
FS_P = 13            # panel font-size
ADV_P = FS_P * 0.60  # panel char advance
LH_P = 19            # panel line height
VALUE_COL = 24       # char column where values begin
MAX_VAL = 40         # wrap width for values
PAD = 26
BAR_H = 34
GAP = 34

PORTRAIT = [l.rstrip("\n") for l in open("ascii_v2.txt").read().split("\n")]
PORTRAIT = [l for l in PORTRAIT if l.strip()]
PORTRAIT_W = max(len(l) for l in PORTRAIT)
PANEL_LINES_TOTAL = 60  # dashes length for headers/prompt

def wrap_value(value, width):
    words, lines, cur = value.split(" "), [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= width:
            cur += " " + w
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def esc(s):
    return escape(s, quote=True)

def build(theme_name):
    t = THEMES[theme_name]
    portrait_x = PAD
    portrait_h = len(PORTRAIT) * LH_A
    panel_x = PAD + PORTRAIT_W * ADV_A + GAP
    panel_top = BAR_H + 24

    # Build panel rows as list of (segments) where segments = [(text, cls)]
    rows = []
    # prompt line
    dash = "\u2500" * (PANEL_LINES_TOTAL - len(USER) - len(HOST) - 2)
    rows.append([(USER, "prompt"), ("@", "at"), (HOST, "prompt"), (" " + dash, "leader")])
    for item in CONTENT:
        kind = item[0]
        if kind == "spacer":
            rows.append([(".", "leader")])
        elif kind == "header":
            label = item[1]
            dl = "\u2500" * (PANEL_LINES_TOTAL - len(label) - 4)
            rows.append([("- ", "header"), (label, "header"), (" " + dl, "leader")])
        elif kind in ("field", "stat", "loc"):
            key = item[1]
            prefix = ". " + key
            padn = VALUE_COL - len(prefix) - 1
            leader = " " + ("." * padn if padn > 0 else "") + " "
            if kind == "loc":
                rows.append([(". ", "leader"), (key, "key"), (leader, "leader"),
                             ("\u2026", "text", "loc_data"), (" (", "text"),
                             ("\u2026", "add", "loc_add_data"), ("++", "add"),
                             (", ", "text"),
                             ("\u2026", "dele", "loc_del_data"), ("--", "dele"),
                             (")", "text")])
            elif kind == "stat":
                sid = item[2]
                rows.append([(". ", "leader"), (key, "key"), (leader, "leader"),
                             ("\u2026", "text", sid)])
            else:
                value = item[2]
                vlines = wrap_value(value, MAX_VAL)
                rows.append([(". ", "leader"), (key, "key"), (leader, "leader"),
                             (vlines[0], "text")])
                indent = " " * VALUE_COL
                for extra in vlines[1:]:
                    rows.append([(indent, "leader"), (extra, "text")])

    panel_h = len(rows) * LH_P
    total_h = BAR_H + 24 + max(portrait_h, panel_h) + PAD
    panel_w = max(sum(len(seg[0]) for seg in r) for r in rows) * (FS_P * 0.64)
    total_w = panel_x + panel_w + PAD + 24

    cls_fill = dict(prompt=t["prompt"], at=t["at"], key=t["key"], leader=t["leader"],
                    header=t["header"], text=t["text"], add=t["add"], dele=t["dele"])

    out = []
    out.append(f'<svg width="{total_w:.0f}" height="{total_h:.0f}" '
               f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" '
               f'xmlns="http://www.w3.org/2000/svg" role="img">')
    # styles + animations
    out.append("<style>")
    out.append('text{font-family:"JetBrains Mono","Fira Code","DejaVu Sans Mono",'
               '"SFMono-Regular",Consolas,monospace;}')
    for c, col in cls_fill.items():
        out.append(f'.{c}{{fill:{col};}}')
    out.append(f'.portrait{{fill:{t["portrait"]};}}')
    out.append(f'.title{{fill:{t["title"]};}}')
    out.append('@keyframes fadein{from{opacity:0}to{opacity:1}}')
    out.append('@keyframes rise{from{opacity:0;transform:translateY(4px)}'
               'to{opacity:1;transform:translateY(0)}}')
    out.append('@keyframes blink{50%{opacity:0}}')
    out.append('.line{opacity:0;animation:rise .5s ease forwards;}')
    out.append('.pf{opacity:0;animation:fadein .9s ease forwards;}')
    out.append('.cursor{animation:blink 1.1s step-end infinite;}')
    out.append("</style>")

    # background + window chrome
    out.append(f'<rect x="1" y="1" width="{total_w-2:.0f}" height="{total_h-2:.0f}" '
               f'rx="12" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1.5"/>')
    out.append(f'<path d="M1,13 a12,12 0 0 1 12,-12 h{total_w-26:.0f} a12,12 0 0 1 12,12 '
               f'v{BAR_H-13} h{-(total_w-2):.0f} z" fill="{t["bar"]}"/>')
    for i, dc in enumerate(["dot_r", "dot_y", "dot_g"]):
        out.append(f'<circle cx="{22+i*20}" cy="{BAR_H/2:.0f}" r="6" fill="{t[dc]}"/>')
    out.append(f'<text x="{total_w/2:.0f}" y="{BAR_H/2+4:.0f}" text-anchor="middle" '
               f'font-size="12" class="title">{USER}@{HOST}: ~/profile</text>')

    # portrait (fade in as a group)
    out.append(f'<g class="pf" style="animation-delay:.1s">')
    out.append(f'<text x="{portrait_x}" y="{panel_top}" font-size="{FS_A}" '
               f'class="portrait" xml:space="preserve">')
    for i, line in enumerate(PORTRAIT):
        dy = "0" if i == 0 else f"{LH_A:.2f}"
        out.append(f'<tspan x="{portrait_x}" dy="{dy}">{esc(line)}</tspan>')
    out.append('</text></g>')

    # panel rows (staggered)
    base_delay = 0.35
    step = 0.045
    cursor_xy = None
    for ri, r in enumerate(rows):
        y = panel_top + ri * LH_P
        delay = base_delay + ri * step
        out.append(f'<text x="{panel_x:.0f}" y="{y:.0f}" font-size="{FS_P}" '
                   f'class="line" style="animation-delay:{delay:.2f}s" '
                   f'xml:space="preserve">')
        seg_chars = 0
        for seg in r:
            txt, cls = seg[0], seg[1]
            sid = seg[2] if len(seg) > 2 else None
            idattr = f' id="{sid}"' if sid else ""
            out.append(f'<tspan class="{cls}"{idattr}>{esc(txt)}</tspan>')
            seg_chars += len(txt)
        out.append('</text>')
        cursor_xy = (panel_x + seg_chars * ADV_P, y)
    # blinking cursor after last row
    cx, cy = cursor_xy
    total_delay = base_delay + len(rows) * step
    out.append(f'<rect class="cursor" x="{cx+4:.0f}" y="{cy-FS_P+2:.0f}" width="{ADV_P:.0f}" '
               f'height="{FS_P:.0f}" fill="{t["prompt"]}" opacity="0" '
               f'style="animation-delay:{total_delay:.2f}s"/>')

    out.append('</svg>')
    return "\n".join(out)

for name in ("dark", "light"):
    svg = build(name)
    open(f"{name}_mode.svg", "w").write(svg)
    print(f"{name}_mode.svg written ({len(svg)} bytes)")
