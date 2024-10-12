import streamlit as st

from streamlit_folium import folium_static, st_folium
from utils.map import Node, Edge, Map, get_port_poi_plot
from utils.state import define_session_states
from api.weather import findRoute
from constants import PORTS, MARITIME_POINTS, SAILING_SPEEDS, TRAVEL_DURATIONS

# declare session states
define_session_states()

st.image("assets/image.png")

st.header("Hackermen")
st.markdown("Use this page to generate the safest and most sustainable routes from one Port to another.")

st.subheader("Select Ports")
st.markdown("Select the starting and destination port to begin charting a route!")

col1, col2 = st.columns(2)
source_dock = col1.selectbox("Select your Starting Port", options=PORTS, key="source_port")
dest_dock = col2.selectbox("Select your Destination Port", options=[ports for ports in PORTS if ports != source_dock], key="destination_port")

selected_speed = st.selectbox("Select Sailing Speed Range", options=[desc for desc, _ in SAILING_SPEEDS])
sailing_speed = next(value for desc, value in SAILING_SPEEDS if desc == selected_speed)

travel_duration = st.selectbox("Select Travel Duration (hours)", options=TRAVEL_DURATIONS)


with st.expander("See Port Locations and Points of Interest"):
    st.subheader("Port Location")
    
    inner_col1, inner_col2 = st.columns(2)

    st.session_state["show-port"] = inner_col1.checkbox("Display Ports", key="can-show-port", value=True)
    st.session_state["show-poi"] = inner_col2.checkbox("Display Points of Interest", key="can-show-poi", value=False)

    if not st.session_state["show-port"] and not st.session_state["show-poi"]:
        st.info("Select either options to begin visualising port/points of interest location!")

    st_folium(get_port_poi_plot(PORTS, MARITIME_POINTS), key="port-loc", width=700)

st.subheader("Generate Route")
st.markdown("Once you are ready, hit the **\"Find optimal route\"** button below to begin finding the optimal path "
            f"from {source_dock} to {dest_dock}!")
if st.button("Find optimal route", key="find_route") or st.session_state["find_route"]:
    with st.spinner("Generating..."):
        st.session_state["df"], st.session_state["figure"], st.session_state["route"] = findRoute(source_dock, dest_dock, sailing_speed, travel_duration)

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
