
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Google Drive Picker", layout="centered")
st.title("Vybrat soubor z Google Drive a uložit odkaz")

# --- kontrola secrets ---
required = ["GOOGLE_CLIENT_ID", "GOOGLE_API_KEY", "GOOGLE_APP_ID"]
missing = [k for k in required if k not in st.secrets]
if missing:
    st.error(f"Chybí secrets: {', '.join(missing)}")
    st.stop()

CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
API_KEY = st.secrets["GOOGLE_API_KEY"]
APP_ID = st.secrets["GOOGLE_APP_ID"]

# --- 1) přečti návrat z pickeru (query params) ---
qp = st.query_params
if "fileId" in qp and "name" in qp:
    file_id = qp["fileId"]
    name = qp["name"]

    st.session_state.setdefault("saved_files", [])
    # neukládej duplicity
    if not any(x["fileId"] == file_id for x in st.session_state["saved_files"]):
        st.session_state["saved_files"].append({"name": name, "fileId": file_id})

    # vyčisti URL, ať se to nepřidává znovu po refreshi
    st.query_params.clear()

    st.success(f"Uloženo: {name}")

# --- 2) UI: tlačítko otevře picker (běží v HTML/JS) ---
st.markdown("### 1) Klikni na tlačítko a vyber soubor")
st.markdown("Pozn.: Přihlašování proběhne v modálním okně od Googlu (GIS), bez serverového OAuth.")

# Doporučení: minimal scope.
# Oficiální sample používá drive.metadata.readonly. [1](https://developers.google.com/workspace/drive/picker/guides/sample)
# Pro lepší bezpečnost se často doporučuje drive.file (omezuje přístup na soubory otevřené přes picker). [3](https://dev.to/googleworkspace/secure-google-drive-picker-token-best-practices-43al)
SCOPE = "https://www.googleapis.com/auth/drive.file"

html = f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <style>
      body {{ font-family: sans-serif; }}
      button {{
        padding: 10px 14px; border: 0; border-radius: 8px;
        background: #1a73e8; color: white; cursor: pointer;
      }}
      button:disabled {{ background: #999; cursor: not-allowed; }}
      .hint {{ margin-top: 10px; color: #555; }}
    </style>
  </head>
  <body>
    <button id="pickBtn" disabled>Vybrat z Google Drive</button>
    <div class="hint" id="status">Načítám Google knihovny…</div>

    <script>
      const SCOPES = "{SCOPE}";
      const CLIENT_ID = "{CLIENT_ID}";
      const API_KEY = "{API_KEY}";
      const APP_ID = "{APP_ID}";

      let tokenClient;
      let accessToken = null;
      let pickerInited = false;
      let gisInited = false;

      function maybeEnable() {{
        if (pickerInited && gisInited) {{
          document.getElementById("pickBtn").disabled = false;
          document.getElementById("status").textContent = "Připraveno. Klikni na tlačítko.";
        }}
      }}

      // z oficiálního vzoru: gapi.load('client:picker', ...) a GIS token client [1](https://developers.google.com/workspace/drive/picker/guides/sample)
      function gapiLoaded() {{
        gapi.load('client:picker', async () => {{
          await gapi.client.load('https://www.googleapis.com/discovery/v1/apis/drive/v3/rest');
          pickerInited = true;
          maybeEnable();
        }});
      }}

      function gisLoaded() {{
        tokenClient = google.accounts.oauth2.initTokenClient({{
          client_id: CLIENT_ID,
          scope: SCOPES,
          callback: (resp) => {{
            if (resp.error) {{
              document.getElementById("status").textContent = "OAuth chyba: " + resp.error;
              return;
            }}
            accessToken = resp.access_token;
            createPicker();
          }}
        }});
        gisInited = true;
        maybeEnable();
      }}

      function createPicker() {{
        if (!accessToken) return;

        const view = new google.picker.DocsView()
          .setIncludeFolders(true);

        const picker = new google.picker.PickerBuilder()
          .setDeveloperKey(API_KEY)
          .setAppId(APP_ID)
          .setOAuthToken(accessToken)
          .addView(view)
          .setCallback(pickerCallback)
          .build();

        picker.setVisible(true);
      }}

      function pickerCallback(data) {{
        if (data.action === google.picker.Action.PICKED) {{
          const doc = data.docs[0];
          const fileId = doc.id;
          const name = doc.name || doc.title || "soubor";

          // Pošli výsledek zpět do Streamlitu přes query string
          const base = window.location.origin + window.location.pathname;
          const url = base + "?fileId=" + encodeURIComponent(fileId) + "&name=" + encodeURIComponent(name);
          window.location.href = url;
        }}
      }}

      document.getElementById("pickBtn").addEventListener("click", () => {{
        document.getElementById("status").textContent = "Otevírám přihlášení / picker…";
        tokenClient.requestAccessToken({{ prompt: 'consent' }});
      }});
    </script>

    <script async defer src="https://apis.google.com/js/api.js" onload="gapiLoaded()"></script>
    <script async defer src="https://accounts.google.com/gsi/client" onload="gisLoaded()"></script>
  </body>
</html>
"""

components.html(html, height=140)

# --- 3) Zobrazení uložených položek + odkaz pro otevření ---
st.markdown("### 2) Uložené soubory")
saved = st.session_state.get("saved_files", [])

if not saved:
    st.info("Zatím nic uloženého.")
else:
    for item in saved:
        file_id = item["fileId"]
        name = item["name"]
        # praktický odkaz pro otevření v Drive UI
        link = f"https://drive.google.com/file/d/{file_id}/view"
        st.markdown(f"- **{name}** — {link}")

    # volitelné: export do JSON (na Streamlit Cloud je disk dočasný, ale pro test ok)
    st.download_button(
        "Stáhnout uložené odkazy (JSON)",
        data=json.dumps(saved, ensure_ascii=False, indent=2),
        file_name="saved_drive_files.json",
        mime="application/json",
    )
