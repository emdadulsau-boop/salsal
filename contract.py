import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. Connection ---
conn = st.connection("gsheets", type=GSheetsConnection)

def log_to_sheet(name, job, location):
    try:
        # Use the name of the tab at the bottom of your sheet
        sheet_name = "Sheet1" 
        
        # Read existing data to append to it
        existing_data = conn.read(worksheet=sheet_name, ttl=0)
        
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Client Name": name,
            "Job": job,
            "Location": location
        }])
        
        updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
        conn.update(worksheet=sheet_name, data=updated_df)
        st.toast("🚀 Logged to Google Sheets!")
    except Exception as e:
        st.error(f"Sheet Error: {e}")

# --- 2. PDF Generation ---
def generate_contract(name, place, building, contact, date1, date2, job, sig_file, sx, sy):
    # Use relative paths for GitHub (upload these images to your repo)
    p1 = Image.open("temp.png").convert("RGB")
    p2 = Image.open("temp2.png").convert("RGB")
    
    draw1 = ImageDraw.Draw(p1)
    draw2 = ImageDraw.Draw(p2)
    
    # Ensure arial.ttf is uploaded to your GitHub repo!
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    # Draw Page 1
    draw1.text((143, 619), name, fill="black", font=font)
    draw1.text((143, 649), place, fill="black", font=font)
    draw1.text((619, 652), building, fill="black", font=font)
    draw1.text((619, 682), contact, fill="black", font=font)
    draw1.text((403, 185), date1, fill="black", font=font)
    draw1.text((577, 185), date2, fill="black", font=font)
    draw1.text((259, 542), job, fill="black", font=font)

    # Draw Page 2
    draw2.text((143, 100), f"Contract Start Date: {date1}", fill="black", font=font)

    if sig_file:
        sig = Image.open(sig_file).convert("RGBA")
        sig = sig.resize((200, 80))
        p1.paste(sig, (sx, sy), sig)
        
    return p1, p2

# --- 3. UI ---
st.title("📜 Contract Automator")

# Inputs
name_in = st.text_input("Client Name")
job_in = st.text_input("Job")
loc_in = st.text_input("Location")
# ... add your other inputs (date1, date2, etc) here ...

sig_up = st.file_uploader("Sign Here", type=['png', 'jpg'])
sx = st.number_input("Sig X", value=450)
sy = st.number_input("Sig Y", value=1000)

if st.button("Finish & Log"):
    # (Assuming all other date/contact variables are defined)
    p1, p2 = generate_contract(name_in, loc_in, "Bldg", "017...", "2026-03-17", "2027-03-17", job_in, sig_up, sx, sy)
    
    # 1. Log to Sheet
    log_to_sheet(name_in, job_in, loc_in)
    
    # 2. PDF Download
    buf = io.BytesIO()
    p1.save(buf, format="PDF", save_all=True, append_images=[p2])
    st.download_button("💾 Download Contract", buf.getvalue(), f"{name_in}.pdf")
