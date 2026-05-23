import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import re

print("Loading local HTML file...")

with open("99acres_raw.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, 'html.parser')

# 1. ADVANCED EXTRACTION: Look for ALL the different class names 99acres uses
class_variations = ['tupleNew__tupleWrap', 'tupleNew__tupleWrapTopaz', 'PseudoTupleRevamp__tupleWrapProject']
listings = soup.find_all('div', class_=class_variations)

print(f"Found {len(listings)} property cards!\n")

parsed_properties = []

for card in listings:
    try:
        # Since classes change, we use a broader search to grab the text
        title_tag = card.find('h2')
        title = title_tag.text.strip() if title_tag else "Unknown"

        # Search for either the standard price class OR the premium price class
        price_tag = card.find('div', class_='tupleNew__priceValWrap') or card.find('div', class_='configs__ccl2')
        price = price_tag.text.strip() if price_tag else "0"

        size_tag = card.find('span', class_='tupleNew__area1Type') or card.find('div', class_='configs__ccl1')
        size = size_tag.text.strip() if size_tag else "0"

        # Skip useless data
        if "Price on Request" in price or price == "0":
            continue

        parsed_properties.append({
            'Title': title,
            'Price_Raw': price,
            'Size_Raw': size
        })
    except Exception:
        continue

df = pd.DataFrame(parsed_properties)
print("--- Raw Data ---")
print(df.head())

# ==========================================
# 2. PANDAS DATA CLEANING (Handling Ranges)
# ==========================================

def clean_size(size_str):
    # 1. Defensive Check: Does this string even contain digits?
    # If it doesn't contain a number, it's probably not a size, so return 0
    if not any(char.isdigit() for char in size_str):
        return 0.0

    # 2. Clean the string
    clean_str = size_str.replace('sqft', '').replace('sq. ft.', '').replace(',', '').strip()
    
    # 3. Handle Ranges
    if '-' in clean_str:
        try:
            parts = clean_str.split('-')
            # Extract digits only, in case there's leftover text like "sqft"
            val1 = ''.join(filter(str.isdigit, parts[0]))
            val2 = ''.join(filter(str.isdigit, parts[1]))
            return (float(val1) + float(val2)) / 2
        except:
            return 0.0
            
    # 4. Handle single values (e.g., "2,121")
    try:
        val = ''.join(filter(str.isdigit, clean_str))
        return float(val) if val else 0.0
    except:
        return 0.0

def clean_price(price_str):
    # 1. Defensive Check
    if not price_str or "Request" in price_str:
        return 0.0
    
    # 2. Extract all numbers (including decimals) using Regex
    # This finds patterns like "72.99" or "74.73"
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", price_str)
    
    if not numbers:
        return 0.0
    
    # Convert found numbers to floats
    values = [float(n) for n in numbers]
    avg_val = sum(values) / len(values)
    
    # 3. Determine Multiplier (Cr = 10^7, L/Lac = 10^5)
    # Check if 'Cr' is in the original string, else assume Lakh
    if 'Cr' in price_str:
        return avg_val * 10000000
    else:
        return avg_val * 100000

# Update your existing apply line:
df['Price_Clean'] = df['Price_Raw'].apply(clean_price)

print("\nCleaning data...")
df['Size_Clean'] = df['Size_Raw'].apply(clean_size)
df['Price_Clean'] = df['Price_Raw'].apply(clean_price)

print("--- Cleaned Data ---")
print(df[['Title', 'Size_Clean', 'Price_Clean']].head())

# ==========================================
# 3. VISUALIZATION
# ==========================================

print("\nGenerating scatter plot...")
plt.figure(figsize=(10, 6))

# X-axis is Size, Y-axis is Price
plt.scatter(df['Size_Clean'], df['Price_Clean'], color='blue', alpha=0.6, edgecolors='black')

plt.title('Ahmedabad Real Estate: Size vs. Price', fontsize=16, fontweight='bold')
plt.xlabel('Size (Square Feet)', fontsize=12)
plt.ylabel('Price in INR (₹)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)

# 1. Price Per Sqft
df['Price_Per_Sqft'] = df['Price_Clean'] / df['Size_Clean']

# 2. Top 3 Expensive Localities
top_expensive = df.groupby('Location')['Price_Clean'].mean().sort_values(ascending=False).head(3)
print("\n--- Most Expensive Localities ---")
print(top_expensive)

# 3. Best Value Deals (Lowest price per sqft)
best_value = df.sort_values(by='Price_Per_Sqft').head(3)
print("\n--- Best Value Deals ---")
print(best_value[['Title', 'Price_Per_Sqft']])

# Save the chart
plt.savefig('ahmedabad_real_estate.png', bbox_inches='tight')
print("Success! Check your folder for 'ahmedabad_real_estate.png'.")