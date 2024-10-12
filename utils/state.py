import streamlit as st

def define_session_states() -> None:
    if "df" not in st.session_state:
        st.session_state["df"] = None
    
    if "figure" not in st.session_state:
        st.session_state["figure"] = None
    
    if "show-port" not in st.session_state:
        st.session_state["show-port"] = False
    
    if "show-poi" not in st.session_state:
        st.session_state["show-poi"] = False
