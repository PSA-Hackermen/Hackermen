import streamlit as st

from api.weather import findRoute
from constants import PORTS

st.image("assets/image.png")
st.header("Hackermen")

col1, col2 = st.columns(2)

source_dock = col1.selectbox("Select your Starting Port", options=PORTS, key="source_port")
dest_dock = col2.selectbox("Select your Destination Port", options=[ports for ports in PORTS if ports != source_dock], key="destination_port")

if st.button("Find optimal route", key="find"):
    result = findRoute()
    st.success(result)
