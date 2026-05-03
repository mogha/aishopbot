import streamlit as st
import pandas as pd
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
from thefuzz import process # NEW: Import the fuzzy matching library

# 1. Page Setup
st.set_page_config(page_title="Inventory Bot", page_icon="📦")
st.title("📦 Voice Inventory Bot")
st.write("Tap the microphone to speak, or type your search below.")

# 2. Load the Data
@st.cache_data(ttl=5) # Refreshes every 5 seconds to catch inventory updates
def load_inventory():
    try:
        df = pd.read_csv('inventory.csv')
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        return None

df = load_inventory()

if df is None:
    st.error("Error: I could not find 'inventory.csv' in this folder.")
else:
    # 3. Voice Input Button
    spoken_text = speech_to_text(
        language='en',
        start_prompt="🎙️ Tap to Speak",
        stop_prompt="🛑 Stop Recording",
        just_once=True,
        key='STT'
    )

    # 4. Text Input (Fallback)
    typed_text = st.text_input("Or type the product name here:")

    # Decide which input to use
    user_input = spoken_text if spoken_text else typed_text

    # 5. Search & Respond Logic (UPDATED FOR FUZZY MATCHING)
    if user_input:
        st.write(f"**You searched for:** {user_input}")
        
        # Get a list of all product names from the CSV
        product_list = df['Product'].astype(str).tolist()
        
        # Find the single best fuzzy match and its score (0 to 100)
        best_match, score = process.extractOne(user_input, product_list)
        
        # We set the threshold to 70. 
        # (You can lower this if it's too strict, or raise it if it's matching the wrong items)
        if score >= 70:
            # Let the user know if we auto-corrected their typo
            if best_match.lower() != user_input.lower():
                st.info(f"💡 Assuming you meant: **{best_match}** (Match Confidence: {score}%)")

            # Get the exact row for the matched product
            match_row = df[df['Product'] == best_match].iloc[0]
            
            product_name = str(match_row['Product'])
            qty = int(match_row['Qty']) 
            rack = str(match_row['Rack'])
            shelf = str(match_row['Shelf'])
            
            response = f"Yes, we have {qty} {product_name} in stock. You can find them on Rack {rack}, Shelf {shelf}."
            st.success(response)
            
        else:
            response = f"Sorry, I couldn't find anything sounding like {user_input} in the inventory."
            st.warning(response)
            
        # Generate and Play the Audio Answer
        tts = gTTS(text=response, lang='en')
        tts.save("response.mp3")
        st.audio("response.mp3", format="audio/mp3", autoplay=True)
