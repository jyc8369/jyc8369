from __future__ import annotations

import math
from itertools import combinations
from pathlib import Path

WIDTH = 1200
HEIGHT = 800
PHI = (1 + 5**0.5) / 2
FRAMES = 12
DURATION = "18s"
CENTER = (890.0, 405.0)
SCALE = 72.0
CAMERA = 5.8

VERTICES = (
    (0, -1, -PHI), (0, -1, PHI), (0, 1, -PHI), (0, 1, PHI),
    (-1, -PHI, 0), (-1, PHI, 0), (1, -PHI, 0), (1, PHI, 0),
    (-PHI, 0, -1), (-PHI, 0, 1), (PHI, 0, -1), (PHI, 0, 1),
)


def distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


EDGE_LENGTH = min(
    distance(VERTICES[i], VERTICES[j])
    for i, j in combinations(range(12), 2)
)
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
    return (
        CENTER[0] + x * SCALE * perspective,
        CENTER[1] + y * SCALE * perspective,
        z,
    )


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
    depth = max(
        0.0,
        min(1.0, ((a[2] + b[2] + c[2]) / 3 + PHI) / (2 * PHI)),
    )
    return number((0.025 + 0.16 * facing) * (0.7 + 0.3 * depth))


THEMES = {
    "dark": dict(
        outer="#070B12",
        bg0="#070B15",
        bg1="#0B1425",
        border="#26344D",
        bar="#080E19",
        title="#F2F6FF",
        body="#CDD6E6",
        muted="#8190A8",
        faint="#52617A",
        panel="#0A1120",
        panel_border="#31405B",
        grid="#52617A",
        a0="#7C3AED",
        a1="#22D3EE",
        a2="#10B981",
        node="#E6FCFF",
        back="#5F7397",
        chips=("#10261D", "#102331", "#24163A"),
        chip_text=("#4ADE80", "#67E8F9", "#C4B5FD"),
        status="#10B981",
    ),
    "light": dict(
        outer="#F6F8FA",
        bg0="#F6F8FC",
        bg1="#EDF3FA",
        border="#D0D7E2",
        bar="#F0F3F7",
        title="#1F2328",
        body="#32383F",
        muted="#66707B",
        faint="#8A949F",
        panel="#FFFFFF",
        panel_border="#D8DEE8",
        grid="#8A949F",
        a0="#8250DF",
        a1="#0969DA",
        a2="#1A7F37",
        node="#FFFFFF",
        back="#9AA8B9",
        chips=("#EAF7EE", "#EAF2FB", "#F3EAFE"),
        chip_text=("#1A7F37", "#0969DA", "#8250DF"),
        status="#1A7F37",
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
        f'<circle cx="{number(PROJECTED[0][index][0])}" cy="{number(PROJECTED[0][index][1])}" r="3.3" fill="{c["node"]}" stroke="url(#accent)" stroke-width="1.2" filter="url(#softGlow)">'
        f'<animate attributeName="cx" values="{vertex_series(index, 0)}" dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/>'
        f'<animate attributeName="cy" values="{vertex_series(index, 1)}" dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/>'
        '</circle>'
        for index in range(12)
    )
    chip = c["chips"]
    chip_text = c["chip_text"]

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" role="img" aria-label="jyc8369 mathematically regular 3D icosahedron profile banner"><desc>Regular icosahedron generated from the standard golden-ratio coordinates, 30 equal 3D edges, rotation matrices, and perspective projection.</desc><defs><linearGradient id="background" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['bg0']}"/><stop offset="1" stop-color="{c['bg1']}"/></linearGradient><linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['a0']}"><animate attributeName="stop-color" values="{c['a0']};{c['a1']};{c['a2']};{c['a0']}" dur="12s" repeatCount="indefinite"/></stop><stop offset="1" stop-color="{c['a1']}"><animate attributeName="stop-color" values="{c['a1']};{c['a2']};{c['a0']};{c['a1']}" dur="12s" repeatCount="indefinite"/></stop></linearGradient><linearGradient id="faceFill" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['a0']}"/><stop offset=".55" stop-color="{c['a1']}"/><stop offset="1" stop-color="{c['a2']}"/></linearGradient><radialGradient id="coreGlow"><stop offset="0" stop-color="{c['node']}" stop-opacity=".95"/><stop offset=".28" stop-color="{c['a1']}" stop-opacity=".5"/><stop offset="1" stop-color="{c['a1']}" stop-opacity="0"/></radialGradient><pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" fill="none" stroke="{c['grid']}" stroke-opacity=".12" stroke-width=".8"/></pattern><filter id="blur40" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="40"/></filter><filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="1.8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter><filter id="wideGlow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="6"/></filter><clipPath id="window"><rect x="20" y="20" width="1160" height="760" rx="30"/></clipPath><path id="wire" d="{INITIAL_WIRE}"><animate attributeName="d" values="{WIRE_VALUES}" dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/></path></defs><rect width="1200" height="800" rx="36" fill="{c['outer']}"/><g clip-path="url(#window)"><rect x="20" y="20" width="1160" height="760" rx="30" fill="url(#background)" stroke="{c['border']}" stroke-width="2"/><circle cx="910" cy="250" r="250" fill="{c['a1']}" opacity=".14" filter="url(#blur40)"><animate attributeName="cx" values="885;945;885" dur="13s" repeatCount="indefinite"/><animate attributeName="cy" values="225;285;225" dur="15s" repeatCount="indefinite"/></circle><circle cx="1080" cy="610" r="270" fill="{c['a0']}" opacity=".14" filter="url(#blur40)"><animate attributeName="cx" values="1090;1025;1090" dur="16s" repeatCount="indefinite"/><animate attributeName="cy" values="625;570;625" dur="14s" repeatCount="indefinite"/></circle><rect x="20" y="20" width="1160" height="56" fill="{c['bar']}"/><circle cx="50" cy="48" r="6" fill="#FF5F56"/><circle cx="72" cy="48" r="6" fill="#FFBD2E"/><circle cx="94" cy="48" r="6" fill="#27C93F"/><text x="600" y="53" text-anchor="middle" fill="{c['muted']}" font-size="14" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace">jyc8369@github: ~/profile $ ./render --true-3d-icosahedron</text><rect x="20" y="75" width="1160" height="2" fill="url(#accent)"/><g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"><text x="76" y="150" fill="{c['faint']}" font-size="14" letter-spacing="2.9">PROFILE / OVERVIEW</text><text x="76" y="236" fill="{c['title']}" font-size="68" font-weight="700">jyc8369</text><text x="78" y="284" fill="{c['body']}" font-size="24">Practical software</text><text x="78" y="318" fill="{c['body']}" font-size="24">for concrete problems.</text><text x="78" y="358" fill="{c['muted']}" font-size="16">Automation, utilities, and developer tooling</text><text x="78" y="384" fill="{c['muted']}" font-size="16">built around real workflows.</text><rect x="77" y="426" width="132" height="40" rx="20" fill="{chip[0]}" stroke="{chip_text[0]}"/><text x="143" y="453" text-anchor="middle" fill="{chip_text[0]}" font-size="15" font-weight="600">AUTOMATION</text><rect x="223" y="426" width="132" height="40" rx="20" fill="{chip[1]}" stroke="{chip_text[1]}"/><text x="289" y="453" text-anchor="middle" fill="{chip_text[1]}" font-size="15" font-weight="600">UTILITIES</text><rect x="369" y="426" width="148" height="40" rx="20" fill="{chip[2]}" stroke="{chip_text[2]}"/><text x="443" y="453" text-anchor="middle" fill="{chip_text[2]}" font-size="15" font-weight="600">DEV TOOLS</text><rect x="76" y="520" width="500" height="150" rx="24" fill="{c['panel']}" fill-opacity=".56" stroke="{c['panel_border']}"/><text x="102" y="558" fill="{c['faint']}" font-size="12" letter-spacing="2.2">HOW I LIKE TO WORK</text><text x="102" y="598" fill="{c['body']}" font-size="17">Notice friction. Build a usable fix.</text><text x="102" y="626" fill="{c['muted']}" font-size="15"><tspan x="102" dy="0">Deploy it, observe what breaks,</tspan><tspan x="102" dy="23">and improve the next step.</tspan></text><text x="78" y="730" fill="{c['muted']}" font-size="15">&gt; build · deploy · observe · improve</text><rect x="399" y="711" width="10" height="22" rx="1" fill="{c['a1']}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect><g><rect x="628" y="112" width="506" height="610" rx="28" fill="{c['panel']}" fill-opacity=".72" stroke="{c['panel_border']}" stroke-width="1.5"/><rect x="646" y="130" width="470" height="574" rx="22" fill="url(#grid)"/><text x="668" y="168" fill="{c['faint']}" font-size="13" letter-spacing="2.3">TRUE 3D / REGULAR ICOSAHEDRON</text><text x="668" y="198" fill="{c['muted']}" font-size="13">12 vertices · 30 equal edges · 20 equilateral faces</text><ellipse cx="890" cy="405" rx="224" ry="104" fill="none" stroke="{c['a1']}" stroke-opacity=".28" stroke-width="1.4" stroke-dasharray="5 12" transform="rotate(-16 890 405)"><animate attributeName="stroke-dashoffset" values="0;-132" dur="14s" repeatCount="indefinite"/></ellipse><ellipse cx="890" cy="405" rx="202" ry="84" fill="none" stroke="{c['a0']}" stroke-opacity=".2" stroke-width="1.2" stroke-dasharray="2 14" transform="rotate(38 890 405)"><animate attributeName="stroke-dashoffset" values="0;124" dur="18s" repeatCount="indefinite"/></ellipse>{face_markup}<use href="#wire" fill="none" stroke="{c['a1']}" stroke-opacity=".25" stroke-width="11" stroke-linecap="round" filter="url(#wideGlow)"/><use href="#wire" fill="none" stroke="{c['back']}" stroke-opacity=".3" stroke-width="4" stroke-linecap="round"/><use href="#wire" fill="none" stroke="url(#accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" filter="url(#softGlow)"/>{nodes}<circle cx="890" cy="405" r="30" fill="url(#coreGlow)"><animate attributeName="r" values="25;31;25" dur="6s" repeatCount="indefinite"/></circle><text x="668" y="664" fill="{c['muted']}" font-size="12">φ = (1 + √5) / 2 · rotation matrix · perspective projection</text><circle cx="1084" cy="658" r="5" fill="{c['status']}"><animate attributeName="opacity" values=".35;1;.35" dur="1.8s" repeatCount="indefinite"/></circle></g></g></g></svg>'''


for name in THEMES:
    Path(f"{name}.svg").write_text(generate(name), encoding="utf-8")