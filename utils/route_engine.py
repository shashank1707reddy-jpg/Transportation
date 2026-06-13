# utils/route_engine.py

import heapq
import random
from utils.station_network import GRAPH


class RouteEngine:
    def __init__(self):
        self.graph = GRAPH

    # ---------------------------
    # Shortest Path (Dijkstra)
    # ---------------------------
    def shortest_path(self, source, destination):

        if source not in self.graph:
            return None

        distances = {
            node: float('inf')
            for node in self.graph
        }

        previous_nodes = {}

        distances[source] = 0

        priority_queue = [(0, source)]

        while priority_queue:

            current_distance, current_node = heapq.heappop(
                priority_queue
            )

            if current_node == destination:
                break

            neighbors = self.graph.get(
                current_node, {}
            )

            for neighbor, weight in neighbors.items():

                distance = (
                    current_distance + weight
                )

                if distance < distances.get(
                    neighbor, float('inf')
                ):
                    distances[neighbor] = distance

                    previous_nodes[
                        neighbor
                    ] = current_node

                    heapq.heappush(
                        priority_queue,
                        (distance, neighbor)
                    )

        # No route found
        if (
            destination
            not in previous_nodes
            and source != destination
        ):
            return None

        # Build route
        path = []

        current = destination

        while current != source:
            path.append(current)
            current = previous_nodes.get(current)

            if current is None:
                return None

        path.append(source)
        path.reverse()

        return {
            "route": path,
            "distance_km":
            round(
                distances[destination], 2
            )
        }

    # ---------------------------
    # Generate Bus Number
    # ---------------------------
    def generate_bus_number(self):

        prefixes = [
            "500D",
            "KBS",
            "VJ",
            "BMTC",
            "EXP",
            "KA"
        ]

        prefix = random.choice(
            prefixes
        )

        return (
            f"{prefix}-"
            f"{random.randint(10,999)}"
        )

    # ---------------------------
    # Generate Smart Buses
    # ---------------------------
    def generate_buses(
        self,
        route
    ):

        buses = []

        total_buses = random.randint(
            3, 7
        )

        for i in range(
            total_buses
        ):

            current_stop = random.choice(
                route
            )

            bus = {

                "bus_id":
                self.generate_bus_number(),

                "current_stop":
                current_stop,

                "occupancy":
                random.randint(20, 95),

                "speed":
                random.randint(25, 60),

                "delay_minutes":
                random.randint(0, 10),

                "status":
                random.choice([
                    "On Time",
                    "Delayed",
                    "Approaching",
                    "Moving"
                ]),

                "eta":
                random.randint(2, 20)
            }

            buses.append(bus)

        return buses

    # ---------------------------
    # Route + Bus Info
    # ---------------------------
    def get_route_info(
        self,
        source,
        destination
    ):

        result = self.shortest_path(
            source,
            destination
        )

        if not result:
            return {
                "success": False,
                "message":
                "No route found"
            }

        buses = self.generate_buses(
            result["route"]
        )

        return {

            "success": True,

            "source":
            source,

            "destination":
            destination,

            "route":
            result["route"],

            "distance_km":
            result["distance_km"],

            "bus_count":
            len(buses),

            "buses":
            buses
        }