from fastapi import FastAPI,Request

import time
import osmnx as ox
import math
import polyline

graph=ox.load_graphml('Dhaka_Car_Bike_Roads.graphml')
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on the Earth's surface
    using the Haversine formula.
    """
    # Convert coordinates from degrees to radians
    lat1, lon1 = math.radians(lat1), math.radians(lon1)
    lat2, lon2 = math.radians(lat2), math.radians(lon2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of the Earth in kilometers
    R = 6371

    # Calculate the distance in kilometers
    distance = R * c

    return distance


def polyline_distance(polyline):
    """
    Calculate the total distance of a polyline.
    """
    distance = 0

    # Iterate through each pair of consecutive points
    for i in range(len(polyline) - 1):
        lat1, lon1 = polyline[i]
        lat2, lon2 = polyline[i + 1]
        distance += haversine(lat1, lon1, lat2, lon2)

    return distance*1000
app = FastAPI()
@app.get("/direction")
async def get_direction(request: Request):
    coordinates = request.query_params.get('coordinates')
    
    
    index_b=coordinates.index('b')
       
    part1=coordinates[:index_b]
    part2=coordinates[index_b+1:]
    part1_index_a=part1.index('a')
    part2_index_a=part2.index('a')

    lng_1st=part1[:part1_index_a]
    lat_1st=part1[part1_index_a+1:]
    lng_2nd=part2[:part2_index_a]
    lat_2nd=part2[part2_index_a+1:]
    # Find the index of 'b'
    index_b = coordinates.index('b')

    # Split the coordinates into two parts: before and after 'b'
    part1 = coordinates[:index_b]
    part2 = coordinates[index_b + 1:]

    # Find the indices of 'a' in both parts
    part1_index_a = part1.index('a')
    part2_index_a = part2.index('a')

    # Extract the longitude and latitude values from the parts
    lng_1st = float(part1[:part1_index_a])
    lat_1st = float(part1[part1_index_a + 1:])
    lng_2nd = float(part2[:part2_index_a])
    lat_2nd = float(part2[part2_index_a + 1:])
    print("Longitude 1st:", lng_1st)
    print("Latitude 1st:", lat_1st)
    print("Longitude 2nd:", lng_2nd)
    print("Latitude 2nd:", lat_2nd)
    optimizer = 'travel_time'    
    # # Create the graph from place
    # graph = ox.graph_from_place(place, network_type=network_type)

    # # Save the graph as a GraphML file
    # ox.save_graphml(graph, filename='dhaka.graphml')
    
    start_time = time.time()

    # Load the graph from the GraphML file for offline use
    
    
    

    # Define the start and end locations in latlng
    start_latlng = (lat_1st, lng_1st)
    end_latlng = (lat_2nd, lng_2nd) 
    
    # custom weight
 
    # def custom_weight(u, v, data):
    #     road_type = data.get("highway", "")
    #     if "motorway" in road_type or "trunk" in road_type or "primary" in road_type:
    #         return data["length"]  # Main roads
    #     elif "secondary" in road_type or "tertiary" in road_type:
    #         return data["length"] * 2  # Mid-level roads
    #     else:
    #         return data["length"] * 5  # Smaller, narrow roads

    # # Calculate custom weights
    # for u, v, data in graph.edges(data=True):
    #     data['custom_weight'] = custom_weight(u, v, data)

    # # Other code to load graph and define start and end locations...

    # optimizer = 'custom_weight'

    # Find the nearest node to the start and end locations
    orig_node = ox.distance.nearest_nodes(graph, start_latlng[1], start_latlng[0])
    dest_node = ox.distance.nearest_nodes(graph, end_latlng[1], end_latlng[0])

    # Calculate the shortest path using the custom weight
    shortest_route = ox.shortest_path(graph, orig_node, dest_node, weight=optimizer)

    print('test')
    x = []
    y = []
    for u, v in zip(shortest_route[:-1], shortest_route[1:]):
        # if there are parallel edges, select the shortest in length
        data = min(graph.get_edge_data(u, v).values(), key=lambda d: d["length"])
        if "geometry" in data:
            # if geometry attribute exists, add all its coords to list
            xs, ys = data["geometry"].xy
            x.extend(xs)
            y.extend(ys)
        else:
            # otherwise, the edge is a straight line from node to node
            x.extend((graph.nodes[u]["x"], graph.nodes[v]["x"]))
            y.extend((graph.nodes[u]["y"], graph.nodes[v]["y"]))
    coords=[]
    for i in range(len(x)):
        coords.append([y[i],x[i]])
    # coords.append([lat_2nd,lng_2nd])
    # print(coords)
    
    distance = polyline_distance(coords)
    print("Total distance of the polyline:", distance, "kilometers")
    # coordinates = []
    # for node in shortest_route:
    #     lat = graph.nodes[node]['y']
    #     lon = graph.nodes[node]['x']
    #     coordinates.append([lon, lat])

    # print("Coordinates of nodes in the shortest route:")
    # print(coordinates)
    end_time = time.time()
    time_taken = end_time - start_time
    print("Time taken: {:.2f} seconds".format(time_taken))
    distance_km=distance//1000
    duration_hour=(distance_km/40)*60*60

    encode_line=polyline.encode(coords, 6)
    response_dict={}
    response_dict['routes']=[
        {
            "time":duration_hour,
            "duration":duration_hour,
            "distance":distance,
            
            "mode": "driving",
            "hist_time": duration_hour,
            
            "geometry":encode_line,

            }
            ]
    response_dict['waypoints']=[
            {
        "name": "",
        "location":[ 
            lng_1st,
            lat_1st
            ]
        },
            {
        "name": "",
        "location":[ 
            lng_2nd,
            lat_2nd
            ]
        }
    ]
    response_dict["code"]= "Ok"
    response_dict["uuid"]= "cee31bef-871a-4308-9dc6-0334466c5890"
    response_dict["diff_path"]= 187.36791610717773
    
    return response_dict
   


