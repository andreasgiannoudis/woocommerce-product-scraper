# 🛍️ WooCommerce Product Scraper

This Python script scrapes product information from specified product pages and generates a **WooCommerce-compatible CSV** along with downloading product images to a local folder.

## ✅ Features

- Scrapes product:
  - **Title**
  - **Short description**
  - **Main and thumbnail images**
- Downloads and saves all images to a local `product_images` folder
- Generates a structured **CSV file** (`products.csv`) with:
  - **Variable product**
  - **3 variations**: 1-pack, 5-pack, 10-pack
- Custom SKU generation starting from `1146`
- Pack pricing is defined in the script

---

## 📦 Output

- `products.csv`: WooCommerce-ready CSV
- `product_images/`: All downloaded product images saved here

---

## 🧰 Requirements

Make sure you have Python 3 installed.

Install dependencies using pip:

```bash
pip install requests beautifulsoup4
