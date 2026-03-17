import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. Connection Setup ---
# This looks for credentials in the Streamlit Cloud "Secrets" tab
conn = st.connection("gsheets", type=GSheetsConnection)

def log_to_sheet(name, job, place):
    try:
        # 1. Fetch current data (ttl=0 ensures we don't use a cached version)
        sheet_name = "Sheet1"
        existing_data = conn.read(worksheet=sheet_name, ttl=0)
        
        # 2. Prepare the new row as a DataFrame
        new_entry = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Client Name": str(name),
            "Job": str(job),
            "Location": str(place)
        }])
        
        # 3. Append the new row to the existing data
        # ignore_index=True prevents duplicate row numbers
        updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
        
        # 4. Overwrite the sheet with the newly combined table
        conn.update(worksheet=sheet_name, data=updated_df)
        
        st.toast("✅ Google Sheet updated successfully!")
    except Exception as e:
        st.error(f"Sheet Update Error: {e}")

def generate_contract(name, place, building, contact, date1, date2, job, sig_file, sig_x, sig_y):
    # --- LOAD TEMPLATES ---
    # IMPORTANT: Upload temp.png and temp2.png to your GitHub root folder
    page1 = Image.open("temp.png").convert("RGB")
    page2 = Image.open("temp2.png").convert("RGB")
    
    draw1 = ImageDraw.Draw(page1)
    draw2 = ImageDraw.Draw(page2)
    
    # --- LOAD FONT ---
    # Upload arial.ttf to GitHub or use default if it fails
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # --- DRAW ON PAGE 1 ---
    draw1.text((143, 619), name, fill="black", font=font)
    draw1.text((143, 649), place, fill="black", font=font)
    draw1.text((619, 650), building, fill="black", font=font)
    draw1.text((619, 682), contact, fill="black", font=font)
    draw1.text((403, 185), date1, fill="black", font=font)
    draw1.text((577, 185), date2, fill="black", font=font)
    draw1.text((259, 548), job, fill="black", font=font)

    # --- DRAW ON PAGE 2 ---
    draw2.text((457, 225), f"{date1}", fill="black", font=font)

    # --- HANDLE SIGNATURE ---
    if sig_file:
        sig = Image.open(sig_file).convert("RGBA")
        sig = sig.resize((200, 80)) 
        # Pasting signature on Page 2 based on your code logic
        page2.paste(sig, (sig_x, sig_y), sig) 
        
    return page1, page2

# --- STREAMLIT UI ---
st.set_page_config(page_title="Contract Automator", page_icon="📜")
st.title("📜 Salsal Contract Creator")


col1, col2 = st.columns(2)
with col1:
    name_input = st.text_input("Client Name")
    place_input = st.text_input("Client Location")
    job_input = st.text_input("Scope of Work")
    date1_input = st.text_input("Contract Start")
with col2:
    date2_input = st.text_input("Contract End")
    building_input = st.text_input("Building")
    contact_input = st.text_input("Contact No.")

st.divider()

# Signature and Positioning
sig_upload = st.file_uploader("Upload Signature", type=['png', 'jpg'])
c1, c2 = st.columns(2)
with c1:
    sig_x = st.number_input("Signature X", value=150)
with c2:
    sig_y = st.number_input("Signature Y", value=190)

if st.button("Crreate Contract PDF & Log"):
    if name_input and date1_input:
        p1, p2 = generate_contract(
            name_input, place_input, building_input, contact_input, 
            date1_input, date2_input, job_input, sig_upload, sig_x, sig_y
        )
        
        st.image(p1, caption="Page 1 Preview", use_column_width=True)
        st.image(p2, caption="Page 2 Preview", use_column_width=True)
        
        # Save as Multi-page PDF
        pdf_buffer = io.BytesIO()
        p1.save(pdf_buffer, format="PDF", save_all=True, append_images=[p2], resolution=100.0)
        
        st.download_button(
            label="💾 Download Full Contract",
            data=pdf_buffer.getvalue(),
            file_name=f"Contract_{name_input}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        # Log to Google Sheets
        log_to_sheet(name_input, job_input, place_input)
    else:
        st.warning("Please enter at least the Client Name and Start Date.")
