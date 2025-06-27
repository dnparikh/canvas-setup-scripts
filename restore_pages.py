import os
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from slugify import slugify

# 🔐 Load credentials from .env
load_dotenv()

API_URL = os.getenv("CANVAS_API_URL")
ACCESS_TOKEN = os.getenv("CANVAS_ACCESS_TOKEN")
COURSE_ID = int(os.getenv("COURSE_ID"))

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}


def split_merged_html(file_path):
    """Split the merged HTML file into (title, body) page chunks."""
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    pages = []
    page_titles = soup.find_all("h1")
    
    for i, header in enumerate(page_titles):
        title = header.get_text()
        slug = slugify(title)

        # Define the content as all tags between this <h1> and the next <h1>
        content = ""
        current = header.next_sibling
        while current and (not current.name == "h1"):
            content += str(current)
            current = current.next_sibling

        pages.append({
            "title": title.strip(),
            "slug": slug,
            "body": content.strip()
        })

    return pages


def create_or_update_page(course_id, page):
    """Create or update a Canvas wiki page by slug."""
    url = f"{API_URL}/courses/{course_id}/pages/{page['slug']}"
    payload = {
        "wiki_page": {
            "title": page["title"],
            "body": page["body"],
            "published": True
        }
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"✅ Updated: {page['title']}")
    elif response.status_code == 404:
        # If page does not exist, create it
        post_url = f"{API_URL}/courses/{course_id}/pages"
        post_payload = {
            "wiki_page": {
                "title": page["title"],
                "body": page["body"],
                "published": True
            }
        }
        post_response = requests.post(post_url, headers=HEADERS, json=post_payload)
        if post_response.status_code == 201:
            print(f"🆕 Created: {page['title']}")
        else:
            print(f"❌ Failed to create: {page['title']}")
            print(post_response.text)
    else:
        print(f"❌ Error updating: {page['title']}")
        print(response.text)


def main():
    html_path = input("Enter the path to the merged HTML file: ").strip()
    if not os.path.exists(html_path):
        print("❌ File not found.")
        return

    print("🔍 Splitting merged HTML...")
    pages = split_merged_html(html_path)

    print(f"🔧 Restoring {len(pages)} page(s)...")
    for page in pages:
        create_or_update_page(COURSE_ID, page)


if __name__ == "__main__":
    main()

