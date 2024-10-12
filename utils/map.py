import folium
import streamlit as st

from streamlit_folium import st_folium

class Node:
    def __init__(self, name: str, latitude: float, longitude: float):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
    
    def get(self):
        return [self.latitude, self.longitude]

class Edge:
    def __init__(self, source: Node, destination: Node, weight: float):
        self.source = source
        self.destination = destination
        self.weight = weight
    
    def get(self, deep=False):
        return [self.source.get() if deep else self.source, self.destination.get() if deep else self.destination, self.weight]

class Map:
    def __init__(self, latitude, longitude, edges: list[Edge]):
        self.path = list
        self.latitude = latitude
        self.longitude = longitude
        self.edges = edges

    def plot(self, zoom_start=10):
        map = folium.Map(
            location=[self.latitude, self.longitude],
            zoom_start=zoom_start
        )

        for edge in self.edges:
            src, dst, weight = edge.get()

            folium.Marker(location=src.get(), tooltip=src.name, popup=src.name).add_to(map)
            folium.Marker(location=dst.get(), tooltip=dst.name, popup=dst.name).add_to(map)
            
            if weight < 0:
                folium.PolyLine([src.get(), dst.get()], color='green', weight=-weight, opacity=1).add_to(map)
            else:
                folium.PolyLine([src.get(), dst.get()], color='blue', weight=weight + 0.0001, opacity=1).add_to(map)

        map.fit_bounds(map.get_bounds(), padding=[15.0, 15.0])

        return map


def get_port_poi_plot(ports: dict[str, tuple], points_of_interest: dict[str, tuple]):
    if not ports or not points_of_interest:
        st.error("No ports or points of interest detected!")
        return

    # reduce the dicts into a list of values
    port_list = [(port[0], (port[1][0], port[1][1])) for port in ports.items()]
    poi_list = [(port[0], (port[1][0], port[1][1])) for port in points_of_interest.items()]
    
    # create the map
    map = folium.Map(
        location=port_list[0][1],
        zoom_start=10
    )

    # iterate and add the marker onto the map
    if st.session_state["show-port"]:
        port_feature = folium.FeatureGroup(name="Ports (Red)")
        for port, (src, dst) in port_list:
            folium.Marker(
                location=(src, dst), 
                tooltip=port, 
                popup=port,
                icon=folium.Icon(color="red", prefix="fa", icon="fa-ship", icon_color='white')
            ).add_to(port_feature)

        port_feature.add_to(map)
    
    if st.session_state["show-poi"]:
        poi_feature = folium.FeatureGroup(name="Points of Interest (Blue)")
        for poi, (src, dst) in poi_list:
            folium.Marker(
                location=(src, dst),
                tooltip=poi,
                popup=poi,
                icon=folium.Icon(color="blue", prefix="fa", icon="fa-anchor", icon_color='white')
            ).add_to(poi_feature)
    
        poi_feature.add_to(map)

    map.fit_bounds(map.get_bounds())
    return map
