
import json
import os
from urllib.parse import urlencode

import requests
import streamlit as st
from streamlit_google_picker import google_picker

st.set_page_config(page_title="Google Drive Picker – uložit odkaz", layout="centered")

# ----------------------------
# 0) Ověření secrets
# ----------------------------
REQUIRED_SECRETS = [
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_API_KEY",
    "GOOGLE_APP_ID",
]

missing = [k for k in REQUIRED_SECRETS if k not in st.secrets]
if missing:
    st.error(
        "Chybí secrets: "
        + ", ".join(missing)
        + "\n\nOtevři Streamlit Cloud → Manage app → Secrets a doplň je."
    )
    st.stop()

CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
API_KEY = st.secrets["GOOGLE_API_KEY"]
APP_ID = str(st.secrets["GOOGLE_APP_ID"])  # u tebe project number: 364300237799

# Streamlit Cloud redirect endpoint (používá se pro OAuth návrat)
REDIRECT_URI = "https://share.streamlit.io/component/redirect"

# Scope stačí pro výběr souboru a uložení ID/linku (metadata)
SCOPES = "https://www.googleapis.com/auth/drive.metadata.readonly"

SAVE_PATH = "saved_drive_links.json"


# ----------------------------
# 1) Pomocné funkce – persist
# ----------------------------
def load_saved():
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_item(item):
    saved = load_saved()
    saved.append(item)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(saved, f, ensure_ascii=False, indent=2)


# ----------------------------
# 2) OAuth – login URL
# ----------------------------
def build_login_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "online",
        "prompt": "consent",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)


def exchange_code_for_token(code: str) -> dict:
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        },
        timeout=30,
    )
    return resp.json()


# ----------------------------
# 3) UI
# ----------------------------
st.title("📎 Vyber soubor z Google Drive a ulož odkaz")

st.caption(
    "Cíl: vybrat soubor, uložit jeho `fileId` + odkaz pro pozdější otevření (bez uploadu)."
)

# 3a) Pokud se vrátíme z OAuth s ?code=...
qp = st.query_params
if "code" in qp and "token" not in st.session_state:
    code = qp["code"]
    token_data = exchange_code_for_token(code)

    # Uložit token do session
    if "access_token" in token_data:
        st.session_state["token"] = token_data
        st.success("✅ Přihlášení ke Google úspěšné.")
        # uklidit URL parametry
        st.query_params.clear()
    else:
        st.error(f"OAuth selhal: {token_data}")
        st.stop()

# 3b) Pokud nejsme přihlášení, nabídneme login link
if "token" not in st.session_state:
    st.warning("Nejprve je potřeba přihlásit se ke Google účtu.")
    login_url = build_login_url()
    st.markdown(f"👉 Přihlásit se ke Google\n\n{login_url}")
    st.stop()

# 3c) Máme token → můžeme otevřít Picker
access_token = st.session_state["token"]["access_token"]

st.subheader("1) Vybrat soubor")
picked = google_picker(
    label="Otevřít Google Drive Picker",
    token=access_token,
    apiKey=API_KEY,
    appId=APP_ID,
    accept_multiple_files=False,
    key="gdrive_picker",
)

if picked:
    # streamlit-google-picker vrací objekt podobný UploadedFile; některé verze nesou i ID,
    # ale pro jistotu vytáhneme fileId z atributů, pokud existuje.
    file_id = getattr(picked, "id", None) or getattr(picked, "file_id", None)
    file_name = getattr(picked, "name", None) or getattr(picked, "title", None) or "Bez názvu"

    # Pokud komponenta file_id neposkytne, aspoň uložíme název a dáme instrukci.
    if not file_id:
        st.error(
            "Nepodařilo se zjistit fileId z objektu pickeru (záleží na verzi komponenty). "
            "Zkus aktualizovat streamlit-google-picker nebo mi sem pošli `st.write(picked)` výstup."
        )
    else:
        # Praktický link pro otevření v Drive UI:
        view_url = f"https://drive.google.com/file/d/{file_id}/view"

        item = {"name": file_name, "fileId": file_id, "url": view_url}
        save_item(item)

        st.success("✅ Uloženo!")
        st.write("Název:", file_name)
        st.write("File ID:", file_id)
        st.markdown(f"🔗 Odkaz: {view_url}")

st.divider()

st.subheader("2) Uložené položky")
saved = load_saved()
if not saved:
    st.info("Zatím nemáš uložené žádné soubory.")
else:
    for i, it in enumerate(saved, start=1):
        st.write(f"{i}. {it.get('name','(bez názvu)')}")
        st.code(it.get("fileId", ""), language="text")
        url = it.get("url")
        if url:
            st.markdown(f"{url}")
        st.write("---")
