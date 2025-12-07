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
            testcases_data = [
                {
                    "ID": "TC-001",
                    "Kategorie": "Positive",
                    "Titel": "Erfolgreiche Ausführung",
                    "Vorbedingungen": "User eingeloggt",
                    "Testschritte": "1. Aktion ausführen",
                    "Erwartetes Ergebnis": "Erfolgsmeldung erscheint",
                    "Priorität": "Hoch",
                }
            ]
