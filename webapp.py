import streamlit as st
import pandas as pd
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

# 1. Page Setup
st.set_page_config(page_title="Inventory Bot", page_icon="📦")
st.title("📦 Voice Inventory Bot")
st.write("Tap the microphone to speak, or type your search below.")

# 2. Load the Data
@st.cache_data
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
    # This creates a button that records audio and returns the transcribed text
    spoken_text = speech_to_text(
        language='en',
        start_prompt="🎙️ Tap to Speak",
        stop_prompt="🛑 Stop Recording",
        just_once=True,
        key='STT'
    )

    # 4. Text Input (Fallback)
    typed_text = st.text_input("Or type the product name here:")

    # Decide which input to use. If they spoke, use that. Otherwise, use what they typed.
    user_input = spoken_text if spoken_text else typed_text

    # 5. Search & Respond Logic
    if user_input:
        st.write(f"**Searching for:** {user_input}")
        
        match = df[df['Product'].str.contains(user_input, case=False, na=False)]
        
        if not match.empty:
            row = match.iloc[0] 
            product_name = str(row['Product'])
            qty = int(row['Qty']) 
            rack = str(row['Rack'])
            shelf = str(row['Shelf'])
            
            response = f"Yes, we have {qty} {product_name} in stock. You can find them on Rack {rack}, Shelf {shelf}."
            st.success(response)
        else:
            response = f"Sorry, I couldn't find {user_input} in the inventory."
            st.warning(response)
            
        # Generate and Play the Audio Answer
        tts = gTTS(text=response, lang='en')
        tts.save("response.mp3")
        st.audio("response.mp3", format="audio/mp3", autoplay=True)