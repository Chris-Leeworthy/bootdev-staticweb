import unittest

from textnode import (
    TextNode,
    TextType,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    text_node_to_html_node,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_equal_text_type(self):
        node1 = TextNode("Text", TextType.BOLD)
        node2 = TextNode("Text", TextType.ITALIC)
        self.assertNotEqual(node1, node2)

    def test_not_equal_url(self):
        node1 = TextNode("Example", TextType.LINK, url=None)
        node2 = TextNode("Example", TextType.LINK, url="http://example.com")
        self.assertNotEqual(node1, node2)

    def test_equal_with_url(self):
        node1 = TextNode("Example", TextType.LINK, url="http://example.com")
        node2 = TextNode("Example", TextType.LINK, url="http://example.com")
        self.assertEqual(node1, node2)

    def test_edge_empty_text(self):
        node1 = TextNode("", TextType.TEXT)
        node2 = TextNode("", TextType.TEXT)
        self.assertEqual(node1, node2)

    def test_text_node_to_html_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
        self.assertEqual(html_node.props, None)

    def test_text_node_to_html_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")
        self.assertEqual(html_node.props, None)

    def test_text_node_to_html_italic(self):
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")
        self.assertEqual(html_node.props, None)

    def test_text_node_to_html_code(self):
        node = TextNode("print('hello')", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('hello')")
        self.assertEqual(html_node.props, None)

    def test_text_node_to_html_link(self):
        node = TextNode("Boot.dev", TextType.LINK, "https://www.boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Boot.dev")
        self.assertEqual(html_node.props, {"href": "https://www.boot.dev"})

    def test_text_node_to_html_image(self):
        node = TextNode("Boot.dev logo", TextType.IMAGE, "https://www.boot.dev/logo.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props,
            {"src": "https://www.boot.dev/logo.png", "alt": "Boot.dev logo"},
        )

    def test_text_node_to_html_invalid_type(self):
        node = TextNode("Invalid", "not a text type")
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

    def test_split_nodes_delimiter_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_split_nodes_delimiter_bold(self):
        node = TextNode("This is text with a **bolded phrase** in the middle", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded phrase", TextType.BOLD),
                TextNode(" in the middle", TextType.TEXT),
            ],
        )

    def test_split_nodes_delimiter_italic(self):
        node = TextNode("This is text with an _italic phrase_ in the middle", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("italic phrase", TextType.ITALIC),
                TextNode(" in the middle", TextType.TEXT),
            ],
        )

    def test_split_nodes_delimiter_multiple_matches(self):
        node = TextNode("A **bold** word and **another** one", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("A ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" word and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
                TextNode(" one", TextType.TEXT),
            ],
        )

    def test_split_nodes_delimiter_preserves_non_text_nodes(self):
        old_nodes = [
            TextNode("Already bold", TextType.BOLD),
            TextNode(" and `code`", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(old_nodes, "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("Already bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("code", TextType.CODE),
            ],
        )

    def test_split_nodes_delimiter_no_delimiter(self):
        node = TextNode("This is plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [TextNode("This is plain text", TextType.TEXT)])

    def test_split_nodes_delimiter_only_delimited_text(self):
        node = TextNode("**bold only**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [TextNode("bold only", TextType.BOLD)])

    def test_split_nodes_delimiter_unmatched_delimiter_raises(self):
        node = TextNode("This has an unmatched ` delimiter", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        matches = extract_markdown_images(
            "This has ![rick roll](https://i.imgur.com/aKaOqIh.gif)"
            " and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            matches,
        )

    def test_extract_markdown_images_none(self):
        matches = extract_markdown_images(
            "This is text with [a link](https://www.boot.dev)"
        )
        self.assertListEqual([], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev)"
        )
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_extract_markdown_links_multiple(self):
        matches = extract_markdown_links(
            "This has [to boot dev](https://www.boot.dev)"
            " and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            matches,
        )

    def test_extract_markdown_links_excludes_images(self):
        matches = extract_markdown_links(
            "This has ![image](https://i.imgur.com/zjjcJKZ.png)"
            " and [a link](https://www.boot.dev)"
        )
        self.assertListEqual([("a link", "https://www.boot.dev")], matches)

    def test_extract_markdown_links_none(self):
        matches = extract_markdown_links("This is plain text with no links")
        self.assertListEqual([], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
            " and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_no_images(self):
        node = TextNode("This is text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_images_at_start_and_end(self):
        node = TextNode(
            "![first](https://example.com/first.png) middle "
            "![last](https://example.com/last.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("first", TextType.IMAGE, "https://example.com/first.png"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("last", TextType.IMAGE, "https://example.com/last.png"),
            ],
            new_nodes,
        )

    def test_split_images_preserves_non_text_nodes(self):
        old_nodes = [
            TextNode("Already bold", TextType.BOLD),
            TextNode(" ![image](https://example.com/image.png)", TextType.TEXT),
        ]
        new_nodes = split_nodes_image(old_nodes)
        self.assertListEqual(
            [
                TextNode("Already bold", TextType.BOLD),
                TextNode(" ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://example.com/image.png"),
            ],
            new_nodes,
        )

    def test_split_images_ignores_links(self):
        node = TextNode(
            "This has [a link](https://www.boot.dev) and ![image](https://img.com/a.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This has [a link](https://www.boot.dev) and ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://img.com/a.png"),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev)"
            " and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_split_links_no_links(self):
        node = TextNode("This is text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links_at_start_and_end(self):
        node = TextNode(
            "[first](https://example.com/first) middle [last](https://example.com/last)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("first", TextType.LINK, "https://example.com/first"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("last", TextType.LINK, "https://example.com/last"),
            ],
            new_nodes,
        )

    def test_split_links_preserves_non_text_nodes(self):
        old_nodes = [
            TextNode("Already italic", TextType.ITALIC),
            TextNode(" [link](https://example.com)", TextType.TEXT),
        ]
        new_nodes = split_nodes_link(old_nodes)
        self.assertListEqual(
            [
                TextNode("Already italic", TextType.ITALIC),
                TextNode(" ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_split_links_ignores_images(self):
        node = TextNode(
            "This has ![image](https://img.com/a.png) and [a link](https://www.boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This has ![image](https://img.com/a.png) and ", TextType.TEXT),
                TextNode("a link", TextType.LINK, "https://www.boot.dev"),
            ],
            new_nodes,
        )

    def test_text_to_textnodes(self):
        text = (
            "This is **text** with an _italic_ word and a `code block`"
            " and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg)"
            " and a [link](https://boot.dev)"
        )
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image",
                    TextType.IMAGE,
                    "https://i.imgur.com/fJRm4Vk.jpeg",
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_text_to_textnodes_plain_text(self):
        nodes = text_to_textnodes("This is plain text")
        self.assertListEqual([TextNode("This is plain text", TextType.TEXT)], nodes)

    def test_text_to_textnodes_multiple_inline_styles(self):
        nodes = text_to_textnodes("**bold** _italic_ `code`")
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" ", TextType.TEXT),
                TextNode("code", TextType.CODE),
            ],
            nodes,
        )

    def test_text_to_textnodes_images_and_links(self):
        nodes = text_to_textnodes(
            "![image](https://example.com/image.png) [link](https://example.com)"
        )
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://example.com/image.png"),
                TextNode(" ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
            nodes,
        )

if __name__ == "__main__":
    unittest.main()
