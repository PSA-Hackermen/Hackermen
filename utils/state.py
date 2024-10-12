import streamlit as st

def define_session_states() -> None:
    if "maritime-df" not in st.session_state:
        st.session_state["maritime-df"] = None
    
    if "maritime-figure" not in st.session_state:
        st.session_state["maritime-figure"] = None
    
    if "weather-df" not in st.session_state:
        st.session_state["weather-df"] = None
    
    if "weather-figure" not in st.session_state:
        st.session_state["weather-figure"] = None

    if "show-port" not in st.session_state:
        st.session_state["show-port"] = False
    
    if "show-poi" not in st.session_state:
        st.session_state["show-poi"] = False
