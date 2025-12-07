import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Testcase Generator", layout="wide")

st.title("AI Testcase Generator")
st.caption("Gib eine User Story ein und erhalte strukturierte Testfälle und Test-User. (Demo Oberfläche)")

st.markdown("---")

col_input, col_output = st.columns([1, 2])

with col_input:
    st.subheader("Eingabe")

    user_story = st.text_area(
        "User Story",
        placeholder="Als [Rolle] möchte ich [Funktion], um [Nutzen] ...",
        height=220
    )

    test_types = st.multiselect(
        "Welche Testarten möchtest du generieren?",
        ["Positive", "Negative", "Edge"],
        default=["Positive", "Negative", "Edge"]
    )

    generate = st.button("Testfälle generieren")

with col_output:
    st.subheader("Ausgabe")

    if not generate:
        st.info("Gib links eine User Story ein und klicke auf 'Testfälle generieren'.")
    else:
        if not user_story.strip():
            st.warning("Bitte zuerst eine User Story eingeben.")
        else:
            # --- Demo-Testfälle ---
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
                    "Titel": "Maximale Versicherungs­summe",
                    "Vorbedingungen": "User eingeloggt",
                    "Testschritte": "1. App öffnen\n2. maximale Versicherungs­summe eingeben\n3. speichern",
                    "Erwartetes Ergebnis": "Versicherung wird akzeptiert, keine Fehlermeldung",
                    "Priorität": "Mittel",
                },
            ]

            # Nach gewählten Kategorien filtern
            testcases_data = [
                tc for tc in testcases_data if tc["Kategorie"] in test_types
            ]

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
