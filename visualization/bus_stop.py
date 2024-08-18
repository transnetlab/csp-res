import folium
import networkx as nx
import osmnx as ox
import pandas as pd
import pickle


def extract_nearest_node(data, g):
    """
    finds the nearest node for given bus stop
    Parameters
    ----------
    data: dataframe
    g: Graph

    Returns
    -------
    nearest node from graph for each bus-stop_id
    """
    for index1, row1 in data.iterrows():
        lon = float(data[data.stop_id == row1.stop_id].stop_lon.values[0])
        lat = float(data[data.stop_id == row1.stop_id].stop_lat.values[0])
        data.loc[index1, ["node_number", "distance"]] = ox.nearest_nodes(g, lon, lat, return_dist=True)

    return None


def obtain_node_lat_lon(stop_id, graph_1, stop_df):
    """
    returns tuple of latitude and longitude for a given stop
    Parameters
    ----------
    stop_id: int
    graph_1: MultiDiGraph
    stop_df: Dataframe

    Returns
    -------
    lat, lon: tuple of latitude and longitude for a given stop
    """
    node_num = stop_df[stop_df.stop_id == stop_id].node_number.values[0]
    lat = graph_1.nodes[node_num]['y']
    lon = graph_1.nodes[node_num]['x']
    return lat, lon


def make_stop_sequence_dict(trip_df, stop_times_df, route_no):
    """
    makes a dictionary with stop sequence for every trip
    Parameters
    -------
    trip_df: Dataframe
    stop_times_df: Dataframe
    route_no: int

    Returns
    -------
    dict_t: dict
    """
    trip_id_l = list(trip_df[trip_df.route_id == route_no].trip_id)
    dict_t = {}
    df = stop_times_df[stop_times_df.trip_id.isin(trip_id_l)]
    for index_1, r in df.iterrows():
        if r.trip_id not in dict_t:
            dict_t[r.trip_id] = [r.stop_id]
        else:
            dict_t[r.trip_id].append(r.stop_id)
    return dict_t


def get_potential_stop_list(trip_df, stop_times_df):
    """
    makes a list with unique start/end stop every trip
    Parameters
    ----------
    trip_df: Dataframe
    stop_times_df: Dataframe

    Returns
    -------
    dict_t: dict
    """
    list_l = set()
    for trip in list(trip_df.trip_id):
        start_stop = stop_times_df[stop_times_df.trip_id == trip].stop_id.head(1).values[0]
        end_stop = stop_times_df[stop_times_df.trip_id == trip].stop_id.tail(1).values[0]
        list_l.add(start_stop)
        list_l.add(end_stop)
    return list_l


def find_trip_with_max_no_of_stops(dict_t):
    """
    finds trip_id with maximum number of stops
    Parameters
    ----------
    dict_t: dict

    Returns
    -------
    t_max_stop: int

    """
    max_len = 0
    t_max_stop = 0
    for k in dict_t:
        if max_len < len(dict_t[k]):
            max_len = len(dict_t[k])
            t_max_stop = k
    return t_max_stop


def add_tile_layer(map_bus_stop):
    """
    adds tile layer in folium map
    Parameters
    ----------
    map_bus_stop: folium map
    """
    # folium.TileLayer('https://{s}.tile.jawg.io/jawg-streets/{z}/{x}/{y}{r}.png?access-token={accessToken}',
    #                  attr='<a href="http://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy;<b>'
    #                       'Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
    #                       'contributors',
    #                  minZoom=0,
    #                  maxZoom=22,
    #                  subdomains='abcd',
    #                  accessToken='gw7eeERNnnCYsG1xqSREZI6pj5b5G0cyoR2CNmyJJGiCqKaC1msFMTBV8zhSnEq2').add_to(
    #     map_bus_stop)
    folium.TileLayer('https://{s}.tile.jawg.io/jawg-light/{z}/{x}/{y}{r}.png?access-token={accessToken}',
                     attr='<a href="http://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; '
                          '<b>Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                     minZoom=0,
                     maxZoom=22,
                     subdomains='abcd',
                     accessToken='gw7eeERNnnCYsG1xqSREZI6pj5b5G0cyoR2CNmyJJGiCqKaC1msFMTBV8zhSnEq2').add_to(
        map_bus_stop)


def add_marker_bus_stop(stops_df, map_bus_stop, color, size=1, alpha=1):
    """
    adds marker to each bus stop in the network
    Parameters
    ----------
    stops_df: Dataframe
    map_bus_stop: folium map
    size: float
    color: str
    alpha: float
    """
    for index, row in stops_df.iterrows():
        # folium.Marker([row.stop_lat, row.stop_lon],
        #               icon=folium.Icon(icon='bus', prefix='fa', markerColor='red')
        #               ).add_to(map_bus_stop)
        folium.CircleMarker((row.stop_lat, row.stop_lon),
                            radius=size,
                            fill_color=color,
                            fill_opacity=alpha,
                            color=color,
                            opacity=alpha
                            ).add_to(map_bus_stop)


def add_marker_route(dict_t, t_max_stops, my_map0):
    """
    adds marker to bus stop with ordering numbered in the route
    Parameters
    ----------
    dict_t: dict
    t_max_stops: int
    my_map0: folium map
    """
    for x in dict_t[t_max_stops]:
        folium.CircleMarker(obtain_node_lat_lon(x, G, stops),
                            radius=6,
                            fill_color='red',
                            fill_opacity=1,
                            color="red"
                            ).add_to(my_map0)
    i = 1
    if dict_t[t_max_stops][0] == dict_t[t_max_stops][-1]:
        for x in dict_t[t_max_stops][:-1]:
            icon = folium.DivIcon(
                html=f'<div style = font-weight: bold,  font-size: 100px><b>{i}</b></div>',
                icon_size=(7, 14)
            )
            folium.Marker(obtain_node_lat_lon(x, G, stops),
                          icon=icon
                          ).add_to(my_map0)
            i += 1
    else:
        for x in dict_t[t_max_stops][:]:
            icon = folium.DivIcon(
                html=f'<div style = font-weight: bold,  font-size: 100px><b>{i}</b></div>',
                icon_size=(7, 14)
            )
            folium.Marker(obtain_node_lat_lon(x, G, stops),
                          icon=icon
                          ).add_to(my_map0)
            i += 1


def add_route(dict_t, t_max_stops, map_r, stops_df):
    """
    adds route for even stop sequence
    Parameters
    ----------
    dict_t: dict
    t_max_stops: int
    map_r: folium map
    stops_df: Dataframe
    """
    for i in range(len(dict_t[t_max_stops]) - 1):
        try:
            origin = int(stops_df[stops.stop_id == dict_t[t_max_stops][i]].node_number.values[0])
            destination = int(stops_df[stops.stop_id == dict_t[t_max_stops][i + 1]].node_number.values[0])
            try:
                route_check = nx.shortest_path(G, origin, destination, weight="length", method='dijkstra')
                map_r = ox.plot_route_folium(G,
                                             route_check,
                                             route_map=map_r,
                                             tiles='OpenStreetMap',
                                             zoom=10,
                                             fit_bounds=True,
                                             weight=1.5,
                                             color="black")
            except nx.exception.NetworkXNoPath:
                pass
        except ValueError:
            pass


# loading data
network = 'Durham_2.1k'
folder_path = 'E:/PycharmProjects/CSP-Benders'
stops = pd.read_csv(fr"{folder_path}\{network}\stops.txt")
trips = pd.read_csv(fr"{folder_path}\{network}\trips.txt")
stop_times = pd.read_csv(fr"{folder_path}\{network}\stop_times.txt")
route = pd.read_csv(fr"{folder_path}\{network}\routes.txt")

# open charging location file
with open(fr"{folder_path}\{network}\52_scenario\overall_charging_locations_cs.pkl", 'rb') as f:
    charging_location = pickle.load(f)


# open depot file
with open(fr"{folder_path}\{network}\depot_updated.pkl", 'rb') as f:
    depot = pickle.load(f)


# min and max lat and lon for bounding box
min_lat = min(list(stops.stop_lat)) - 0.04
max_lat = max(list(stops.stop_lat)) + 0.04
min_lon = min(list(stops.stop_lon)) - 0.04
max_lon = max(list(stops.stop_lon)) + 0.04

# creating MultiDiGraph for given region
G = ox.graph_from_bbox(max_lat, min_lat, max_lon, min_lon, network_type="drive")

# finding nearest-node for each bus stop
extract_nearest_node(stops, G)

# list of all routes in the network
route_id_list = list(route.route_id.unique())

# finding route id with maximum no. of trips passing through
trips["count"] = 1
route_id_max_trip = trips.groupby(["route_id"]).sum().sort_values("count", ascending=False).head(1).index[0]
print(f"route with maximum number of trips is {route_id_max_trip}")

# saves bus_stop_visualisation in html file
# my_map_bus_stop = folium.Map(location=[(min_lat + max_lat) / 2, (min_lon + max_lon) / 2], png_enabled=True)
# add_marker_bus_stop(stops, my_map_bus_stop, "black")
# add_tile_layer(my_map_bus_stop)
# my_map_bus_stop.save(fr"{folder_path}\{network}\visualization\my_map_bus_stop.html")

# saves potential stops for charging and discharging
# potential_stop_l = potential_stop_list(trips, stop_times)
potential_stop_l = list(charging_location)
my_map_bus_stop = folium.Map(location=[(min_lat + max_lat) / 2, (min_lon + max_lon) / 2])
add_marker_bus_stop(stops, my_map_bus_stop, "black", size=0.5)
add_marker_bus_stop(stops[stops.stop_id.isin(potential_stop_l)], my_map_bus_stop, "red", size=3.5)
add_marker_bus_stop(stops[stops.stop_id.isin(depot)], my_map_bus_stop, "blue", size=5.5)
add_tile_layer(my_map_bus_stop)
my_map_bus_stop.save(fr"{folder_path}\{network}\visualization\my_map_potential_bus_stop.html")

# # to remove route for which no trips are assigned
# for route_id_x in route_id_list:
#     if len(list(trips[trips.route_id == route_id_x].trip_id)) == 0:
#         route_id_list.remove(route_id_x)

# # # to generate route visualization for each route id
# for route_id in route_id_list:
#
#     dict_trip = stop_sequence_dict(trips, stop_times, route_id)
#     trip_max_stop = trip_with_max_stop(dict_trip)
#     my_map0 = folium.Map(location=[(min_lat + max_lat) / 2, (min_lon + max_lon) / 2])
#     add_route(dict_trip, trip_max_stop, my_map0, stops)
#     add_marker_route(dict_trip, trip_max_stop, my_map0)
#     add_tile_layer(my_map0)
#
#     my_map0.save(f"./Canberra/route_{route_id}.html")
