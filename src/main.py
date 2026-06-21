import os
import shutil

from markdown_blocks import markdown_to_html_node


def copy_static(source_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    for item in sorted(os.listdir(source_dir)):
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)

        if os.path.isfile(source_path):
            print(f"Copying {source_path} -> {dest_path}")
            shutil.copy(source_path, dest_path)
        else:
            copy_static(source_path, dest_path)


def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("No h1 header found")


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path) as markdown_file:
        markdown = markdown_file.read()

    with open(template_path) as template_file:
        template = template_file.read()

    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    page = template.replace("{{ Title }}", title).replace("{{ Content }}", html)

    dest_dir = os.path.dirname(dest_path)
    if dest_dir != "":
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w") as dest_file:
        dest_file.write(page)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for item in sorted(os.listdir(dir_path_content)):
        source_path = os.path.join(dir_path_content, item)
        dest_path = os.path.join(dest_dir_path, item)

        if os.path.isfile(source_path):
            if source_path.endswith(".md"):
                html_dest_path = dest_path[:-3] + ".html"
                generate_page(source_path, template_path, html_dest_path)
        else:
            generate_pages_recursive(source_path, template_path, dest_path)


def main():
    source_dir = "static"
    dest_dir = "public"

    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    copy_static(source_dir, dest_dir)
    generate_pages_recursive("content", "template.html", dest_dir)


if __name__ == "__main__":
    main()
