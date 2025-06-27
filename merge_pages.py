import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

# 🔐 Load API config from .env
load_dotenv()

API_URL = os.getenv("CANVAS_API_URL")
ACCESS_TOKEN = os.getenv("CANVAS_ACCESS_TOKEN")
COURSE_ID = int(os.getenv("COURSE_ID"))

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}


def get_paginated(url):
    """Helper to retrieve paginated Canvas API results."""
    results = []
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        results.extend(response.json())
        url = None
        if 'Link' in response.headers:
            links = requests.utils.parse_header_links(response.headers['Link'].rstrip('>').replace('>,', '>,'))            
            for link in links:
                if link.get('rel') == 'next':
                    url = link.get('url')
    return results


def get_all_pages(course_id):
    """Get list of all wiki pages (title and URL slug)."""
    url = f"{API_URL}/courses/{course_id}/pages"
    return get_paginated(url)


def get_page_content(course_id, page_url):
    """Get the full HTML content of a single wiki page."""
    url = f"{API_URL}/courses/{course_id}/pages/{page_url}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def merge_pages_to_html(course_id, pages):
    """Merge all pages into one HTML file."""
    merged_html = ['<html><head><meta charset="utf-8"><title>Course Pages</title></head><body>']
    for i, page in enumerate(pages):
        slug = page["url"]
        title = page["title"]
        print(f"📄 Fetching: {title}")
        full_page = get_page_content(course_id, slug)
        merged_html.append(f"<h1>{title}</h1>")
        merged_html.append(full_page.get("body", "<p><em>No content</em></p>"))

    merged_html.append('</body></html>')
    return "\n".join(merged_html)


def save_html_file(content):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"merged_canvas_pages_{timestamp}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n✅ Merged HTML saved to: {filename}")


def main():
    print("🔍 Retrieving Canvas pages...")
    pages = get_all_pages(COURSE_ID)

    if not pages:
        print("❌ No pages found.")
        return

    html_content = merge_pages_to_html(COURSE_ID, pages)
    save_html_file(html_content)


if __name__ == "__main__":
    main()

