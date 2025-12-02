import heapq
from .graph import Abington_Map, Buildings

def shortest_path(graph, start, end):
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

def closest_building_path(graph, start):
    results = []
    for building in Buildings:
        result = shortest_path(graph, start, building)
        results.append(result)
    results.sort()
    print(results[0])
    return results[0]

if __name__ == "__main__":
    distance, route = shortest_path(Abington_Map, "Woodland Building", "AN")
    print("Shortest Distance:", distance)
    print("Route: ", " → ".join(route))


