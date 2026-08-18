from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ASSET_DIR = Path("assets/profile")
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

FONT_MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
FONT_DISPLAY = "system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',sans-serif"
FONT_BODY = "system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',sans-serif"

PANEL_NAMES = ("about", "values", "lifecycle", "projects", "stack")
STAGE_LABELS = {"BUILD", "DEPLOY", "OBSERVE", "DEBUG", "IMPROVE"}
MONO_LABELS = {
    "CURRENT DIRECTION",
    "LONG-TERM GOAL",
    "LANGUAGES",
    "DIRECTION · DEVOPS / SYSTEMS ENGINEERING",
    "GOAL",
    "DEVOPS",
    "SYSTEMS ENGINEERING",
    "RELIABILITY",
}


def q(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def number(value: str | None, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except ValueError:
        return default


def text_value(element: ET.Element) -> str:
    return "".join(element.itertext()).strip()


def add_animate(
    element: ET.Element,
    attribute: str,
    values: str,
    duration: str,
    *,
    begin: str | None = None,
) -> None:
    animate = ET.SubElement(element, q("animate"))
    animate.set("attributeName", attribute)
    animate.set("values", values)
    animate.set("dur", duration)
    animate.set("repeatCount", "indefinite")
    animate.set("calcMode", "spline")
    animate.set("keyTimes", "0;0.5;1")
    animate.set("keySplines", ".4 0 .2 1;.4 0 .2 1")
    if begin:
        animate.set("begin", begin)


def classify_fonts(root: ET.Element) -> None:
    for element in root.iter(q("text")):
        text = text_value(element)
        size = number(element.get("font-size"))
        weight = element.get("font-weight", "")
        letter_spacing = element.get("letter-spacing")
        y = element.get("y")

        if y == "51" or letter_spacing or text in MONO_LABELS:
            family = FONT_MONO
        elif text in STAGE_LABELS:
            family = FONT_DISPLAY
        elif size >= 30 or (weight in {"700", "800"} and size >= 16):
            family = FONT_DISPLAY
        elif size <= 13 and ("·" in text or text.isupper()):
            family = FONT_MONO
        else:
            family = FONT_BODY

        element.set("font-family", family)


def split_about_step_titles(root: ET.Element) -> None:
    pattern = re.compile(r"^(0[1-3]) · (.+)$")

    for parent in root.iter():
        children = list(parent)
        for index, child in enumerate(children):
            if child.tag != q("text"):
                continue

            match = pattern.match(text_value(child))
            if not match:
                continue

            number_text, title_text = match.groups()
            old_x = number(child.get("x"))
            child.text = number_text
            child.set("font-family", FONT_MONO)
            child.set("letter-spacing", ".6")

            title = ET.Element(q("text"), child.attrib.copy())
            title.set("x", f"{old_x + 38:g}")
            title.set("font-family", FONT_DISPLAY)
            title.attrib.pop("letter-spacing", None)
            title.text = title_text
            parent.insert(index + 1, title)


def pulse_vertical_accents(root: ET.Element) -> None:
    stripes = [
        element
        for element in root.iter(q("rect"))
        if element.get("width") == "8" and number(element.get("height")) >= 40
    ]

    for index, stripe in enumerate(stripes):
        add_animate(
            stripe,
            "opacity",
            ".68;1;.68",
            f"{6.8 + (index % 3) * 0.7:.1f}s",
            begin=f"{index * 0.55:.2f}s",
        )


def animate_about(root: ET.Element) -> None:
    direction_rects = [
        element
        for element in root.iter(q("rect"))
        if element.get("width") == "265" and element.get("height") == "32"
    ]
    for index, rect in enumerate(direction_rects):
        add_animate(
            rect,
            "stroke-opacity",
            ".42;1;.42",
            "5.4s",
            begin=f"{index * 1.4:.1f}s",
        )

    for group in root.iter(q("g")):
        if group.get("transform") != "translate(70 650)":
            continue

        scan = ET.SubElement(group, q("rect"))
        scan.set("x", "0")
        scan.set("y", "0")
        scan.set("width", "130")
        scan.set("height", "2")
        scan.set("rx", "1")
        scan.set("fill", "url(#accent)")
        scan.set("opacity", ".58")
        animate = ET.SubElement(scan, q("animate"))
        animate.set("attributeName", "x")
        animate.set("values", "-130;1060")
        animate.set("dur", "10s")
        animate.set("repeatCount", "indefinite")
        animate.set("calcMode", "linear")
        break


def animate_values(root: ET.Element) -> None:
    cards: list[ET.Element] = []
    for group in root.iter(q("g")):
        children = list(group)
        card_rect = next(
            (
                child
                for child in children
                if child.tag == q("rect")
                and child.get("width") == "510"
                and child.get("height") == "145"
            ),
            None,
        )
        if card_rect is not None:
            cards.append(group)

    for index, group in enumerate(cards):
        title = next(
            (
                child
                for child in group
                if child.tag == q("text") and number(child.get("font-size")) >= 18
            ),
            None,
        )
        accent = title.get("fill", "url(#accent)") if title is not None else "url(#accent)"
        dot = ET.SubElement(group, q("circle"))
        dot.set("cx", "470")
        dot.set("cy", "38")
        dot.set("r", "4")
        dot.set("fill", accent)
        dot.set("opacity", ".55")
        add_animate(dot, "r", "3;5;3", "7.2s", begin=f"{index * 0.9:.1f}s")
        add_animate(dot, "opacity", ".35;1;.35", "7.2s", begin=f"{index * 0.9:.1f}s")


def animate_lifecycle(root: ET.Element) -> None:
    nodes = [
        element
        for element in root.iter(q("circle"))
        if element.get("r") == "34" and element.get("stroke")
    ]
    for index, node in enumerate(nodes):
        add_animate(
            node,
            "stroke-opacity",
            ".48;1;.48",
            "8s",
            begin=f"{index * 1.35:.2f}s",
        )
        add_animate(
            node,
            "stroke-width",
            "2.2;3.4;2.2",
            "8s",
            begin=f"{index * 1.35:.2f}s",
        )


def animate_projects(root: ET.Element) -> None:
    cards: list[ET.Element] = []
    for group in root.iter(q("g")):
        card_rect = next(
            (
                child
                for child in group
                if child.tag == q("rect")
                and child.get("width") == "510"
                and child.get("height") == "185"
            ),
            None,
        )
        if card_rect is not None:
            cards.append(group)

    for index, group in enumerate(cards):
        accent_rect = next(
            (
                child
                for child in group
                if child.tag == q("rect") and child.get("width") == "8"
            ),
            None,
        )
        accent = accent_rect.get("fill", "url(#accent)") if accent_rect is not None else "url(#accent)"
        dot = ET.SubElement(group, q("circle"))
        dot.set("cx", "474")
        dot.set("cy", "34")
        dot.set("r", "4")
        dot.set("fill", accent)
        add_animate(dot, "opacity", ".25;1;.25", "6.6s", begin=f"{index * 1.0:.1f}s")
        add_animate(dot, "r", "3;5;3", "6.6s", begin=f"{index * 1.0:.1f}s")


def animate_stack(root: ET.Element) -> None:
    focus_rects = [
        element
        for element in root.iter(q("rect"))
        if element.get("width") == "225" and element.get("height") == "68"
    ]
    for index, rect in enumerate(focus_rects):
        add_animate(
            rect,
            "stroke-opacity",
            ".42;1;.42",
            "7.5s",
            begin=f"{index * 0.75:.2f}s",
        )

    underline = ET.SubElement(root, q("rect"))
    underline.set("x", "630")
    underline.set("y", "318")
    underline.set("width", "90")
    underline.set("height", "2")
    underline.set("rx", "1")
    underline.set("fill", "url(#accent)")
    underline.set("opacity", ".38")
    add_animate(underline, "width", "90;480;90", "9s")


def enhance(path: Path) -> None:
    tree = ET.parse(path)
    root = tree.getroot()

    classify_fonts(root)
    pulse_vertical_accents(root)

    name = path.stem.rsplit("-", 1)[0]
    if name == "about":
        split_about_step_titles(root)
        animate_about(root)
    elif name == "values":
        animate_values(root)
    elif name == "lifecycle":
        animate_lifecycle(root)
    elif name == "projects":
        animate_projects(root)
    elif name == "stack":
        animate_stack(root)

    tree.write(path, encoding="unicode", xml_declaration=False)
    with path.open("a", encoding="utf-8") as file:
        file.write("\n")
    print(f"enhanced {path}")


def main() -> None:
    for name in PANEL_NAMES:
        for theme in ("dark", "light"):
            path = ASSET_DIR / f"{name}-{theme}.svg"
            if not path.exists():
                raise SystemExit(f"Missing generated profile panel: {path}")
            enhance(path)


if __name__ == "__main__":
    main()
