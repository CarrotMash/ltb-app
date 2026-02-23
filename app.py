
import streamlit as st
import pandas as pd
from ltb_data import generate_volumes
from gemini_sync import fetch_missing_titles, fetch_latest_volumes
from supabase_db import load_collection, save_collection
import json
import os

# Page Config
st.set_page_config(page_title="LTB Sammel-Zentrale", page_icon="🦆", layout="wide")

# Custom CSS for Comic Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .comic-card {
        background: white;
        border: 4px solid black;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 8px 8px 0px black;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    
    .comic-card:hover {
        transform: translate(-2px, -2px);
        box-shadow: 10px 10px 0px black;
    }
    
    .ltb-logo {
        background: #e11d48;
        color: white;
        font-weight: 900;
        padding: 10px 25px;
        border: 4px solid black;
        border-radius: 12px;
        box-shadow: 6px 6px 0px black;
        display: inline-block;
        transform: rotate(-3deg);
        font-style: italic;
        font-size: 32px;
        margin-bottom: 20px;
    }
    
    .stButton>button {
        background-color: white;
        border: 3px solid black !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        box-shadow: 4px 4px 0px black !important;
        transition: all 0.2s;
        width: 100%;
        text-transform: uppercase;
        font-size: 14px;
    }
    
    .stButton>button:hover {
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0px black !important;
        background-color: #fef9c3;
        border-color: black !important;
    }
    
    .stButton>button:active {
        transform: translate(2px, 2px);
        box-shadow: 0px 0px 0px black !important;
    }

    .owned-btn>button {
        background-color: #10b981 !important; /* Emerald 500 */
        color: white !important;
    }

    .missing-btn>button {
        background-color: white !important;
        color: black !important;
    }
    
    h1, h2, h3 {
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: -1px;
        color: black;
    }

    .owned-row {
        background-color: #ecfdf5; /* Emerald 50 */
        border: 4px solid #059669; /* Emerald 600 */
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        box-shadow: 4px 4px 0px #059669;
    }

    .missing-row {
        background-color: white;
        border: 4px solid black;
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        box-shadow: 4px 4px 0px black;
    }

    .vol-nr {
        background: black;
        color: white;
        font-weight: 900;
        padding: 6px 14px;
        border-radius: 10px;
        margin-right: 15px;
        font-size: 20px;
        min-width: 60px;
        text-align: center;
    }

    .vol-title {
        font-weight: 800;
        font-size: 18px;
        flex-grow: 1;
        color: #1f2937;
    }
</style>
""", unsafe_allow_html=True)

# State Management
if 'volumes' not in st.session_state:
    st.session_state.volumes = generate_volumes(608)
if 'username' not in st.session_state:
    st.session_state.username = None
if 'owned' not in st.session_state:
    st.session_state.owned = []

# Login Logic
if not st.session_state.username:
    st.markdown('<div style="display: flex; justify-content: center; align-items: center; height: 80vh;">', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="comic-card" style="width: 400px; text-align: center;">', unsafe_allow_html=True)
        st.markdown('<div class="ltb-logo">LTB</div>', unsafe_allow_html=True)
        st.header("Zentrale")
        user_input = st.text_input("Dein Name:", placeholder="z.B. Donald")
        if st.button("Einloggen"):
            if user_input:
                st.session_state.username = user_input
                st.session_state.owned = load_collection(user_input)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Header
header_col1, header_col2 = st.columns([1, 4])
with header_col1:
    st.markdown('<div class="ltb-logo">LTB</div>', unsafe_allow_html=True)
with header_col2:
    st.title("Sammel-Zentrale")
    st.write(f"Willkommen zurück, **{st.session_state.username}**!")

# Sidebar / Stats
with st.sidebar:
    st.markdown(f'<div class="comic-card">', unsafe_allow_html=True)
    st.header("Status")
    total = len(st.session_state.volumes)
    owned_count = len(st.session_state.owned)
    percent = int((owned_count / total) * 100) if total > 0 else 0
    
    st.metric("Fortschritt", f"{percent}%", f"{owned_count} / {total}")
    st.progress(percent / 100)
    
    if st.button("💾 Speichern"):
        save_collection(st.session_state.username, st.session_state.owned)
        st.success("Gespeichert!")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="comic-card">', unsafe_allow_html=True)
    st.header("Aktionen")
    if st.button("Alle bis 608"):
        st.session_state.owned = list(range(1, 609))
        save_collection(st.session_state.username, st.session_state.owned)
        st.rerun()
        
    if st.button("Reset"):
        st.session_state.owned = []
        save_collection(st.session_state.username, st.session_state.owned)
        st.rerun()
    
    if st.button("Abmelden"):
        st.session_state.username = None
        st.session_state.owned = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Main Tabs
tab1, tab2, tab3 = st.tabs(["📚 MEINE SAMMLUNG", "📅 KALENDER", "🔄 SYNC"])

with tab1:
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search = st.text_input("Suchen...", placeholder="Nummer oder Titel", label_visibility="collapsed")
    with search_col2:
        filter_mode = st.selectbox("Filter", ["Alle", "Besessen", "Fehlend"], label_visibility="collapsed")
    
    # Filter logic
    filtered = [v for v in st.session_state.volumes if search.lower() in v['title'].lower() or search in str(v['nr'])]
    
    if filter_mode == "Besessen":
        filtered = [v for v in filtered if v['nr'] in st.session_state.owned]
    elif filter_mode == "Fehlend":
        filtered = [v for v in filtered if v['nr'] not in st.session_state.owned]

    # Pagination
    page_size = 24
    total_pages = max((len(filtered) // page_size) + (1 if len(filtered) % page_size > 0 else 0), 1)
    
    page_col1, page_col2 = st.columns([1, 4])
    with page_col1:
        page = st.number_input("Seite", min_value=1, max_value=total_pages, step=1)
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Display Grid
    st.markdown("---")
    
    # We use columns to create a grid-like feel
    cols_per_row = 3
    for i in range(0, len(filtered[start_idx:end_idx]), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, vol in enumerate(filtered[start_idx:end_idx][i:i+cols_per_row]):
            is_owned = vol['nr'] in st.session_state.owned
            with cols[j]:
                st.markdown(f"""
                <div class="{'owned-row' if is_owned else 'missing-row'}">
                    <span class="vol-nr">{vol['nr']}</span>
                    <span class="vol-title">{vol['title']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                btn_label = "BESITZEN" if not is_owned else "ENTFERNEN"
                btn_key = f"btn_{vol['nr']}"
                
                # Wrap button in a div to apply custom class for color
                st.markdown(f'<div class="{"owned-btn" if is_owned else "missing-btn"}">', unsafe_allow_html=True)
                if st.button(btn_label, key=btn_key):
                    if is_owned:
                        st.session_state.owned.remove(vol['nr'])
                    else:
                        st.session_state.owned.append(vol['nr'])
                    save_collection(st.session_state.username, st.session_state.owned)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.header("Kommende Highlights")
    upcoming = [v for v in st.session_state.volumes if v['is_upcoming']]
    if upcoming:
        for v in upcoming:
            st.markdown(f"""
            <div class="comic-card" style="border-color: #e11d48;">
                <h3 style="color: #e11d48;">Band {v['nr']}: {v['title']}</h3>
                <p style="font-size: 18px;">📅 <b>{v['release_date']}</b></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Momentan keine neuen Ankündigungen.")

with tab3:
    st.markdown('<div class="comic-card">', unsafe_allow_html=True)
    st.header("Daten-Abgleich")
    st.write("Synchronisiere deine Liste mit den neuesten Veröffentlichungen aus Entenhausen.")
    
    if st.button("🔄 JETZT ABGLEICHEN"):
        with st.spinner("Verbindung zum Archiv wird hergestellt..."):
            # Fetch new
            max_nr = max(v['nr'] for v in st.session_state.volumes)
            new_vols = fetch_latest_volumes(max_nr)
            if new_vols:
                st.session_state.volumes.extend(new_vols)
                st.success(f"{len(new_vols)} neue Bände gefunden!")
            
            # Fetch missing titles for 600+
            missing = [v['nr'] for v in st.session_state.volumes if v['nr'] >= 600 and "LTB Band" in v['title']]
            if missing:
                updates = fetch_missing_titles(missing[:20])
                for up in updates:
                    for v in st.session_state.volumes:
                        if v['nr'] == up['nr']:
                            v['title'] = up['title']
                st.success(f"{len(updates)} Titel aktualisiert!")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
