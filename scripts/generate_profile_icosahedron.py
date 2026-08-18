from __future__ import annotations

import math
from itertools import combinations
from pathlib import Path

PHI = (1 + 5**0.5) / 2
FRAMES = 12
DURATION = "18s"
CENTER = (300.0, 188.0)
SCALE = 48.0
CAMERA = 5.8

VERTICES = (
    (0, -1, -PHI), (0, -1, PHI), (0, 1, -PHI), (0, 1, PHI),
    (-1, -PHI, 0), (-1, PHI, 0), (1, -PHI, 0), (1, PHI, 0),
    (-PHI, 0, -1), (-PHI, 0, 1), (PHI, 0, -1), (PHI, 0, 1),
)


def distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


EDGE_LENGTH = min(distance(VERTICES[i], VERTICES[j]) for i, j in combinations(range(12), 2))
EDGES = tuple(
    (i, j)
    for i, j in combinations(range(12), 2)
    if abs(distance(VERTICES[i], VERTICES[j]) - EDGE_LENGTH) < 1e-9
)
EDGE_SET = {tuple(sorted(edge)) for edge in EDGES}


def outward_face(a, b, c):
    va, vb, vc = VERTICES[a], VERTICES[b], VERTICES[c]
    u = tuple(vb[i] - va[i] for i in range(3))
    v = tuple(vc[i] - va[i] for i in range(3))
    n = (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )
    center = tuple((va[i] + vb[i] + vc[i]) / 3 for i in range(3))
    return (a, c, b) if sum(n[i] * center[i] for i in range(3)) < 0 else (a, b, c)


FACES = tuple(
    outward_face(a, b, c)
    for a, b, c in combinations(range(12), 3)
    if tuple(sorted((a, b))) in EDGE_SET
    and tuple(sorted((a, c))) in EDGE_SET
    and tuple(sorted((b, c))) in EDGE_SET
)

assert len(VERTICES) == 12
assert len(EDGES) == 30
assert len(FACES) == 20
assert max(abs(distance(VERTICES[i], VERTICES[j]) - 2.0) for i, j in EDGES) < 1e-9


def rotate(vertex, ax, ay, az):
    x, y, z = vertex
    cx, sx = math.cos(ax), math.sin(ax)
    y, z = y * cx - z * sx, y * sx + z * cx
    cy, sy = math.cos(ay), math.sin(ay)
    x, z = x * cy + z * sy, -x * sy + z * cy
    cz, sz = math.cos(az), math.sin(az)
    return x * cz - y * sz, x * sz + y * cz, z


def project(vertex):
    x, y, z = vertex
    perspective = CAMERA / (CAMERA - z)
    return CENTER[0] + x * SCALE * perspective, CENTER[1] + y * SCALE * perspective, z


def normal(a, b, c):
    u = tuple(b[i] - a[i] for i in range(3))
    v = tuple(c[i] - a[i] for i in range(3))
    n = (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )
    length = math.sqrt(sum(value * value for value in n))
    return tuple(value / length for value in n)


def number(value):
    return f"{value:.1f}"


ROTATED = []
PROJECTED = []
for frame in range(FRAMES):
    t = 2 * math.pi * frame / FRAMES
    ax = math.radians(-17) + math.radians(6) * math.sin(t)
    ay = t
    az = math.radians(10) + math.radians(4) * math.cos(t)
    rotated = [rotate(vertex, ax, ay, az) for vertex in VERTICES]
    ROTATED.append(rotated)
    PROJECTED.append([project(vertex) for vertex in rotated])
ROTATED.append(ROTATED[0])
PROJECTED.append(PROJECTED[0])


def values(items):
    return ";".join(items)


def wire_path(points):
    return "".join(
        f"M{number(points[i][0])},{number(points[i][1])}"
        f"L{number(points[j][0])},{number(points[j][1])}"
        for i, j in EDGES
    )


WIRE_VALUES = values(wire_path(frame) for frame in PROJECTED)
INITIAL_WIRE = wire_path(PROJECTED[0])


def vertex_series(index, coordinate):
    return values(number(frame[index][coordinate]) for frame in PROJECTED)


def face_points(face, frame):
    return " ".join(
        f"{number(PROJECTED[frame][i][0])},{number(PROJECTED[frame][i][1])}"
        for i in face
    )


def face_opacity(face, frame):
    a, b, c = (ROTATED[frame][i] for i in face)
    facing = max(0.0, normal(a, b, c)[2])
    depth = max(0.0, min(1.0, ((a[2] + b[2] + c[2]) / 3 + PHI) / (2 * PHI)))
    return number((0.025 + 0.16 * facing) * (0.7 + 0.3 * depth))


THEMES = {
    "dark": dict(
        outer="#070B12", bg0="#070B15", bg1="#0B1425", border="#26344D",
        bar="#080E19", title="#F2F6FF", body="#CDD6E6", muted="#8190A8",
        faint="#52617A", panel="#0A1120", panel_border="#31405B", grid="#52617A",
        a0="#7C3AED", a1="#22D3EE", a2="#10B981", node="#E6FCFF",
        back="#5F7397", chips=("#10261D", "#102331", "#24163A"),
        chip_text=("#4ADE80", "#67E8F9", "#C4B5FD"), status="#10B981",
    ),
    "light": dict(
        outer="#F6F8FA", bg0="#F6F8FC", bg1="#EDF3FA", border="#D0D7E2",
        bar="#F0F3F7", title="#1F2328", body="#32383F", muted="#66707B",
        faint="#8A949F", panel="#FFFFFF", panel_border="#D8DEE8", grid="#8A949F",
        a0="#8250DF", a1="#0969DA", a2="#1A7F37", node="#FFFFFF",
        back="#9AA8B9", chips=("#EAF7EE", "#EAF2FB", "#F3EAFE"),
        chip_text=("#1A7F37", "#0969DA", "#8250DF"), status="#1A7F37",
    ),
}


def generate(theme_name):
    c = THEMES[theme_name]
    face_markup = "".join(
        f'<polygon points="{face_points(face, 0)}" fill="url(#faceFill)" opacity="{face_opacity(face, 0)}">'
        f'<animate attributeName="points" values="{values(face_points(face, frame) for frame in range(FRAMES + 1))}" dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/>'
        f'<animate attributeName="opacity" values="{values(face_opacity(face, frame) for frame in range(FRAMES + 1))}" dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/>'
        '</polygon>'
        for face in FACES
    )
    nodes = "".join(
        f'<circle cx="{number(PROJECTED[0][index][0])}" cy="{number(PROJECTED[0][index][1])}" r="3" fill="{c["node"]}" stroke="url(#accent)" stroke-width="1.2" filter="url(#softGlow)">'
        f'<animate attributeName="cx" values="{vertex_series(index, 0)}" dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/>'
        f'<animate attributeName="cy" values="{vertex_series(index, 1)}" dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/>'
        '</circle>'
        for index in range(12)
    )
    chip = c["chips"]
    chip_text = c["chip_text"]

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="480" viewBox="0 0 1200 480" role="img" aria-label="jyc8369 mathematically regular 3D icosahedron profile banner"><desc>Regular icosahedron generated from the standard golden-ratio coordinates, 30 equal 3D edges, rotation matrices, and perspective projection.</desc><defs><linearGradient id="background" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['bg0']}"/><stop offset="1" stop-color="{c['bg1']}"/></linearGradient><linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['a0']}"><animate attributeName="stop-color" values="{c['a0']};{c['a1']};{c['a2']};{c['a0']}" dur="12s" repeatCount="indefinite"/></stop><stop offset="1" stop-color="{c['a1']}"><animate attributeName="stop-color" values="{c['a1']};{c['a2']};{c['a0']};{c['a1']}" dur="12s" repeatCount="indefinite"/></stop></linearGradient><linearGradient id="faceFill" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['a0']}"/><stop offset=".55" stop-color="{c['a1']}"/><stop offset="1" stop-color="{c['a2']}"/></linearGradient><radialGradient id="coreGlow"><stop offset="0" stop-color="{c['node']}" stop-opacity=".95"/><stop offset=".28" stop-color="{c['a1']}" stop-opacity=".5"/><stop offset="1" stop-color="{c['a1']}" stop-opacity="0"/></radialGradient><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{c['grid']}" stroke-opacity=".12" stroke-width=".8"/></pattern><filter id="blur32" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="32"/></filter><filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter><filter id="wideGlow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="5"/></filter><clipPath id="window"><rect x="20" y="20" width="1160" height="440" rx="28"/></clipPath><path id="wire" d="{INITIAL_WIRE}"><animate attributeName="d" values="{WIRE_VALUES}" dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/></path></defs><rect width="1200" height="480" rx="34" fill="{c['outer']}"/><g clip-path="url(#window)"><rect x="20" y="20" width="1160" height="440" rx="28" fill="url(#background)" stroke="{c['border']}" stroke-width="2"/><circle cx="920" cy="175" r="180" fill="{c['a1']}" opacity=".16" filter="url(#blur32)"><animate attributeName="cx" values="900;945;900" dur="13s" repeatCount="indefinite"/><animate attributeName="cy" values="160;195;160" dur="15s" repeatCount="indefinite"/></circle><circle cx="1100" cy="360" r="195" fill="{c['a0']}" opacity=".16" filter="url(#blur32)"><animate attributeName="cx" values="1110;1060;1110" dur="16s" repeatCount="indefinite"/><animate attributeName="cy" values="365;325;365" dur="14s" repeatCount="indefinite"/></circle><rect x="20" y="20" width="1160" height="52" fill="{c['bar']}"/><circle cx="48" cy="46" r="6" fill="#FF5F56"/><circle cx="70" cy="46" r="6" fill="#FFBD2E"/><circle cx="92" cy="46" r="6" fill="#27C93F"/><text x="600" y="51" text-anchor="middle" fill="{c['muted']}" font-size="14" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace">jyc8369@github: ~/profile $ ./render --true-3d-icosahedron</text><rect x="20" y="71" width="1160" height="2" fill="url(#accent)"/><g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"><text x="72" y="128" fill="{c['faint']}" font-size="13" letter-spacing="2.7">PROFILE / OVERVIEW</text><text x="72" y="196" fill="{c['title']}" font-size="56" font-weight="700">jyc8369</text><text x="74" y="238" fill="{c['body']}" font-size="21">Practical software for concrete problems.</text><text x="74" y="270" fill="{c['muted']}" font-size="15">Automation, utilities, and developer tooling built around real workflows.</text><rect x="73" y="306" width="126" height="36" rx="18" fill="{chip[0]}" stroke="{chip_text[0]}"/><text x="136" y="330" text-anchor="middle" fill="{chip_text[0]}" font-size="14" font-weight="600">AUTOMATION</text><rect x="211" y="306" width="126" height="36" rx="18" fill="{chip[1]}" stroke="{chip_text[1]}"/><text x="274" y="330" text-anchor="middle" fill="{chip_text[1]}" font-size="14" font-weight="600">UTILITIES</text><rect x="349" y="306" width="142" height="36" rx="18" fill="{chip[2]}" stroke="{chip_text[2]}"/><text x="420" y="330" text-anchor="middle" fill="{chip_text[2]}" font-size="14" font-weight="600">DEV TOOLS</text><text x="74" y="388" fill="{c['muted']}" font-size="14">&gt; build · deploy · observe · improve</text><rect x="383" y="372" width="9" height="19" rx="1" fill="{c['a1']}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect><g transform="translate(660 96)"><rect x="0" y="0" width="470" height="330" rx="22" fill="{c['panel']}" fill-opacity=".72" stroke="{c['panel_border']}" stroke-width="1.4"/><rect x="16" y="16" width="438" height="298" rx="17" fill="url(#grid)"/><text x="28" y="40" fill="{c['faint']}" font-size="12" letter-spacing="2.2">TRUE 3D / REGULAR ICOSAHEDRON</text><text x="28" y="66" fill="{c['muted']}" font-size="12">12 vertices · 30 equal edges · 20 equilateral faces</text><ellipse cx="300" cy="188" rx="170" ry="78" fill="none" stroke="{c['a1']}" stroke-opacity=".28" stroke-width="1.2" stroke-dasharray="4 10" transform="rotate(-16 300 188)"><animate attributeName="stroke-dashoffset" values="0;-112" dur="14s" repeatCount="indefinite"/></ellipse><ellipse cx="300" cy="188" rx="152" ry="62" fill="none" stroke="{c['a0']}" stroke-opacity=".2" stroke-width="1.1" stroke-dasharray="2 12" transform="rotate(38 300 188)"><animate attributeName="stroke-dashoffset" values="0;104" dur="18s" repeatCount="indefinite"/></ellipse>{face_markup}<use href="#wire" fill="none" stroke="{c['a1']}" stroke-opacity=".25" stroke-width="9" stroke-linecap="round" filter="url(#wideGlow)"/><use href="#wire" fill="none" stroke="{c['back']}" stroke-opacity=".3" stroke-width="3.4" stroke-linecap="round"/><use href="#wire" fill="none" stroke="url(#accent)" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" filter="url(#softGlow)"/>{nodes}<circle cx="300" cy="188" r="24" fill="url(#coreGlow)"><animate attributeName="r" values="20;25;20" dur="6s" repeatCount="indefinite"/></circle><text x="28" y="296" fill="{c['muted']}" font-size="11">φ = (1 + √5) / 2 · rotation matrix · perspective projection</text><circle cx="430" cy="292" r="5" fill="{c['status']}"><animate attributeName="opacity" values=".35;1;.35" dur="1.8s" repeatCount="indefinite"/></circle></g></g></g></svg>'''


for name in THEMES:
    Path(f"{name}.svg").write_text(generate(name), encoding="utf-8")
