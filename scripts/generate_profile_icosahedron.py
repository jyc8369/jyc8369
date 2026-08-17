from __future__ import annotations

import math
from itertools import combinations
from pathlib import Path

PHI = (1 + 5**0.5) / 2
FRAMES = 12
DURATION = "18s"
CENTER = (238.0, 119.0)
SCALE = 33.0
CAMERA = 5.8

VERTICES = (
    (0, -1, -PHI), (0, -1, PHI), (0, 1, -PHI), (0, 1, PHI),
    (-1, -PHI, 0), (-1, PHI, 0), (1, -PHI, 0), (1, PHI, 0),
    (-PHI, 0, -1), (-PHI, 0, 1), (PHI, 0, -1), (PHI, 0, 1),
)


def distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


EDGE_LENGTH = min(distance(VERTICES[i], VERTICES[j]) for i, j in combinations(range(12), 2))
EDGES = tuple((i, j) for i, j in combinations(range(12), 2) if abs(distance(VERTICES[i], VERTICES[j]) - EDGE_LENGTH) < 1e-9)
EDGE_SET = {tuple(sorted(edge)) for edge in EDGES}


def outward_face(a, b, c):
    va, vb, vc = VERTICES[a], VERTICES[b], VERTICES[c]
    u = tuple(vb[i] - va[i] for i in range(3))
    v = tuple(vc[i] - va[i] for i in range(3))
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
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
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
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
    return "".join(f"M{number(points[i][0])},{number(points[i][1])}L{number(points[j][0])},{number(points[j][1])}" for i, j in EDGES)


WIRE_VALUES = values(wire_path(frame) for frame in PROJECTED)
INITIAL_WIRE = wire_path(PROJECTED[0])


def vertex_series(index, coordinate):
    return values(number(frame[index][coordinate]) for frame in PROJECTED)


def face_points(face, frame):
    return " ".join(f"{number(PROJECTED[frame][i][0])},{number(PROJECTED[frame][i][1])}" for i in face)


def face_opacity(face, frame):
    a, b, c = (ROTATED[frame][i] for i in face)
    facing = max(0.0, normal(a, b, c)[2])
    depth = max(0.0, min(1.0, ((a[2] + b[2] + c[2]) / 3 + PHI) / (2 * PHI)))
    return number((0.025 + 0.16 * facing) * (0.7 + 0.3 * depth))


THEMES = {
    "dark": dict(outer="#070B12", bg0="#070B15", bg1="#0B1425", border="#26344D", bar="#080E19", title="#F2F6FF", body="#CDD6E6", muted="#8190A8", faint="#52617A", panel="#0A1120", panel_border="#31405B", grid="#52617A", a0="#7C3AED", a1="#22D3EE", a2="#10B981", node="#E6FCFF", back="#5F7397", chips=("#10261D", "#102331", "#24163A"), chip_text=("#4ADE80", "#67E8F9", "#C4B5FD"), status="#10B981"),
    "light": dict(outer="#F6F8FA", bg0="#F6F8FC", bg1="#EDF3FA", border="#D0D7E2", bar="#F0F3F7", title="#1F2328", body="#32383F", muted="#66707B", faint="#8A949F", panel="#FFFFFF", panel_border="#D8DEE8", grid="#8A949F", a0="#8250DF", a1="#0969DA", a2="#1A7F37", node="#FFFFFF", back="#9AA8B9", chips=("#EAF7EE", "#EAF2FB", "#F3EAFE"), chip_text=("#1A7F37", "#0969DA", "#8250DF"), status="#1A7F37"),
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
        f'<circle cx="{number(PROJECTED[0][index][0])}" cy="{number(PROJECTED[0][index][1])}" r="2.4" fill="{c["node"]}" stroke="url(#accent)" stroke-width="1" filter="url(#softGlow)">'
        f'<animate attributeName="cx" values="{vertex_series(index, 0)}" dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/>'
        f'<animate attributeName="cy" values="{vertex_series(index, 1)}" dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/>'
        '</circle>'
        for index in range(12)
    )
    chip = c["chips"]
    chip_text = c["chip_text"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="320" viewBox="0 0 1100 320" role="img" aria-label="jyc8369 mathematically regular 3D icosahedron profile banner"><desc>Regular icosahedron generated from the standard golden-ratio coordinates, 30 equal 3D edges, rotation matrices, and perspective projection.</desc><defs><linearGradient id="background" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['bg0']}"/><stop offset="1" stop-color="{c['bg1']}"/></linearGradient><linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['a0']}"><animate attributeName="stop-color" values="{c['a0']};{c['a1']};{c['a2']};{c['a0']}" dur="12s" repeatCount="indefinite"/></stop><stop offset="1" stop-color="{c['a1']}"><animate attributeName="stop-color" values="{c['a1']};{c['a2']};{c['a0']};{c['a1']}" dur="12s" repeatCount="indefinite"/></stop></linearGradient><linearGradient id="faceFill" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['a0']}"/><stop offset=".55" stop-color="{c['a1']}"/><stop offset="1" stop-color="{c['a2']}"/></linearGradient><radialGradient id="coreGlow"><stop offset="0" stop-color="{c['node']}" stop-opacity=".95"/><stop offset=".28" stop-color="{c['a1']}" stop-opacity=".5"/><stop offset="1" stop-color="{c['a1']}" stop-opacity="0"/></radialGradient><pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="{c['grid']}" stroke-opacity=".12" stroke-width=".8"/></pattern><filter id="blur28" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="28"/></filter><filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="1.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter><filter id="wideGlow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/></filter><clipPath id="window"><rect x="18" y="18" width="1064" height="284" rx="18"/></clipPath><path id="wire" d="{INITIAL_WIRE}"><animate attributeName="d" values="{WIRE_VALUES}" dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/></path></defs><rect width="1100" height="320" rx="20" fill="{c['outer']}"/><g clip-path="url(#window)"><rect x="18" y="18" width="1064" height="284" rx="18" fill="url(#background)" stroke="{c['border']}" stroke-width="2"/><circle cx="835" cy="132" r="138" fill="{c['a1']}" opacity=".18" filter="url(#blur28)"><animate attributeName="cx" values="815;850;815" dur="13s" repeatCount="indefinite"/><animate attributeName="cy" values="120;145;120" dur="15s" repeatCount="indefinite"/></circle><circle cx="995" cy="245" r="150" fill="{c['a0']}" opacity=".18" filter="url(#blur28)"><animate attributeName="cx" values="1000;960;1000" dur="16s" repeatCount="indefinite"/><animate attributeName="cy" values="250;220;250" dur="14s" repeatCount="indefinite"/></circle><rect x="18" y="18" width="1064" height="42" fill="{c['bar']}"/><circle cx="43" cy="39" r="5.5" fill="#FF5F56"/><circle cx="62" cy="39" r="5.5" fill="#FFBD2E"/><circle cx="81" cy="39" r="5.5" fill="#27C93F"/><text x="550" y="44" text-anchor="middle" fill="{c['muted']}" font-size="12" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace">jyc8369@github: ~/profile $ ./render --true-3d-icosahedron</text><rect x="18" y="59" width="1064" height="2" fill="url(#accent)"/><g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"><text x="68" y="101" fill="{c['faint']}" font-size="11" letter-spacing="2.4">PROFILE / OVERVIEW</text><text x="68" y="153" fill="{c['title']}" font-size="46" font-weight="700">jyc8369</text><text x="70" y="186" fill="{c['body']}" font-size="18">Practical software for concrete problems.</text><text x="70" y="210" fill="{c['muted']}" font-size="13">Automation, utilities, and developer tooling with real workflows.</text><rect x="69" y="229" width="112" height="30" rx="15" fill="{chip[0]}" stroke="{chip_text[0]}"/><text x="125" y="249" text-anchor="middle" fill="{chip_text[0]}" font-size="13" font-weight="600">AUTOMATION</text><rect x="191" y="229" width="118" height="30" rx="15" fill="{chip[1]}" stroke="{chip_text[1]}"/><text x="250" y="249" text-anchor="middle" fill="{chip_text[1]}" font-size="13" font-weight="600">UTILITIES</text><rect x="319" y="229" width="128" height="30" rx="15" fill="{chip[2]}" stroke="{chip_text[2]}"/><text x="383" y="249" text-anchor="middle" fill="{chip_text[2]}" font-size="13" font-weight="600">DEV TOOLS</text><text x="70" y="286" fill="{c['muted']}" font-size="13">&gt; build · iterate · document · ship</text><rect x="386" y="272" width="8" height="17" rx="1" fill="{c['a1']}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect><g transform="translate(655 76)"><rect x="0" y="0" width="377" height="210" rx="18" fill="{c['panel']}" fill-opacity=".7" stroke="{c['panel_border']}"/><rect x="14" y="14" width="349" height="182" rx="14" fill="url(#grid)"/><text x="24" y="33" fill="{c['faint']}" font-size="11" letter-spacing="2.1">TRUE 3D / REGULAR ICOSAHEDRON</text><text x="24" y="54" fill="{c['muted']}" font-size="11">12 vertices · 30 equal edges · 20 equilateral faces</text><ellipse cx="238" cy="119" rx="124" ry="55" fill="none" stroke="{c['a1']}" stroke-opacity=".28" stroke-width="1.1" stroke-dasharray="3 9" transform="rotate(-16 238 119)"><animate attributeName="stroke-dashoffset" values="0;-96" dur="14s" repeatCount="indefinite"/></ellipse><ellipse cx="238" cy="119" rx="112" ry="43" fill="none" stroke="{c['a0']}" stroke-opacity=".2" stroke-width="1" stroke-dasharray="1 11" transform="rotate(38 238 119)"><animate attributeName="stroke-dashoffset" values="0;88" dur="18s" repeatCount="indefinite"/></ellipse>{face_markup}<use href="#wire" fill="none" stroke="{c['a1']}" stroke-opacity=".25" stroke-width="7" stroke-linecap="round" filter="url(#wideGlow)"/><use href="#wire" fill="none" stroke="{c['back']}" stroke-opacity=".3" stroke-width="3" stroke-linecap="round"/><use href="#wire" fill="none" stroke="url(#accent)" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" filter="url(#softGlow)"/>{nodes}<circle cx="238" cy="119" r="18" fill="url(#coreGlow)"><animate attributeName="r" values="15;19;15" dur="6s" repeatCount="indefinite"/></circle><text x="24" y="188" fill="{c['muted']}" font-size="10">φ = (1 + √5) / 2 · rotation matrix · perspective projection</text><circle cx="348" cy="184" r="4" fill="{c['status']}"><animate attributeName="opacity" values=".35;1;.35" dur="1.8s" repeatCount="indefinite"/></circle></g></g></g></svg>'''


for name in THEMES:
    Path(f"{name}.svg").write_text(generate(name), encoding="utf-8")
