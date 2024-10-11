import streamlit as st

from streamlit_folium import folium_static, st_folium
from utils.map import Node, Edge, Map
from api.weather import findRoute
from constants import PORTS

st.image("assets/image.png")
st.header("Hackermen")

col1, col2 = st.columns(2)

source_dock = col1.selectbox("Select your Starting Port", options=PORTS, key="source_port")
dest_dock = col2.selectbox("Select your Destination Port", options=[ports for ports in PORTS if ports != source_dock], key="destination_port")

if st.button("Find optimal route", key="find_route") or st.session_state["find_route"]:
    st.subheader("Raw Data")
    result = st.dataframe(findRoute(source_dock, dest_dock))

    st.subheader("Routes")
    node1 = Node(name="A", latitude=1.290270, longitude=103.851959)  # Singapore
    node2 = Node(name="B", latitude=1.352083, longitude=103.819836)  # Another point in Singapore
    node3 = Node(name="C", latitude=1.364917, longitude=103.822872)  # Another point in Singapore

    # Creating edges between nodes
    edge1 = Edge(source=node1, destination=node2, weight=2.0)  # Edge with weight 2.0
    edge2 = Edge(source=node2, destination=node3, weight=5.0)  # Edge with weight 5.0
    edge3 = Edge(source=node1, destination=node3, weight=-8.0)  # Edge with weight 8.0

    # List of edges
    edges = [edge1, edge2, edge3]

    # Get the edge data in list format (source, destination, weight)
    edge_data = [edge.get() for edge in edges]

    st_folium(Map(1.29, 103.8, edges).plot(), width=700, height=500, returned_objects=[])

    st.info("Blue Lines represents normal paths, while Green Lines represents greener paths")