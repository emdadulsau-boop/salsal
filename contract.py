from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import io
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. Connection Setup ---
# In Streamlit Cloud, you'll add the URL to your .streamlit/secrets.toml
conn = st.connection("gsheets", type=GSheetsConnection)

def log_to_sheet(name, job, location):
    # Fetch existing data
    existing_data = conn.read(worksheet="Sheet1")
    
    # Create new row
    new_entry = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Client Name": name,
        "Job": job,
        "Location": location
    }])
    
    # Combine and update
    updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
    conn.update(worksheet="Sheet1", data=updated_df)

def generate_contract(name, place, building, contact, date1, date2, job, sig_file, sig_x, sig_y):
    # --- PAGE 1 ---
    page1 = Image.open("C:/Users/Tc/Desktop/temp.png").convert("RGB")
    draw1 = ImageDraw.Draw(page1)
    
    # --- PAGE 2 ---
    # Load your second image template here
    page2 = Image.open("C:/Users/Tc/Desktop/temp2.png").convert("RGB")
    draw2 = ImageDraw.Draw(page2)
    
    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Draw on Page 1
    draw1.text((143, 619), name, fill="black", font=font)
    draw1.text((143, 649), place, fill="black", font=font)
    draw1.text((619, 650), building, fill="black", font=font)
    draw1.text((619, 682), contact, fill="black", font=font)
    draw1.text((403, 185), date1, fill="black", font=font)
    draw1.text((577, 185), date2, fill="black", font=font)
    draw1.text((259, 542), job, fill="black", font=font)

    # Draw on Page 2 (Example: adding date1 to a specific spot on page 2)
    # Adjust these coordinates (x, y) for where date1 belongs on the second page
    draw2.text((457, 231), f"{date1}", fill="black", font=font)

    # Handle Signature on Page 1
    if sig_file:
        sig = Image.open(sig_file).convert("RGBA")
        sig = sig.resize((200, 80)) 
        page2.paste(sig, (sig_x, sig_y), sig) 
        
    return page1, page2

# --- Streamlit UI ---
st.title("📜 Multi-Page Contract Generator")

# (Input fields remain the same as previous step...)
col1, col2 = st.columns(2)
with col1:
    name_input = st.text_input("Client Name")
    place_input = st.text_input("Client Location")
    job_input = st.text_input("Work/Job")
    date1_input = st.text_input("Contract Start")
with col2:
    date2_input = st.text_input("Contract End")
    building_input = st.text_input("Building")
    contact_input = st.text_input("Contact No.")
    

sig_upload = st.file_uploader("Upload Signature", type=['png', 'jpg'])
sig_x = st.number_input("Signature X", value=450)
sig_y = st.number_input("Signature Y", value=1000)

if st.button("Generate 2-Page PDF"):
    p1, p2 = generate_contract(
        name_input, place_input, building_input, contact_input, 
        date1_input, date2_input, job_input, sig_upload, sig_x, sig_y
    )
    
    # Preview both pages in Streamlit
    st.image(p1, caption="Page 1 Preview", use_column_width=True)
    st.image(p2, caption="Page 2 Preview", use_column_width=True)
    
    # SAVE AS MULTI-PAGE PDF
    pdf_buffer = io.BytesIO()
    # Save p1, and append p2 to the list
    p1.save(pdf_buffer, format="PDF", save_all=True, append_images=[p2], resolution=100.0)
    
    st.download_button(
        label="Download Full Contract (2 Pages)",
        data=pdf_buffer.getvalue(),
        file_name=f"Contract_{name_input}.pdf",
        mime="application/pdf"
    )
    
    try:
        log_to_sheet(name_input, job_input, place_input)
        st.toast("🚀 Activity logged to Google Sheets!")
    except Exception as e:
        st.error("Sheet logging failed, but PDF is ready.")