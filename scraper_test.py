import pandas as pd
from bs4 import BeautifulSoup

# ==========================================
# PHASE 1: THE RAW DATA (The "Extract" Phase)
# ==========================================
mock_html_content = """
<html>
    <body>
        <div class="property-card">
            <h2 class="prop-title">3 BHK Luxury Apartment</h2>
            <span class="prop-price">₹1.25 Cr</span>
            <p class="prop-location">Vastrapur, Ahmedabad</p>
            <div class="prop-size">1850 sq ft</div>
        </div>
        <div class="property-card">
            <h2 class="prop-title">2 BHK Semi-Furnished Flat</h2>
            <span class="prop-price">₹75.0 Lakh</span>
            <p class="prop-location">Satellite, Ahmedabad</p>
            <div class="prop-size">1200 sq ft</div>
        </div>
        <div class="property-card">
            <h2 class="prop-title">4 BHK Ultra Villa</h2>
            <span class="prop-price">₹4.10 Cr</span>
            <p class="prop-location">Bodakdev, Ahmedabad</p>
            <div class="prop-size">3600 sq ft</div>
        </div>
    </body>
</html>
"""

# ==========================================
# PHASE 2: PARSING THE HTML
# ==========================================

# TEACHING MOMENT: What is 'html.parser'?
# BeautifulSoup needs to know WHAT kind of text we are giving it. 
# By passing 'html.parser', we are telling Python: "Read this string not as normal text, 
# but as a web page tree with parents and children tags."
soup = BeautifulSoup(mock_html_content, 'html.parser')

# TEACHING MOMENT: find_all()
# A website might have headers, footers, and ads. We ONLY want the property cards.
# soup.find_all() searches the entire HTML tree and grabs every single <div> 
# that has the exact class name 'property-card'. It puts them all into a list.
listings = soup.find_all('div', class_='property-card')

# We create an empty list (a bucket) to hold our clean dictionaries
parsed_properties = []

for card in listings:
    
    # TEACHING MOMENT: .find() vs .text vs .strip()
    # 1. card.find() searches ONLY inside the current property card, not the whole page.
    # 2. .text strips away the HTML tags (like <h2> and </h2>), leaving just the human words.
    # 3. .strip() is a Python string method that deletes any accidental spaces or "Enter" 
    #    newlines at the very beginning or end of the text. It prevents messy formatting.
    title = card.find('h2', class_='prop-title').text.strip()
    price = card.find('span', class_='prop-price').text.strip()
    location = card.find('p', class_='prop-location').text.strip()
    size = card.find('div', class_='prop-size').text.strip()
    
    # TEACHING MOMENT: The Dictionary and .append()
    # We take our 4 variables and pack them into a Dictionary (key-value pairs).
    # Then, we call .append() on our 'parsed_properties' list to drop this dictionary into the bucket.
    parsed_properties.append({
        'Title': title,
        'Price_Raw': price,
        'Location': location,
        'Size_Raw': size
    })

# ==========================================
# PHASE 3: PANDAS DATA CLEANING (The "Transform" Phase)
# ==========================================

# Convert our list of dictionaries into a 2D Pandas Table
df = pd.DataFrame(parsed_properties)

print("--- BEFORE CLEANING ---")
print(df)

# TEACHING MOMENT: Cleaning text with Pandas (.str)
# Right now, size is "1850 sq ft". We can't do math on letters.
# df['Size_Raw'].str gives Pandas permission to treat the whole column like a string.
# We replace " sq ft" with nothing (''), leaving just "1850".
# Finally, .astype(int) forces Python to recognize "1850" as a real math integer.
df['Size_Clean'] = df['Size_Raw'].str.replace(' sq ft', '').astype(int)


# TEACHING MOMENT: Custom Functions and .apply()
# Price is trickier because we have "Cr" and "Lakh". We need a custom rule.
# We build a function that takes one string (e.g., "₹1.25 Cr"), removes the "₹",
# checks if it says "Cr" or "Lakh", removes that word, and multiplies the number 
# by 10,000,000 (Cr) or 100,000 (Lakh) to get the true mathematical value.
def clean_indian_currency(price_string):
    # Remove the Rupee symbol and trim spaces
    clean_str = price_string.replace('₹', '').strip()
    
    if 'Cr' in clean_str:
        # Remove 'Cr', turn the text "1.25" into a float 1.25, and multiply
        number = float(clean_str.replace('Cr', '').strip())
        return number * 10000000
        
    elif 'Lakh' in clean_str:
        number = float(clean_str.replace('Lakh', '').strip())
        return number * 100000
        
    return 0

# TEACHING MOMENT: .apply()
# Instead of writing a slow 'for loop', .apply() grabs our custom function and 
# shoots it down the entire 'Price_Raw' column instantly, creating a new column.
df['Price_Clean'] = df['Price_Raw'].apply(clean_indian_currency)


print("\n--- AFTER CLEANING ---")
# We use [['Title', 'Price_Clean', 'Size_Clean']] to only view our new, clean math columns
print(df[['Title', 'Location', 'Price_Clean', 'Size_Clean']])