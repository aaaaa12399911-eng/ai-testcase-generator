import json
import streamlit as st
import pandas as pd
from openai import OpenAI

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

# ---------- Layout ----------
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
