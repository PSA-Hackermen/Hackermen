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
