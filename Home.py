import streamlit as st
import json as j

from streamlit_folium import folium_static, st_folium
from utils.map import Node, Edge, Map, get_port_poi_plot
from utils.state import define_session_states
from api.weather import findRoute
from constants import PORTS, MARITIME_POINTS

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

sailing_speed = st.select_slider(label="Select Sailing Speed Range", key="sail-range", options=list(range(10, 28 + 1)), value=(10, 28))
travel_duration = st.slider("Select Maximum Travel Duration (hours)", min_value=100, max_value=700, step=10, key="duration-selecter")

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
            f"from {source_dock} to {dest_dock}, travelling at an average of {sailing_speed[0]} knots to {sailing_speed[1]} knots within {travel_duration} hours!")

if st.button("Find Optimal Route", key="find_route") or st.session_state["find_route"]:
    with st.spinner("Generating..."):
        source_dock = PORTS.get(source_dock)
        dest_dock = PORTS.get(dest_dock)    
        st.session_state["maritime-df"], st.session_state["weather-df"], st.session_state["maritime-figure"], st.session_state["weather-figure"], st.session_state["route_list"] = \
            findRoute(source_dock, dest_dock, sailing_speed, travel_duration)
            
        # Parse the JSON string
        parsed_data = j.loads(st.session_state["route_list"])
        # Extract the route information
        route = parsed_data['route']
        # Save latitude and longitude as an array of tuples
        coordinates = [(index+1, point[0], point[1]) for index, point in enumerate(route)]
        # add source and destination to the coordinates
        coordinates.insert(len(coordinates),("DEST", dest_dock[0], dest_dock[1]))
        coordinates.insert(0, ("SOURCE", source_dock[0], dest_dock[1]))

        # Output the array of tuples
        print(coordinates)

        nodes = []
        edges = []

        for index, latitude, longitude in coordinates:
            nodes.append(Node(name=f"Node {index}", latitude=latitude, longitude=longitude))

        for i in range(len(nodes) - 1):
            print(f"Appending edge from {nodes[i].name} to {nodes[i + 1].name}")
            edges.append(Edge(source=nodes[i], destination=nodes[i + 1], weight=2.0))

        # Get the edge data in list format (source, destination, weight)
        edge_data = [edge.get() for edge in edges]

        st.subheader("Routes")
        st_folium(Map(1.29, 103.8, edges).plot(), width=700, height=500, returned_objects=[])

        # Create a list of formatted nodes
        st.write("Path:")

        for i in range(len(coordinates) - 1):
            node_from = coordinates[i]
            node_to = coordinates[i + 1]
            st.write(f"Node {node_from[0]} ({node_from[1]}, {node_from[2]}) ➡️ Node {node_to[0]} ({node_to[1]}, {node_to[2]})")
            
        # Final node
        st.write(f"Final Node: Node {coordinates[-1][0]} ({coordinates[-1][1]}, {coordinates[-1][2]})")
