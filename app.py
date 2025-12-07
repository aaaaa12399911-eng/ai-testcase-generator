import streamlit as st
import pandas as pd

# ---------- Seiteneinstellungen ----------
st.set_page_config(
    page_title="AI Testcase Generator",
    layout="wide"
)

# ---------- Custom CSS mit Animation ----------
st.markdown(
    """
    <style>
    /* Grundlayout */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                     system-ui, sans-serif;
        background: radial-gradient(circle at top left, #f5f7ff, #ffffff);
    }
    .main {
        padding-top: 1.2rem;
    }
    .block-container {
        padding-top: 0.5rem !important;
    }

    /* Leere Spalten-Container entfernen (die weißen Balken) */
    div[data-testid="column"] > div:empty {
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        display: none !important;
    }

    /* Header mit Icon */
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

    /* Karten-Layout */
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

    /* Button mit Glow und leichter Bewegung */
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

    /* Multiselect-Chips */
    .stMultiSelect [data-baseweb="tag"] {
        border-radius: 999px !important;
        background: rgba(79, 70, 229, 0.08) !important;
        color: #1f2933 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.3rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding: 0.25rem 1.1rem;
    }

    /* Dataframe-Rahmen */
    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.5);
    }

    /* Hintergrund-Animation ganz leicht */
    @keyframes bgMove {
        0% {
            background-position: 0% 0%;
        }
        50% {
            background-position: 60% 40%;
        }
        100% {
            background-position: 0% 0%;
        }
    }
    body {
        background: radial-gradient(circle at top left, #eef2ff, #ffffff);
        background-size: 140% 140%;
        animation: bgMove 18s ease-in-out infinite;
    }

    /* Logo-Pulse Animation */
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

# ---------- Layout ----------
left_col, right_col = st.columns([1, 1.25])

# ---------- Eingabe-Karte ----------
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

# ---------- Ausgabe-Karte ----------
with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Ausgabe</div>', unsafe_allow_html=True)

    if not generate:
        st.info("Gib links eine User Story ein und klicke auf **„Testfälle generieren“**.")
    else:
        if not user_story.strip():
            st.warning("Bitte zuerst eine User Story eingeben.")
        else:
            # Demo Testfälle - später durch KI ersetzen
            testcases_data = [
                {
                    "ID": "TC-001",
                    "Kategorie": "Positive",
                    "Titel": "Erfolgreiche Ausführung",
                    "Vorbedingungen": "User eingeloggt",
                    "Testschritte": "1. App öffnen\n2. Versicherung für Haustier anlegen",
                    "Erwartetes Ergebnis": "Versicherung wird erfolgreich gespeichert",
                    "Priorität": "Hoch",
                },
                {
                    "ID": "TC-002",
                    "Kategorie": "Negative",
                    "Titel": "Pflichtfeld fehlt",
                    "Vorbedingungen": "User eingeloggt",
                    "Testschritte": "1. App öffnen\n2. Haustier ohne Namen speichern",
                    "Erwartetes Ergebnis": "Fehlermeldung: Tiername ist Pflicht",
                    "Priorität": "Hoch",
                },
                {
                    "ID": "TC-003",
                    "Kategorie": "Edge",
                    "Titel": "Maximale Versicherungssumme",
                    "Vorbedingungen": "User eingeloggt",
                    "Testschritte": "1. App öffnen\n2. maximale Versicherungssumme eingeben\n3. speichern",
                    "Erwartetes Ergebnis": "Versicherung wird akzeptiert, keine Fehlermeldung",
                    "Priorität": "Mittel",
                },
            ]

            testcases_data = [tc for tc in testcases_data if tc["Kategorie"] in test_types]
            df_testcases = pd.DataFrame(testcases_data)

            personas_data = [
                {
                    "Name": "Max Mustermann",
                    "Rolle": "Privatkunde mit Haustier",
                    "Rechte": "Standardkunde, Zugriff auf Robo-Advisor",
                    "Eigenschaften": "Android, mittlere App-Erfahrung",
                    "Relevanz": "Normale Abschlüsse, Happy Path",
                },
                {
                    "Name": "Anna Admin",
                    "Rolle": "Bankberaterin",
                    "Rechte": "Erweiterte Einsicht, keine Kundenabschlüsse",
                    "Eigenschaften": "iOS, Power-User",
                    "Relevanz": "Berechtigungen und Sonderfälle",
                },
            ]
            df_personas = pd.DataFrame(personas_data)

            tab1, tab2 = st.tabs(["Testfälle", "Test-User"])

            with tab1:
                st.markdown("**Generierte Testfälle (Demo)**")
                st.dataframe(df_testcases, use_container_width=True)

            with tab2:
                st.markdown("**Generierte Test-User / Personas (Demo)**")
                st.dataframe(df_personas, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
