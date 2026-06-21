import unittest

from main import extract_title
from markdown_blocks import (
    BlockType,
    block_to_block_type,
    markdown_to_blocks,
    markdown_to_html_node,
)


class TestMarkdownBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_removes_empty_blocks(self):
        md = """

# Heading


Paragraph text



- List item

"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["# Heading", "Paragraph text", "- List item"])

    def test_markdown_to_blocks_strips_whitespace(self):
        md = "   # Heading   \n\n  Paragraph text  \n\n\t- List item\t"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["# Heading", "Paragraph text", "- List item"])

    def test_markdown_to_blocks_empty_string(self):
        blocks = markdown_to_blocks("")
        self.assertEqual(blocks, [])

    def test_block_to_block_type_paragraph(self):
        block = "This is a paragraph\nwith text on another line."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_heading(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Small heading"), BlockType.HEADING)

    def test_block_to_block_type_heading_requires_space(self):
        self.assertEqual(block_to_block_type("#Heading"), BlockType.PARAGRAPH)

    def test_block_to_block_type_heading_allows_only_six_hashes(self):
        self.assertEqual(block_to_block_type("####### Too many"), BlockType.PARAGRAPH)

    def test_block_to_block_type_code(self):
        block = "```\nprint('hello')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_block_to_block_type_code_requires_opening_newline(self):
        block = "```print('hello')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_code_requires_closing_backticks(self):
        block = "```\nprint('hello')"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote(self):
        block = ">This is a quote\n> and this is still quoted\n>"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_quote_requires_every_line(self):
        block = ">This is a quote\nThis is not quoted"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_unordered_list(self):
        block = "- first item\n- second item\n- third item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_unordered_list_requires_space(self):
        block = "- first item\n-second item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list(self):
        block = "1. first item\n2. second item\n3. third item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ordered_list_requires_start_at_one(self):
        block = "2. first item\n3. second item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_requires_incrementing_numbers(self):
        block = "1. first item\n3. second item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_requires_space(self):
        block = "1. first item\n2.second item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_markdown_to_html_node_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_markdown_to_html_node_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_markdown_to_html_node_heading(self):
        md = "### Heading with `code`"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><h3>Heading with <code>code</code></h3></div>",
        )

    def test_markdown_to_html_node_quote(self):
        md = ">Quote with **bold**\n>and _italic_"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><blockquote>Quote with <b>bold</b>\nand <i>italic</i></blockquote></div>",
        )

    def test_markdown_to_html_node_unordered_list(self):
        md = "- **bold** item\n- plain item\n- `code` item"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ul><li><b>bold</b> item</li><li>plain item</li><li><code>code</code> item</li></ul></div>",
        )

    def test_markdown_to_html_node_ordered_list(self):
        md = "1. first item\n2. _second_ item\n3. third item"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ol><li>first item</li><li><i>second</i> item</li><li>third item</li></ol></div>",
        )

    def test_markdown_to_html_node_mixed_blocks(self):
        md = """
# Title

Intro paragraph

- one
- two
"""
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><h1>Title</h1><p>Intro paragraph</p><ul><li>one</li><li>two</li></ul></div>",
        )

    def test_markdown_to_html_node_empty_document(self):
        node = markdown_to_html_node("")
        self.assertEqual(node.to_html(), "<div></div>")

    def test_extract_title(self):
        markdown = "# Hello\n\nThis is text."
        self.assertEqual(extract_title(markdown), "Hello")

    def test_extract_title_strips_whitespace(self):
        markdown = "#      Hello world     \n\nThis is text."
        self.assertEqual(extract_title(markdown), "Hello world")

    def test_extract_title_ignores_other_headings(self):
        markdown = "## Not an h1\n\n# Real title\n\n### Also not h1"
        self.assertEqual(extract_title(markdown), "Real title")

    def test_extract_title_raises_without_h1(self):
        markdown = "## Not an h1\n\nParagraph"
        with self.assertRaises(Exception):
            extract_title(markdown)


if __name__ == "__main__":
    unittest.main()
