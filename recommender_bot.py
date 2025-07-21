import pandas as pd
import re
import pyttsx3

# Voice engine setup
try:
    tts = pyttsx3.init()
    voices = tts.getProperty('voices')
    tts.setProperty('voice', voices[0].id)  # Try voices[1] or voices[-1] for female voice
    tts.setProperty('rate', 170)
except Exception as e:
    print("Voice engine error:", e)
    tts = None

def speak(text):
    print("🔊 Bot says:", text)
    if tts:
        try:
            tts.say(text)
            tts.runAndWait()
        except Exception as e:
            print("Voice error:", e)

# Ask for user's name
print("📝 Please enter your name:")
user_name = input("👤 You: ").strip().title()
speak(f"Welcome {user_name} to the Beauty Product Recommender!")

# Load dataset
df = pd.read_excel(r"D:\python\beauty-bot\beauty_products.xlsx", engine="openpyxl")
print("✅ Data loaded successfully.")

# Normalize text columns
df['Product_Name'] = df['Product_Name'].str.lower()
df['Category'] = df['Category'].str.lower()
df['Skin_Type'] = df['Skin_Type'].str.lower()
df['Main_Ingredient'] = df['Main_Ingredient'].str.lower()
df['Brand'] = df['Brand'].str.lower()

# Category keyword mapping
category_keywords = {
    "moisturizer": ["moisturizer", "moisturizing", "cream", "hydrating"],
    "serum": ["serum"],
    "cleanser": ["cleanser", "face wash", "wash", "cleansing"],
    "face mask": ["mask", "face mask"],
    "lipstick": ["lipstick", "lip color"],
    "foundation": ["foundation", "base"],
    "concealer": ["concealer"],
    "cc cream": ["cc cream", "color correcting"],
    "eye shadow": ["eye shadow", "eyeshadow"],
}

def detect_category(query):
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in query:
                return category
    return None

print("\n💄 Welcome to the Beauty Product Recommender!")
speak("Type your request, like moisturizer for dry skin with aloe vera. Or type exit to quit.")

# Store user preferences across queries
user_memory = {}

while True:
    query = input("\n👤 You: ").lower().strip()

    if query == "exit":
        speak(f"Goodbye {user_name}, stay beautiful!")
        break

    results = df.copy()
    filters = {}

    # Detect category
    found_category = detect_category(query)
    if found_category:
        filters["Category"] = found_category
        user_memory["Category"] = found_category
    elif "Category" in user_memory:
        filters["Category"] = user_memory["Category"]

    # Detect skin type
    matched_skin = None
    for skin in df["Skin_Type"].dropna().unique():
        if skin in query:
            matched_skin = skin
            filters["Skin_Type"] = skin
            user_memory["Skin_Type"] = skin
            break
    if not matched_skin and "Skin_Type" in user_memory:
        filters["Skin_Type"] = user_memory["Skin_Type"]

    # Detect main ingredient
    matched_ing = None
    for ing in df["Main_Ingredient"].dropna().unique():
        if ing in query:
            matched_ing = ing
            filters["Main_Ingredient"] = ing
            user_memory["Main_Ingredient"] = ing
            break
    if not matched_ing and "Main_Ingredient" in user_memory:
        filters["Main_Ingredient"] = user_memory["Main_Ingredient"]

    # Detect price
    price_match = re.search(r"\$(\d+)|under\s*\$?(\d+)", query)
    if price_match:
        price_val = price_match.group(1) or price_match.group(2)
        try:
            filters["Price_USD"] = float(price_val)
        except:
            pass

    # Apply filters
    if "Category" in filters:
        results = results[results["Category"].str.contains(filters["Category"], na=False)]
    if "Skin_Type" in filters:
        results = results[results["Skin_Type"].str.contains(filters["Skin_Type"], na=False)]
    if "Main_Ingredient" in filters:
        results = results[results["Main_Ingredient"].str.contains(filters["Main_Ingredient"], na=False)]
    if "Price_USD" in filters:
        results = results[results["Price_USD"] <= filters["Price_USD"]]

    # Optional: refine by product name
    if "Category" in filters and len(results) > 50:
        results = results[results["Product_Name"].str.contains(filters["Category"], na=False)]

    if not filters:
        speak("I couldn't understand your need. Try mentioning skin type, product type, or ingredient.")
        continue

    if results.empty:
        speak("No matching products found. Try a broader query.")
        continue

    print(f"\n🔎 Based on filters: {filters}")

    # Show top 3
    top = results.sort_values(by="Rating", ascending=False).head(3)

    print("\n💄 Top product matches:")
    for _, row in top.iterrows():
        message = f"""{row['Product_Name'].title()} by {row['Brand'].title()}.
Price ${row['Price_USD']}, Rating {row['Rating']}.
For {row['Skin_Type']} skin with {row['Main_Ingredient']}.
Recommended usage: {row['Usage_Frequency']}."""
        
        print("⭐", message)
        speak(f"{user_name}, here's a recommendation. {message}")
