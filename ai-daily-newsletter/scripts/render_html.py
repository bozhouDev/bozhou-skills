#!/usr/bin/env python3
"""将 AI 日报 Markdown 渲染为 Newsletter 风格 HTML，可选截图。"""

import argparse
import sys
from pathlib import Path

import markdown


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Serif+SC:wght@400;600;700;900&display=swap');

:root {
    --bg-page: #F7F7F5;
    --bg-paper: #FFFFFF;
    --text-main: #111111;
    --text-muted: #555555;
    --text-light: #999999;
    --accent: #D93025; /* Sharp editorial red */
    --border-divider: #E5E5E5;
    --border-strong: #111111;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Noto Serif SC', "PingFang SC", serif;
    background: var(--bg-page);
    color: var(--text-main);
    line-height: 1.8;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    padding: 40px 20px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: var(--bg-paper);
    padding: 80px 60px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.05);
    position: relative;
}

.container::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 6px;
    background: var(--text-main);
}

/* Header */
.newsletter-header {
    text-align: center;
    padding-bottom: 50px;
    margin-bottom: 50px;
    border-bottom: 2px solid var(--border-strong);
}

.newsletter-header h1 {
    font-family: 'Noto Serif SC', serif;
    font-weight: 900;
    font-size: 42px;
    line-height: 1.2;
    color: var(--text-main);
    margin-bottom: 20px;
    letter-spacing: -0.02em;
}

.newsletter-header blockquote {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    font-style: normal;
    font-weight: 500;
}

/* Body */
.newsletter-body {
    font-size: 16px;
}

/* Section Headings */
.newsletter-body h2 {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--accent);
    margin: 60px 0 30px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-divider);
}

.newsletter-body h2:first-child {
    margin-top: 0;
}

/* Article Titles */
.newsletter-body h3 {
    font-family: 'Noto Serif SC', serif;
    font-size: 20px;
    font-weight: 700;
    margin: 40px 0 16px;
    line-height: 1.5;
    color: var(--text-main);
}

.newsletter-body p {
    margin-bottom: 20px;
    color: #222222;
    text-align: justify;
}

/* Links */
.newsletter-body a {
    color: var(--text-main);
    text-decoration: none;
    border-bottom: 1px solid #CCCCCC;
    transition: all 0.2s ease;
}

.newsletter-body a:hover {
    color: var(--accent);
    border-bottom-color: var(--accent);
}

/* Lists */
.newsletter-body ul, .newsletter-body ol {
    margin-bottom: 30px;
    padding-left: 0;
    list-style: none;
}

.newsletter-body > ul > li {
    position: relative;
    padding-left: 24px;
    margin-bottom: 24px;
}

.newsletter-body > ul > li::before {
    content: "■";
    position: absolute;
    left: 0;
    top: 6px;
    font-size: 10px;
    color: var(--accent);
}

.newsletter-body li ul {
    margin-top: 12px;
    margin-bottom: 0;
    padding-left: 0;
}

.newsletter-body li li {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: var(--text-muted);
    margin-bottom: 8px;
    padding-left: 20px;
    position: relative;
    line-height: 1.6;
}

.newsletter-body li li::before {
    content: "→";
    position: absolute;
    left: 0;
    color: #AAAAAA;
    font-family: monospace;
}

/* Bold/Strong */
.newsletter-body strong {
    font-weight: 700;
    color: var(--text-main);
}

/* Blockquote in body */
.newsletter-body blockquote {
    margin: 30px 0;
    padding: 20px 30px;
    background: #FAFAFA;
    border-left: 3px solid var(--accent);
    font-size: 16px;
    font-family: 'Noto Serif SC', serif;
    color: var(--text-main);
    font-style: italic;
    line-height: 1.8;
}

/* Code */
.newsletter-body code {
    font-family: 'SF Mono', 'Consolas', monospace;
    font-size: 13px;
    background: #F5F5F5;
    padding: 3px 6px;
    border-radius: 2px;
    color: var(--accent);
    border: 1px solid #EAEAEA;
}

.newsletter-body pre {
    background: #111111;
    color: #E5E5E5;
    padding: 20px 24px;
    border-radius: 4px;
    overflow-x: auto;
    margin: 24px 0;
}

.newsletter-body pre code {
    background: none;
    padding: 0;
    border: none;
    color: inherit;
}

/* Horizontal rules */
.newsletter-body hr {
    border: none;
    height: 1px;
    background: var(--border-divider);
    margin: 40px 0;
}

/* Footer */
.newsletter-footer {
    margin-top: 80px;
    padding-top: 30px;
    border-top: 1px solid var(--border-divider);
    text-align: center;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-light);
}

/* Responsive */
@media (max-width: 700px) {
    body { padding: 0; background: var(--bg-paper); }
    .container { padding: 40px 24px; box-shadow: none; }
    .newsletter-header h1 { font-size: 32px; }
}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<div class="container">
{header}
<div class="newsletter-body">
{body}
</div>
{footer}
</div>
</body>
</html>
"""


def split_content(html: str) -> tuple[str, str, str]:
    """从转换后的 HTML 中提取 header（h1 + blockquote）、body 和 footer。"""
    lines = html.split("\n")
    header_parts = []
    footer_parts = []
    body_lines = []

    # 提取开头的 h1 和紧跟的 blockquote 作为 header
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("<h1"):
            header_parts.append(lines[i])
            i += 1
            # 找紧跟的 blockquote
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    i += 1
                    continue
                if s.startswith("<blockquote"):
                    header_parts.append(lines[i])
                    i += 1
                break
            break
        else:
            break

    # 跳过 header 后第一个 hr
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped == "<hr>" or stripped == "<hr />":
            i += 1
            break
        break

    # 寻找最后的「统计」行作为 footer
    # 从尾部反向查找包含"统计"或"源"的段落
    j = len(lines) - 1
    while j > i:
        stripped = lines[j].strip()
        if not stripped:
            j -= 1
            continue
        if "统计" in stripped or ("源" in stripped and "生成于" in stripped):
            footer_parts.append(lines[j])
            j -= 1
            # 跳过 footer 前的 hr
            while j > i:
                s = lines[j].strip()
                if not s:
                    j -= 1
                    continue
                if s == "<hr>" or s == "<hr />":
                    j -= 1
                break
            break
        break

    body_lines = lines[i : j + 1]

    header_html = (
        '<div class="newsletter-header">\n' + "\n".join(header_parts) + "\n</div>"
        if header_parts
        else ""
    )
    footer_html = (
        '<div class="newsletter-footer">\n'
        + "\n".join(l.replace("<p>", "").replace("</p>", "") for l in footer_parts)
        + "\n</div>"
        if footer_parts
        else ""
    )
    body_html = "\n".join(body_lines).strip()

    return header_html, body_html, footer_html


_LINK_ONLY_LINE = re.compile(
    r"^\s*-\s+"                          # 列表项前缀
    r"(\[.+?\]\([^)]*\)\s*[|｜]?\s*)+"  # 一个或多个 [文字](url)，可用 | 分隔
    r"\s*$"
)


def strip_links(md_text: str) -> str:
    """删除 markdown 中纯链接的列表行（如 '  - [原文链接](url)'）。"""
    filtered = [line for line in md_text.splitlines() if not _LINK_ONLY_LINE.match(line)]
    return "\n".join(filtered)


def render(md_path: Path) -> Path:
    """读取 markdown 并生成 HTML 文件，返回 HTML 文件路径。"""
    md_text = md_path.read_text(encoding="utf-8")
    md_text = strip_links(md_text)

    # 提取标题用于 <title>
    title = "AI 日报"
    for line in md_text.splitlines():
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
            break

    html_content = markdown.markdown(md_text, extensions=["extra", "sane_lists"])
    header, body, footer = split_content(html_content)

    full_html = HTML_TEMPLATE.format(
        title=title,
        css=CSS,
        header=header,
        body=body,
        footer=footer,
    )

    out_path = md_path.with_suffix(".html")
    out_path.write_text(full_html, encoding="utf-8")
    print(f"HTML 已生成: {out_path}")
    return out_path


def screenshot(html_path: Path) -> Path:
    """用 Playwright 截取 HTML 全页截图，返回 PNG 路径。"""
    from playwright.sync_api import sync_playwright

    png_path = html_path.with_suffix(".png")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 800, "height": 600}, device_scale_factor=2)
        page.goto(html_path.resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(png_path), full_page=True)
        browser.close()

    print(f"截图已生成: {png_path}")
    return png_path


def split_image(png_path: Path, max_height: int) -> list[Path]:
    """将长图按 max_height 切割成多张，返回切割后的路径列表。"""
    from PIL import Image

    img = Image.open(png_path)
    width, total_height = img.size

    if total_height <= max_height:
        print(f"图片高度 {total_height}px ≤ {max_height}px，无需切割")
        return [png_path]

    parts = []
    part_num = 1
    top = 0
    stem = png_path.stem

    while top < total_height:
        bottom = min(top + max_height, total_height)
        cropped = img.crop((0, top, width, bottom))
        out_path = png_path.parent / f"{stem}-{part_num}.png"
        cropped.save(out_path)
        parts.append(out_path)
        print(f"切割第 {part_num} 张: {out_path}  ({bottom - top}px)")
        top = bottom
        part_num += 1

    # 删除原始长图
    png_path.unlink()
    print(f"共切割为 {len(parts)} 张图片")
    return parts


def screenshot_by_section(html_path: Path) -> list[Path]:
    """按 h2 分节截图，每节一张图片，返回路径列表。"""
    import io
    from PIL import Image
    from playwright.sync_api import sync_playwright

    DPR = 2
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 800, "height": 600}, device_scale_factor=DPR)
        page.goto(html_path.resolve().as_uri())
        page.wait_for_load_state("networkidle")

        full_page_height = page.evaluate("document.body.scrollHeight")

        # 获取所有 h2 的文字和距页面顶部的 y 坐标
        sections = page.evaluate("""() => {
            const h2s = document.querySelectorAll('.newsletter-body h2');
            return Array.from(h2s).map(el => ({
                text: el.textContent.trim(),
                top: el.getBoundingClientRect().top + window.scrollY
            }));
        }""")

        png_bytes = page.screenshot(full_page=True)
        browser.close()

    img = Image.open(io.BytesIO(png_bytes))
    width, total_height = img.size
    stem = html_path.stem
    out_paths = []

    for i, section in enumerate(sections):
        top_page = section["top"]
        bottom_page = sections[i + 1]["top"] if i + 1 < len(sections) else full_page_height

        top_px = int(top_page * DPR)
        bottom_px = min(int(bottom_page * DPR), total_height)

        cropped = img.crop((0, top_px, width, bottom_px))

        # 用分类名称作为文件名（去掉 emoji 前缀里的不可打印字符）
        safe_name = "".join(c for c in section["text"] if c.isalnum() or c in " _-")
        safe_name = safe_name.strip()[:20].strip()
        out_path = html_path.parent / f"{stem}-{i + 1:02d}-{safe_name}.png"
        cropped.save(out_path)
        out_paths.append(out_path)
        print(f"  [{i + 1}] {section['text']} → {out_path.name}")

    print(f"共生成 {len(out_paths)} 张分节图片")
    return out_paths


def main():
    parser = argparse.ArgumentParser(description="AI 日报 Markdown → HTML 渲染器")
    parser.add_argument("markdown_file", type=Path, help="输入的 Markdown 文件路径")
    parser.add_argument(
        "--screenshot", action="store_true", help="生成全页 PNG 截图"
    )
    parser.add_argument(
        "--split-height", type=int, default=0,
        help="截图后按指定高度（px）切割为多张，0 表示不切割（默认 0）"
    )
    parser.add_argument(
        "--split-by-section", action="store_true",
        help="按 h2 分类截图，每个分类一张图片"
    )
    args = parser.parse_args()

    if not args.markdown_file.exists():
        print(f"错误: 文件不存在 {args.markdown_file}", file=sys.stderr)
        sys.exit(1)

    html_path = render(args.markdown_file)

    if args.screenshot:
        if args.split_by_section:
            screenshot_by_section(html_path)
        else:
            png_path = screenshot(html_path)
            if args.split_height > 0:
                split_image(png_path, args.split_height)


if __name__ == "__main__":
    main()
