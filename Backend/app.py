import heapq
from .graph import *

def shortest_path(graph, start, end):
    """
    Return shortest path and distance using Dijkstra's algorithm.
    """
    p_queue = [(0, start, [])]
    visited = set()

    while p_queue:
        dist, node, path = heapq.heappop(p_queue)

        if node in visited:
            continue

        visited.add(node)
        path = path + [node]

        if node == end:
            return dist, path
        
        for neighbor, weight in graph[node]:
            if neighbor not in visited:
                heapq.heappush(p_queue, (dist + weight, neighbor, path))
 
    return float('inf'), []

def k_shortest_paths(graph, start, end, k=5):
    """
    Return up to k shortest paths from start to end in the graph.
    """
    queue = [(0, [start])]
    shortest_paths = []

    while queue and len(shortest_paths) < k:
        dist, path = heapq.heappop(queue)
        last_node = path[-1]

        if last_node == end:
            shortest_paths.append((dist, path))
            continue

        for neighbor, weight in graph[last_node]:
            if neighbor not in path:
                heapq.heappush(queue, (dist + weight, path + [neighbor]))

    return shortest_paths

def closest_building_path(graph, start):
    """
    Find the shortest path from start to the nearest building.
    """
    results = []
    for building in Buildings:
        result = shortest_path(graph, start, building)
        results.append(result)
    results.sort(key=lambda x: x[0])
    return results[0]

def closest_exit_path(graph, start):
    """
    Find the shortest path from start to the nearest Woodland exit.
    """
    results = []
    for exit in Woodland_Exits:
        result = shortest_path(graph, start, exit)
        results.append(result)
    results.sort(key=lambda x: x[0])
    return results[0]

# Old Testing Data
if __name__ == "__main__":
    distance, route = shortest_path(Abington_Map, "Woodland Building", "AN")
    print("Shortest Distance:", distance)
    print("Route: ", " → ".join(route))

    paths = k_shortest_paths(Abington_Map, "Woodland Building", "AN")
    print(paths)

