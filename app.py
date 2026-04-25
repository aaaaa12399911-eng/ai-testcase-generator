import json
import io
import zipfile
import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI
from PIL import Image

# ---------- OpenAI Client ----------
# API-Key kommt aus Streamlit Secrets (nicht im Code speichern)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- Seiteneinstellungen ----------
st.set_page_config(
    page_title="AI Testcase Generator",
    layout="wide"
)

# ---------- Custom CSS mit Animation ----------
st.markdown(
    """
    <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                     system-ui, sans-serif;
        background: radial-gradient(circle at top left, #eef2ff, #ffffff);
        background-size: 140% 140%;
        animation: bgMove 18s ease-in-out infinite;
    }
    .main {
        padding-top: 1.2rem;
    }
    .block-container {
        padding-top: 0.5rem !important;
    }
    div[data-testid="column"] > div:empty {
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        display: none !important;
    }
    .app-header-wrap {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.2rem;
    }
    .logo-badge {
        width: 40px;
        height: 40px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle at 30% 30%, #ffffff, #6366f1);
        box-shadow: 0 10px 25px rgba(79, 70, 229, 0.45);
        color: #111827;
        font-size: 1.3rem;
        animation: logoPulse 2.4s ease-in-out infinite;
    }
    .app-header {
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-bottom: 0.1rem;
    }
    .app-subtitle {
        font-size: 0.95rem;
        color: #6b7280;
        margin-bottom: 1.3rem;
    }
    .card {
        background: #ffffff;
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        box-shadow:
            0 12px 30px rgba(15, 23, 42, 0.08),
            0 1px 2px rgba(15, 23, 42, 0.05);
        border: 1px solid rgba(148, 163, 184, 0.3);
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    .stButton>button {
        border-radius: 999px;
        padding: 0.55rem 1.8rem;
        font-weight: 600;
        border: none;
        background: linear-gradient(135deg, #6366f1, #ec4899);
        color: white;
        box-shadow: 0 12px 26px rgba(79, 70, 229, 0.55);
        transition: transform 0.15s ease-out, box-shadow 0.15s ease-out;
        position: relative;
        overflow: hidden;
    }
    .stButton>button::after {
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 0 0, rgba(255,255,255,0.65), transparent 55%);
        opacity: 0;
        transition: opacity 0.25s ease-out, transform 0.25s ease-out;
        transform: translate(-40%, -40%);
    }
    .stButton>button:hover {
        box-shadow: 0 16px 32px rgba(79, 70, 229, 0.65);
        transform: translateY(-1px);
    }
    .stButton>button:hover::after {
        opacity: 1;
        transform: translate(-10%, -20%);
    }
    .stMultiSelect [data-baseweb="tag"] {
        border-radius: 999px !important;
        background: rgba(79, 70, 229, 0.08) !important;
        color: #1f2933 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.3rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding: 0.25rem 1.1rem;
    }
    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.5);
    }
    @keyframes bgMove {
        0% { background-position: 0% 0%; }
        50% { background-position: 60% 40%; }
        100% { background-position: 0% 0%; }
    }
    @keyframes logoPulse {
        0% {
            transform: translateY(0) scale(1);
            box-shadow: 0 10px 25px rgba(79, 70, 229, 0.45);
        }
        50% {
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 18px 35px rgba(79, 70, 229, 0.6);
        }
        100% {
            transform: translateY(0) scale(1);
            box-shadow: 0 10px 25px rgba(79, 70, 229, 0.45);
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Header ----------
st.markdown(
    """
    <div class="app-header-wrap">
        <div class="logo-badge">🔎</div>
        <div>
            <div class="app-header">AI Testcase Generator</div>
            <div class="app-subtitle">
                Gib eine User Story ein und generiere strukturierte Testfälle und Test-User für dein QA-Team.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("")

# ---------- 3D-Asset-Funktionen ----------
def _build_relief_obj_from_image(
    image: Image.Image,
    max_resolution: int = 192,
    depth_scale: float = 0.25,
):
    """
    Erstellt ein einfaches 3D-Relief-Mesh (OBJ) aus einem Bild.
    Ausgabe: OBJ + MTL + Textur als ZIP (bytes) inklusive Metadaten.
    """
    img = image.convert("RGB")
    width, height = img.size
    longest = max(width, height)
    if longest > max_resolution:
        scale = max_resolution / float(longest)
        new_size = (max(2, int(width * scale)), max(2, int(height * scale)))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    w, h = img.size
    rgb = np.asarray(img).astype(np.float32) / 255.0
    gray = rgb.mean(axis=2)

    # Normiertes Height-Field
    z_map = (gray - gray.min()) / (gray.max() - gray.min() + 1e-8)
    z_map = z_map * depth_scale

    # Vertices (Top + Bottom)
    vertices = []
    uvs = []

    for y in range(h):
        for x in range(w):
            xf = (x / (w - 1)) - 0.5
            yf = 0.5 - (y / (h - 1))
            zf = float(z_map[y, x])
            vertices.append((xf, yf, zf))
            uvs.append((x / (w - 1), 1.0 - y / (h - 1)))

    top_count = len(vertices)
    for y in range(h):
        for x in range(w):
            xf = (x / (w - 1)) - 0.5
            yf = 0.5 - (y / (h - 1))
            vertices.append((xf, yf, 0.0))

    faces = []

    def top_idx(x, y):
        return y * w + x

    def bottom_idx(x, y):
        return top_count + y * w + x

    # Top surface
    for y in range(h - 1):
        for x in range(w - 1):
            a = top_idx(x, y)
            b = top_idx(x + 1, y)
            c = top_idx(x, y + 1)
            d = top_idx(x + 1, y + 1)
            faces.append((a, c, b))
            faces.append((b, c, d))

    # Bottom surface
    for y in range(h - 1):
        for x in range(w - 1):
            a = bottom_idx(x, y)
            b = bottom_idx(x + 1, y)
            c = bottom_idx(x, y + 1)
            d = bottom_idx(x + 1, y + 1)
            faces.append((a, b, c))
            faces.append((b, d, c))

    # Seiten schließen
    for x in range(w - 1):  # top edge
        t1, t2 = top_idx(x, 0), top_idx(x + 1, 0)
        b1, b2 = bottom_idx(x, 0), bottom_idx(x + 1, 0)
        faces.append((t1, t2, b1))
        faces.append((t2, b2, b1))

    for x in range(w - 1):  # bottom edge
        t1, t2 = top_idx(x, h - 1), top_idx(x + 1, h - 1)
        b1, b2 = bottom_idx(x, h - 1), bottom_idx(x + 1, h - 1)
        faces.append((t1, b1, t2))
        faces.append((t2, b1, b2))

    for y in range(h - 1):  # left edge
        t1, t2 = top_idx(0, y), top_idx(0, y + 1)
        b1, b2 = bottom_idx(0, y), bottom_idx(0, y + 1)
        faces.append((t1, b1, t2))
        faces.append((t2, b1, b2))

    for y in range(h - 1):  # right edge
        t1, t2 = top_idx(w - 1, y), top_idx(w - 1, y + 1)
        b1, b2 = bottom_idx(w - 1, y), bottom_idx(w - 1, y + 1)
        faces.append((t1, t2, b1))
        faces.append((t2, b2, b1))

    # OBJ / MTL bauen
    obj_lines = ["mtllib asset.mtl", "usemtl material_0"]
    for vx, vy, vz in vertices:
        obj_lines.append(f"v {vx:.6f} {vy:.6f} {vz:.6f}")
    for u, v in uvs:
        obj_lines.append(f"vt {u:.6f} {v:.6f}")

    # Für Bottom-Vertices dieselben UVs wiederverwenden
    for u, v in uvs:
        obj_lines.append(f"vt {u:.6f} {v:.6f}")

    # v/vt faces (1-indexed)
    for a, b, c in faces:
        # UV-Index 1:1 Vertex-Index
        a1, b1, c1 = a + 1, b + 1, c + 1
        obj_lines.append(f"f {a1}/{a1} {b1}/{b1} {c1}/{c1}")

    mtl = "\n".join(
        [
            "newmtl material_0",
            "Ka 1.000 1.000 1.000",
            "Kd 1.000 1.000 1.000",
            "Ks 0.000 0.000 0.000",
            "d 1.0",
            "illum 2",
            "map_Kd texture.png",
        ]
    )
    obj = "\n".join(obj_lines)

    texture_bytes = io.BytesIO()
    img.save(texture_bytes, format="PNG")
    texture_bytes.seek(0)

    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("asset.obj", obj)
        zf.writestr("asset.mtl", mtl)
        zf.writestr("texture.png", texture_bytes.getvalue())
    archive.seek(0)

    return archive.getvalue(), {
        "vertices": len(vertices),
        "faces": len(faces),
        "texture_size": f"{w}x{h}",
    }

# ---------- KI-Funktion ----------

def generate_tests_with_ai(user_story: str, selected_types: list):
    """
    Ruft OpenAI auf und erzeugt Testfälle + Personas als JSON.
    """
    type_text = ", ".join(selected_types) if selected_types else "alle Kategorien"

    system_msg = (
        "Du bist ein erfahrener Testmanager in einem agilen Banking-Umfeld. "
        "Du schreibst präzise, praxisnahe Testfälle in Deutsch. "
        "Gib die Antwort ausschließlich als JSON zurück, ohne Erklärungstext."
    )

    user_prompt = f"""
Erzeuge auf Basis der folgenden User Story Testfälle und Test-User (Personas).

User Story:
\"\"\"{user_story}\"\"\"


Anforderungen an die Ausgabe:

1) Erzeuge Testfälle in folgenden Kategorien: {type_text}.
2) Für jeden Testfall:
   - id (string, z.B. TC-001, TC-002 ...)
   - category (\"Positive\", \"Negative\" oder \"Edge\")
   - title
   - preconditions
   - steps (Liste von Schritten)
   - expected_result
   - priority (\"Hoch\", \"Mittel\", \"Niedrig\")

3) Erzeuge zusätzlich 2–4 Test-User/Personas mit:
   - name
   - role
   - permissions
   - attributes
   - relevance

Gib das Ergebnis exakt in folgendem JSON-Format zurück:

{{
  "testcases": [
    {{
      "id": "TC-001",
      "category": "Positive",
      "title": "...",
      "preconditions": "...",
      "steps": ["Schritt 1", "Schritt 2"],
      "expected_result": "...",
      "priority": "Hoch"
    }}
  ],
  "personas": [
    {{
      "name": "...",
      "role": "...",
      "permissions": "...",
      "attributes": "...",
      "relevance": "..."
    }}
  ]
}}
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.15,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = resp.choices[0].message.content

    # JSON parsen
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: versuchen, JSON aus Text herauszuziehen
        try:
            start = content.index("{")
            end = content.rindex("}") + 1
            data = json.loads(content[start:end])
        except Exception:
            raise ValueError("Die KI-Antwort konnte nicht als JSON gelesen werden.")

    testcases = data.get("testcases", [])
    personas = data.get("personas", [])

    # In DataFrames umwandeln
    if testcases:
        for i, tc in enumerate(testcases, start=1):
            tc.setdefault("id", f"TC-{i:03d}")
        df_tc = pd.DataFrame(
            [
                {
                    "ID": tc.get("id", ""),
                    "Kategorie": tc.get("category", ""),
                    "Titel": tc.get("title", ""),
                    "Vorbedingungen": tc.get("preconditions", ""),
                    "Testschritte": "\n".join(tc.get("steps", [])),
                    "Erwartetes Ergebnis": tc.get("expected_result", ""),
                    "Priorität": tc.get("priority", ""),
                }
                for tc in testcases
            ]
        )
    else:
        df_tc = pd.DataFrame()

    if personas:
        df_p = pd.DataFrame(
            [
                {
                    "Name": p.get("name", ""),
                    "Rolle": p.get("role", ""),
                    "Rechte": p.get("permissions", ""),
                    "Eigenschaften": p.get("attributes", ""),
                    "Relevanz": p.get("relevance", ""),
                }
                for p in personas
            ]
        )
    else:
        df_p = pd.DataFrame()

    return df_tc, df_p

# ---------- 3D Asset Generator ----------
st.markdown("### 3D Asset aus Bild generieren")
st.caption("Lädt ein einzelnes Bild hoch und erzeugt ein texturiertes OBJ-Mesh (Relief) als ZIP.")

asset_left, asset_right = st.columns([1, 1.2])
with asset_left:
    uploaded_image = st.file_uploader(
        "Bild für 3D-Asset",
        type=["png", "jpg", "jpeg", "webp"],
        help="Für beste Resultate: Objekt klar sichtbar, wenig Bewegungsunschärfe.",
    )
    mesh_resolution = st.slider("Max. Mesh-Auflösung", min_value=64, max_value=320, value=192, step=16)
    depth_scale = st.slider("Relief-Tiefe", min_value=0.05, max_value=0.50, value=0.25, step=0.01)
    generate_asset = st.button("3D Asset generieren")

with asset_right:
    if uploaded_image is not None:
        preview = Image.open(uploaded_image)
        st.image(preview, caption="Vorschau")
    if generate_asset and uploaded_image is not None:
        source_img = Image.open(uploaded_image)
        with st.spinner("Erzeuge 3D-Asset …"):
            zip_bytes, meta = _build_relief_obj_from_image(
                source_img,
                max_resolution=mesh_resolution,
                depth_scale=depth_scale,
            )
        st.success("3D-Asset erstellt. Du kannst das ZIP direkt herunterladen.")
        st.write(f"Vertices: **{meta['vertices']}** | Faces: **{meta['faces']}** | Textur: **{meta['texture_size']}**")
        st.download_button(
            "Download asset.zip",
            data=zip_bytes,
            file_name="asset.zip",
            mime="application/zip",
        )
    elif generate_asset:
        st.warning("Bitte zuerst ein Bild hochladen.")

st.markdown("---")

# ---------- Testcase-Layout ----------
left_col, right_col = st.columns([1, 1.25])

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Eingabe</div>', unsafe_allow_html=True)

    user_story = st.text_area(
        "User Story",
        placeholder="Als [Rolle] möchte ich [Funktion], um [Nutzen] ...",
        height=260,
        label_visibility="visible",
    )

    test_types = st.multiselect(
        "Welche Testarten möchtest du generieren?",
        ["Positive", "Negative", "Edge"],
        default=["Positive", "Negative", "Edge"],
    )

    generate = st.button("Testfälle generieren")

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Ausgabe</div>', unsafe_allow_html=True)

    if not generate:
        st.info("Gib links eine User Story ein und klicke auf **„Testfälle generieren“**.")
    else:
        if not user_story.strip():
            st.warning("Bitte zuerst eine User Story eingeben.")
        elif not test_types:
            st.warning("Bitte mindestens eine Testart auswählen.")
        else:
            with st.spinner("KI generiert Testfälle …"):
                try:
                    df_testcases, df_personas = generate_tests_with_ai(user_story, test_types)

                    if df_testcases.empty:
                        st.warning("Die KI hat keine Testfälle zurückgegeben.")
                    else:
                        tab1, tab2 = st.tabs(["Testfälle", "Test-User"])

                        with tab1:
                            st.markdown("**Generierte Testfälle (KI)**")
                            st.dataframe(df_testcases, use_container_width=True)

                        with tab2:
                            if df_personas.empty:
                                st.info("Keine Personas zurückgegeben.")
                            else:
                                st.markdown("**Generierte Test-User / Personas (KI)**")
                                st.dataframe(df_personas, use_container_width=True)

                except Exception as e:
                    st.error(f"Fehler bei der KI-Generierung: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
