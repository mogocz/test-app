

import streamlit as st
import requests
from urllib.parse import urlencode

# ---- OAuth config ----
CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]

REDIRECT_URI = "https://share.streamlit.io/component/redirect"
SCOPES = "https://www.googleapis.com/auth/drive.metadata.readonly"

# ---- OAuth flow ----
def get_login_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "online",
        "prompt": "consent",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

# ---- Handle redirect ----
query_params = st.query_params
if "code" in query_params and "token" not in st.session_state:
    code = query_params["code"]

    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        },
    ).json()

    st.session_state["token"] = token_resp
    st.query_params.clear()
    st.success("✅ Přihlášení ke Google úspěšné")

# ---- Login UI ----
if "token" not in st.session_state:
    st.markdown("### Přihlášení ke Google")
    st.markdown(
        f'<a href="{get_login_url()}">👉 Přihlásit se ke Google</a>',
        unsafe_allow_html=True,
    )
    st.stop()
``


import streamlit as st

st.title("This is a title A")
st.title("_Streamlit_ is :blue[cool] :sunglasses:")
st.title("Moje první webová apka")

name = st.text_input("Jak se jmenuješ?")
if st.button("pozdrav Mě"):
    st.write(f"Ahoj, {name} 👋")



import streamlit as st

uploaded = st.file_uploader("Nahraj soubor", type=["txt", "csv"])

if uploaded is not None:
    with open(uploaded.name, "wb") as f:
        f.write(uploaded.read())

st.markdown("[A025552378N0204](https://drive.google.com/file/d/1YmUETQCNLsxvRr1rdYal_GuBGaz6qvcZ/view?usp=sharing)")


import streamlit as st

url = st.text_input("URL", value="https://drive.google.com/file/d/1YmUETQCNLsxvRr1rdYal_GuBGaz6qvcZ/view?usp=sharing")
label = st.text_input("Text odkazu", value="Otevřít soubor")

if url:
    st.link_button(label, url)  # label je proměnná [1](https://docs.streamlit.io/develop/api-reference/widgets/st.link_button)


import os, json
import streamlit as st
from streamlit_google_picker import google_picker

st.title("Vyber soubor z Google Drive a ulož odkaz")

# Po OAuth flow musíš mít access token (komponenta očekává token). [9](https://github.com/LounesAl/streamlit-google-picker)[8](https://pypi.org/project/streamlit-google-picker/)
token = st.session_state.get("token", {}).get("access_token")

CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
API_KEY  = st.secrets["GOOGLE_API_KEY"]

APP_ID = CLIENT_ID.split("-")[0]
  # v příkladech komponenty [9](https://github.com/LounesAl/streamlit-google-picker)[8](https://pypi.org/project/streamlit-google-picker/)

if not token:
    st.warning("Nejprve dokonči OAuth přihlášení (musíš mít access_token ve session_state).")
else:
    picked = google_picker(
        label="Vybrat z Google Drive",
        token=token,
        apiKey=API_KEY,
        appId=APP_ID,
        accept_multiple_files=False,
        key="gpicker",
    )

    if picked:
        # picked je 'UploadedFile'-like objekt (má .name, .size_bytes). [8](https://pypi.org/project/streamlit-google-picker/)[9](https://github.com/LounesAl/streamlit-google-picker)
        # ID/link – záleží na tom, co komponenta vrací v objektu ve tvé verzi.
        # Nejrobustnější je ukládat fileId (pokud je dostupné) a link si vždy dopočítat / načíst přes API.

        record = {
            "name": getattr(picked, "name", None),
            "size_bytes": getattr(picked, "size_bytes", None),
            "file_id": getattr(picked, "id", None) or getattr(picked, "file_id", None),
        }

        st.session_state.setdefault("saved", []).append(record)

        # uložit do JSON souboru (jednoduché, bez DB)
        with open("saved_drive_links.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state["saved"], f, ensure_ascii=False, indent=2)

        st.success("Uloženo!")
        st.json(record)

st.subheader("Uložené položky")
st.json(st.session_state.get("saved", []))


st.write("CLIENT_ID OK:", CLIENT_ID[:10])
st.write("APP_ID:", APP_ID)