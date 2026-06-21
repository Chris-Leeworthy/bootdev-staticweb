import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_none(self):
        node = HTMLNode(tag="a", value="Link", props=None)
        self.assertEqual(node.props_to_html(), "")

    def test_props_empty(self):
        node = HTMLNode(tag="a", value="Link", props={})
        self.assertEqual(node.props_to_html(), "")

    def test_props_multiple(self):
        props = {"href": "https://www.google.com", "target": "_blank"}
        node = HTMLNode(tag="a", value="Google", props=props)
        self.assertEqual(
            node.props_to_html(), ' href="https://www.google.com" target="_blank"'
        )

    def test_to_html_not_implemented(self):
        node = HTMLNode(tag="p", value="Hello")
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_repr(self):
        child = HTMLNode(tag="span", value="child")
        node = HTMLNode(tag="div", children=[child], props={"class": "wrapper"})
        rep = repr(node)
        # Basic checks to ensure we can see key fields
        self.assertIn("HTMLNode(", rep)
        self.assertIn("div", rep)
        self.assertIn("wrapper", rep)

    def test_leaf_to_html_paragraph(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_anchor_with_props(self):
        props = {"href": "https://www.boot.dev", "target": "_blank"}
        node = LeafNode("a", "Boot.dev", props)
        self.assertEqual(
            node.to_html(),
            '<a href="https://www.boot.dev" target="_blank">Boot.dev</a>',
        )

    def test_leaf_to_html_bold(self):
        node = LeafNode("b", "Bold text")
        self.assertEqual(node.to_html(), "<b>Bold text</b>")

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Plain text")
        self.assertEqual(node.to_html(), "Plain text")

    def test_parent_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_parent_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_parent_to_html_multiple_mixed_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_parent_to_html_with_props(self):
        child_node = LeafNode(None, "content")
        parent_node = ParentNode("div", [child_node], {"class": "content"})
        self.assertEqual(parent_node.to_html(), '<div class="content">content</div>')

    def test_parent_to_html_no_tag_raises(self):
        node = ParentNode(None, [LeafNode("span", "child")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_parent_to_html_missing_children_raises(self):
        node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_parent_to_html_no_children(self):
        node = ParentNode("div", [])
        self.assertEqual(node.to_html(), "<div></div>")


if __name__ == "__main__":
    unittest.main()
