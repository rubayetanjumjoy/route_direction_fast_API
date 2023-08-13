import osmnx as ox

# Define the location (e.g., Dhaka)
location = 'Dhaka, Bangladesh'

# Define the custom filter to include only roads for cars and bikes
custom_filter = (
    '["area"!~"yes"]'
    '["highway"~"motorway|trunk|primary|secondary|tertiary|unclassified|residential|service|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link"]'
    '["motor_vehicle"!~"no"]'
    '["bicycle"!~"no"]'
    '["service"!~"parking|parking_aisle|driveway|emergency_access"]'
)

# Create the graph using the custom filter
graph = ox.graph_from_place(location, custom_filter=custom_filter)

# Save the graph to a GraphML file
ox.save_graphml(graph, filepath='Dhaka_Car_Bike_Roads.graphml')