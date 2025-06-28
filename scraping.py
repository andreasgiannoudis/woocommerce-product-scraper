import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import re

# Directory to save product images
IMAGE_DIR = "product_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Price mapping for different pack sizes
PACK_PRICES = {
    "1-pack": "79",
    "5-pack": "349",
    "10-pack": "649"
}

# Clean filename
def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

# Get image URLs and download images
def download_product_images(soup, title):
    images = []

    # Main product image
    img_div = soup.find("div", class_="woocommerce-product-gallery__image")
    img_tag = img_div.find("img") if img_div else None
    if img_tag and img_tag.get("src"):
        img_url = img_tag["src"]
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        images.append(img_url)

    # Thumbnail images
    thumbnails_div = soup.find("div", class_="ast-single-product-thumbnails")
    if thumbnails_div:
        for img in thumbnails_div.find_all("img"):
            if img.get("src"):
                img_url = img["src"]
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                if img_url not in images:  # Avoid duplicates
                    images.append(img_url)

    # Download all images
    downloaded_files = []
    for i, img_url in enumerate(images):
        try:
            ext = os.path.splitext(img_url)[1].split("?")[0]
            if not ext:
                ext = ".jpg"

            filename = f"{slugify(title)}{'-'+str(i) if i > 0 else ''}{ext}"
            filepath = os.path.join(IMAGE_DIR, filename)

            img_data = requests.get(img_url, timeout=10).content
            with open(filepath, "wb") as f:
                f.write(img_data)
            print(f"📸 Image saved: {filename}")
            downloaded_files.append(filename)
        except Exception as e:
            print(f"⚠️ Failed to download image {i+1} for {title}: {e}")

    return downloaded_files

# Scrape title, description, and images
def scrape_product(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title_tag = soup.find("h1", class_="product_title")
        title = title_tag.get_text(strip=True) if title_tag else "Untitled Product"

        desc_tag = soup.find(class_="woocommerce-product-details__short-description")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        image_files = download_product_images(soup, title)

        return {
            "Name": title,
            "Description": description,
            "Images": ", ".join(image_files) if image_files else ""
        }

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return {
            "Name": "ERROR",
            "Description": "",
            "Images": ""
        }

# URLs to scrape
urls = [
    "https://example.com/product-name",
         
]

# CSV setup with WooCommerce-compatible field names
fieldnames = [
    "Type", "SKU", "Name", "Description", "Categories", "Images",
    "Regular price", "Attributes", "Parent",
    "Attribute 1 name", "Attribute 1 value(s)",
    "Attribute 1 visible", "Attribute 1 is used for variations"
]

pack_sizes = list(PACK_PRICES.keys())
sku_start = 1146  # Starting SKU

with open("products.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for idx, url in enumerate(urls, start=1):
        print(f"\n🔍 Scraping ({idx}/{len(urls)}): {url}")
        product = scrape_product(url)
        base_name = product["Name"]
        sku = str(sku_start + idx - 1)

        # Write variable product row (parent)
        writer.writerow({
            "Type": "variable",
            "SKU": sku,
            "Name": base_name,
            "Description": product["Description"],
            "Categories": "Test_product",
            "Images": product["Images"],
            "Regular price": "",
            "Attributes": "Välj antal",
            "Parent": "",
            "Attribute 1 name": "Välj antal",
            "Attribute 1 value(s)": " | ".join(pack_sizes),
            "Attribute 1 visible": 1,
            "Attribute 1 is used for variations": 1
        })

        # Write variation rows
        for size in pack_sizes:
            writer.writerow({
                "Type": "variation",
                "SKU": "",
                "Name": f"{base_name} - {size}",
                "Description": "",
                "Categories": "",
                "Images": "",
                "Regular price": PACK_PRICES[size],
                "Attributes": "",
                "Parent": base_name,
                "Attribute 1 name": "Välj antal",
                "Attribute 1 value(s)": size,
                "Attribute 1 visible": 1,
                "Attribute 1 is used for variations": 1
            })

        time.sleep(1)  # prevent rate-limiting

print("\n✅ All products scraped and saved to products.csv")
print(f"🖼️ Images downloaded to: {IMAGE_DIR}/")
