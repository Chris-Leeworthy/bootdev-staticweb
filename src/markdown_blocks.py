from enum import Enum

from htmlnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node, text_to_textnodes


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    return [block.strip() for block in blocks if block.strip() != ""]


def block_to_block_type(block):
    if block.startswith("#"):
        hashes = 0
        for char in block:
            if char == "#":
                hashes += 1
            else:
                break
        if hashes <= 6 and len(block) > hashes and block[hashes] == " ":
            return BlockType.HEADING

    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    lines = block.split("\n")
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    is_ordered_list = True
    for index, line in enumerate(lines):
        if not line.startswith(f"{index + 1}. "):
            is_ordered_list = False
            break
    if is_ordered_list:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(text_node) for text_node in text_nodes]


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.PARAGRAPH:
            children.append(paragraph_to_html_node(block))
        elif block_type == BlockType.HEADING:
            children.append(heading_to_html_node(block))
        elif block_type == BlockType.CODE:
            children.append(code_to_html_node(block))
        elif block_type == BlockType.QUOTE:
            children.append(quote_to_html_node(block))
        elif block_type == BlockType.UNORDERED_LIST:
            children.append(unordered_list_to_html_node(block))
        elif block_type == BlockType.ORDERED_LIST:
            children.append(ordered_list_to_html_node(block))
        else:
            raise ValueError(f"Invalid block type: {block_type}")

    return ParentNode("div", children)


def paragraph_to_html_node(block):
    text = " ".join(block.split("\n"))
    return ParentNode("p", text_to_children(text))


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    text = block[level + 1 :]
    return ParentNode(f"h{level}", text_to_children(text))


def code_to_html_node(block):
    text = block[4:-3]
    code_node = text_node_to_html_node(TextNode(text, TextType.CODE))
    return ParentNode("pre", [code_node])


def quote_to_html_node(block):
    lines = block.split("\n")
    text = "\n".join(line[1:].lstrip(" ") for line in lines)
    return ParentNode("blockquote", text_to_children(text))


def unordered_list_to_html_node(block):
    lines = block.split("\n")
    list_items = [ParentNode("li", text_to_children(line[2:])) for line in lines]
    return ParentNode("ul", list_items)


def ordered_list_to_html_node(block):
    lines = block.split("\n")
    list_items = [
        ParentNode("li", text_to_children(line.split(". ", 1)[1])) for line in lines
    ]
    return ParentNode("ol", list_items)
