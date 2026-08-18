from __future__ import annotations

from pathlib import Path
from xml.dom import Node, minidom
from xml.sax.saxutils import quoteattr

ASSET_DIR = Path("assets/profile")
INLINE_TAGS = {"text", "tspan", "desc", "title"}
MAX_INLINE_WIDTH = 110
MAX_INLINE_ATTRIBUTES = 4


def remove_whitespace_nodes(node: Node) -> None:
    """Remove formatting-only text nodes before re-serializing XML."""
    for child in list(node.childNodes):
        if child.nodeType == Node.TEXT_NODE and not child.data.strip():
            node.removeChild(child)
        elif child.nodeType == Node.ELEMENT_NODE:
            remove_whitespace_nodes(child)


def attributes(node: Node) -> list[tuple[str, str]]:
    return [
        (node.attributes.item(index).name, node.attributes.item(index).value)
        for index in range(node.attributes.length)
    ]


def inline_opening(node: Node) -> str:
    attrs = " ".join(f"{name}={quoteattr(value)}" for name, value in attributes(node))
    return f"<{node.tagName}{' ' + attrs if attrs else ''}>"


def serialize_inline(node: Node, level: int) -> list[str]:
    """Keep SVG text content compact so formatting does not change rendered whitespace."""
    indent = "  " * level
    opening = inline_opening(node)
    inner = "".join(child.toxml() for child in node.childNodes)
    closing = f"</{node.tagName}>"
    combined = f"{opening}{inner}{closing}"
    attrs = attributes(node)

    if not attrs or len(indent) + len(combined) <= 140:
        return [indent + combined]

    lines = [indent + f"<{node.tagName}"]
    for name, value in attrs[:-1]:
        lines.append(indent + "  " + f"{name}={quoteattr(value)}")

    last_name, last_value = attrs[-1]
    lines.append(
        indent
        + "  "
        + f"{last_name}={quoteattr(last_value)}>"
        + inner
        + closing
    )
    return lines


def serialize_element(node: Node, level: int = 0) -> list[str]:
    indent = "  " * level

    if node.tagName in INLINE_TAGS:
        return serialize_inline(node, level)

    element_children = [
        child for child in node.childNodes if child.nodeType == Node.ELEMENT_NODE
    ]
    text_children = [
        child for child in node.childNodes if child.nodeType == Node.TEXT_NODE and child.data
    ]

    if text_children:
        return [indent + node.toxml()]

    attrs = attributes(node)
    attr_text = " ".join(f"{name}={quoteattr(value)}" for name, value in attrs)

    if not element_children:
        single = f"<{node.tagName}{' ' + attr_text if attr_text else ''}/>"
        if len(indent) + len(single) <= MAX_INLINE_WIDTH and len(attrs) <= MAX_INLINE_ATTRIBUTES:
            return [indent + single]

        lines = [indent + f"<{node.tagName}"]
        for name, value in attrs:
            lines.append(indent + "  " + f"{name}={quoteattr(value)}")
        lines.append(indent + "/>")
        return lines

    opening = f"<{node.tagName}{' ' + attr_text if attr_text else ''}>"
    if len(indent) + len(opening) <= MAX_INLINE_WIDTH and len(attrs) <= MAX_INLINE_ATTRIBUTES:
        lines = [indent + opening]
    else:
        lines = [indent + f"<{node.tagName}"]
        for name, value in attrs:
            lines.append(indent + "  " + f"{name}={quoteattr(value)}")
        lines.append(indent + ">")

    for child in element_children:
        lines.extend(serialize_element(child, level + 1))

    lines.append(indent + f"</{node.tagName}>")
    return lines


def structural_signature(node: Node):
    """Compare XML structure while ignoring formatting-only whitespace nodes."""
    if node.nodeType == Node.ELEMENT_NODE:
        return (
            "element",
            node.tagName,
            tuple(sorted(attributes(node))),
            tuple(
                structural_signature(child)
                for child in node.childNodes
                if not (child.nodeType == Node.TEXT_NODE and not child.data.strip())
            ),
        )
    if node.nodeType == Node.TEXT_NODE:
        return ("text", node.data)
    return (node.nodeType, node.toxml())


def format_svg(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    original_doc = minidom.parseString(original)
    remove_whitespace_nodes(original_doc)
    before = structural_signature(original_doc.documentElement)

    formatted = "\n".join(serialize_element(original_doc.documentElement)) + "\n"

    formatted_doc = minidom.parseString(formatted)
    remove_whitespace_nodes(formatted_doc)
    after = structural_signature(formatted_doc.documentElement)
    if before != after:
        raise RuntimeError(f"Formatting changed SVG structure: {path}")

    if original == formatted:
        return False

    path.write_text(formatted, encoding="utf-8")
    return True


def main() -> None:
    paths = sorted(ASSET_DIR.glob("*.svg"))
    if not paths:
        raise SystemExit(f"No SVG files found under {ASSET_DIR}")

    changed = []
    for path in paths:
        if format_svg(path):
            changed.append(path)
        print(f"formatted {path}")

    print(f"changed {len(changed)} of {len(paths)} SVG files")


if __name__ == "__main__":
    main()
