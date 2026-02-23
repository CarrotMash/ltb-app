
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
    }
    
    .ltb-logo {
        background: #e11d48;
        color: white;
        font-weight: 900;
        padding: 10px 20px;
        border: 3px solid black;
        border-radius: 15px;
        box-shadow: 4px 4px 0px black;
        display: inline-block;
        transform: rotate(-3deg);
        font-style: italic;
        font-size: 24px;
    }
    
    .stButton>button {
        background-color: white;
        border: 3px solid black !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        box-shadow: 4px 4px 0px black !important;
        transition: all 0.2s;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0px black !important;
        background-color: #fef9c3;
    }
    
    .stButton>button:active {
        transform: translate(2px, 2px);
        box-shadow: 0px 0px 0px black !important;
    }
    
    h1, h2, h3 {
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: -1px;
    }

    .owned-row {
        background-color: #eff6ff;
        border-left: 10px solid #2563eb;
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
    st.markdown('<div class="comic-card">', unsafe_allow_html=True)
    st.header("Willkommen in der Zentrale!")
    user_input = st.text_input("Gib deinen Namen ein, um deine Sammlung zu laden:", placeholder="z.B. Donald")
    if st.button("Einloggen"):
        if user_input:
            st.session_state.username = user_input
            st.session_state.owned = load_collection(user_input)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.markdown('<div class="ltb-logo">LTB</div>', unsafe_allow_html=True)
with col2:
    st.title("Sammel-Zentrale")
    st.write(f"Hallo, **{st.session_state.username}**! Deine Schatzkammer ist bereit.")
with col3:
    if st.button("Abmelden"):
        st.session_state.username = None
        st.session_state.owned = []
        st.rerun()

# Sidebar / Stats
with st.sidebar:
    st.header("Deine Sammlung")
    total = len(st.session_state.volumes)
    owned_count = len(st.session_state.owned)
    percent = int((owned_count / total) * 100) if total > 0 else 0
    
    st.metric("Fortschritt", f"{percent}%", f"{owned_count} von {total}")
    st.progress(percent / 100)
    
    if st.button("💾 Sammlung jetzt speichern"):
        save_collection(st.session_state.username, st.session_state.owned)
        st.success("Gespeichert!")

    st.divider()
    
    if st.button("Alle bis 608 markieren"):
        st.session_state.owned = list(range(1, 609))
        st.rerun()
        
    if st.button("Sammlung zurücksetzen"):
        if st.checkbox("Ja, ich bin sicher"):
            st.session_state.owned = []
            st.rerun()

# Main Tabs
tab1, tab2, tab3 = st.tabs(["📚 Sammlung", "📅 Kalender", "⚙️ Admin"])

with tab1:
    c1, c2 = st.columns([3, 1])
    with c1:
        search = st.text_input("Suchen...", placeholder="Bandnummer oder Titel")
    with c2:
        filter_mode = st.selectbox("Filter", ["Alle", "Besessen", "Fehlend"])
    
    # Filter logic
    filtered = [v for v in st.session_state.volumes if search.lower() in v['title'].lower() or search in str(v['nr'])]
    
    if filter_mode == "Besessen":
        filtered = [v for v in filtered if v['nr'] in st.session_state.owned]
    elif filter_mode == "Fehlend":
        filtered = [v for v in filtered if v['nr'] not in st.session_state.owned]

    # Pagination
    page_size = 50
    total_pages = max((len(filtered) // page_size) + (1 if len(filtered) % page_size > 0 else 0), 1)
    
    page_col1, page_col2 = st.columns([1, 4])
    with page_col1:
        page = st.number_input("Seite", min_value=1, max_value=total_pages, step=1)
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Display List
    st.markdown("---")
    for vol in filtered[start_idx:end_idx]:
        is_owned = vol['nr'] in st.session_state.owned
        
        # Row styling
        bg_class = "owned-row" if is_owned else ""
        
        row_col1, row_col2, row_col3 = st.columns([1, 4, 1])
        with row_col1:
            st.markdown(f"**#{vol['nr']}**")
        with row_col2:
            st.write(vol['title'])
        with row_col3:
            if st.button("✓" if is_owned else "○", key=f"btn_{vol['nr']}"):
                if is_owned:
                    st.session_state.owned.remove(vol['nr'])
                else:
                    st.session_state.owned.append(vol['nr'])
                # Auto-save on change
                save_collection(st.session_state.username, st.session_state.owned)
                st.rerun()
        st.divider()

with tab2:
    st.header("Kommende Bände")
    upcoming = [v for v in st.session_state.volumes if v['is_upcoming']]
    if upcoming:
        for v in upcoming:
            with st.container():
                st.markdown(f"""
                <div class="comic-card">
                    <h3>Band {v['nr']}: {v['title']}</h3>
                    <p>📅 Erscheint am: <b>{v['release_date']}</b></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.write("Keine kommenden Bände in der Liste.")

with tab3:
    st.header("Daten-Abgleich")
    st.write("Hier kannst du die neuesten Bände aus Entenhausen laden.")
    
    if st.button("🔄 Jetzt synchronisieren"):
        with st.spinner("Synchronisiere..."):
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
