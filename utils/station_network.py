# utils/station_network.py

STATIONS = {
    # WEST BENGALURU
    "Vijayanagar": (12.9719, 77.5367),
    "Nayandahalli": (12.9497, 77.5266),
    "RR Nagar": (12.9275, 77.5151),
    "Kengeri": (12.9081, 77.4833),
    "Mysore Road": (12.9467, 77.5301),
    "RV College": (12.9237, 77.4987),

    # CENTRAL
    "Majestic": (12.9784, 77.5723),
    "KR Market": (12.9605, 77.5736),
    "Cubbon Park": (12.9763, 77.5929),
    "MG Road": (12.9755, 77.6063),
    "Shivajinagar": (12.9833, 77.6033),
    "Rajajinagar": (12.9911, 77.5553),
    "Malleshwaram": (13.0035, 77.5700),

    # SOUTH
    "Jayanagar": (12.9293, 77.5828),
    "JP Nagar": (12.9077, 77.5850),
    "Banashankari": (12.9255, 77.5468),
    "BTM Layout": (12.9166, 77.6101),
    "Silk Board": (12.9170, 77.6220),
    "HSR Layout": (12.9116, 77.6474),
    "Electronic City": (12.8399, 77.6770),

    # EAST
    "Indiranagar": (12.9719, 77.6412),
    "Domlur": (12.9611, 77.6387),
    "Marathahalli": (12.9591, 77.6974),
    "Whitefield": (12.9698, 77.7499),
    "KR Puram": (13.0089, 77.6956),
    "Kadugodi": (12.9950, 77.7600),

    # NORTH
    "Hebbal": (13.0358, 77.5970),
    "Yeshwanthpur": (13.0285, 77.5401),
    "Peenya": (13.0329, 77.5273),
    "Nagasandra": (13.0475, 77.4932),
    "Jalahalli": (13.0465, 77.5480),

    # EXTRA STATIONS
    "Basavanagudi": (12.9417, 77.5755),
    "Lalbagh": (12.9507, 77.5848),
    "Ulsoor": (12.9845, 77.6200),
    "Bellandur": (12.9250, 77.6760),
    "Sarjapur": (12.9070, 77.6960),
    "Bommanahalli": (12.8998, 77.6245),
    "Koramangala": (12.9352, 77.6245),
    "Hosur Road": (12.9000, 77.6300),
    "Richmond Town": (12.9611, 77.6000),
    "Vasanth Nagar": (12.9916, 77.5923),
    "RT Nagar": (13.0222, 77.5946),
    "Frazer Town": (13.0005, 77.6145),
    "Kalyan Nagar": (13.0250, 77.6408),
    "Banaswadi": (13.0142, 77.6512),
    "Mahadevapura": (12.9916, 77.6950),
    "Brookefield": (12.9667, 77.7172),
    "Kundalahalli": (12.9564, 77.7114),
    "Hoodi": (13.0040, 77.7150),
    "Bommasandra": (12.8000, 77.7050),
    "Attibele": (12.7797, 77.7700),
    "Kengeri Satellite Town": (12.9045, 77.4839),
    "Chandra Layout": (12.9564, 77.5242),
    "Magadi Road": (12.9750, 77.5480),
    "Seshadripuram": (12.9935, 77.5710),
    "Town Hall": (12.9634, 77.5840),
}

# Graph Connections (Distance Weight in KM)

GRAPH = {

    # WEST
    "Vijayanagar": {
        "Rajajinagar": 5,
        "Nayandahalli": 3,
        "Chandra Layout": 2
    },

    "Nayandahalli": {
        "Vijayanagar": 3,
        "Mysore Road": 2,
        "RR Nagar": 4
    },

    "RR Nagar": {
        "Nayandahalli": 4,
        "RV College": 3,
        "Kengeri": 5
    },

    "RV College": {
        "RR Nagar": 3,
        "Kengeri": 4,
        "Banashankari": 5
    },

    "Kengeri": {
        "RV College": 4,
        "Kengeri Satellite Town": 2
    },

    # CENTRAL
    "Rajajinagar": {
        "Vijayanagar": 5,
        "Majestic": 3,
        "Malleshwaram": 3,
        "Yeshwanthpur": 3
    },

    "Majestic": {
        "Rajajinagar": 3,
        "KR Market": 2,
        "MG Road": 4,
        "Cubbon Park": 3
    },

    "KR Market": {
        "Majestic": 2,
        "Town Hall": 1,
        "Lalbagh": 2
    },

    "MG Road": {
        "Majestic": 4,
        "Cubbon Park": 1,
        "Ulsoor": 2,
        "Indiranagar": 4,
        "Richmond Town": 2
    },

    "Cubbon Park": {
        "MG Road": 1,
        "Vasanth Nagar": 2
    },

    # SOUTH
    "Jayanagar": {
        "JP Nagar": 3,
        "Banashankari": 3,
        "BTM Layout": 3,
        "Basavanagudi": 2
    },

    "JP Nagar": {
        "Jayanagar": 3,
        "Banashankari": 2
    },

    "Banashankari": {
        "Jayanagar": 3,
        "JP Nagar": 2,
        "RV College": 5,
        "BTM Layout": 4
    },

    "BTM Layout": {
        "Jayanagar": 3,
        "Koramangala": 2,
        "Silk Board": 3
    },

    "Koramangala": {
        "BTM Layout": 2,
        "Domlur": 3,
        "HSR Layout": 3
    },

    "HSR Layout": {
        "Koramangala": 3,
        "Silk Board": 2,
        "Bellandur": 4
    },

    "Silk Board": {
        "BTM Layout": 3,
        "HSR Layout": 2,
        "Electronic City": 8,
        "Bommanahalli": 2
    },

    "Electronic City": {
        "Silk Board": 8,
        "Bommasandra": 6,
        "Attibele": 7
    },

    # EAST
    "Indiranagar": {
        "MG Road": 4,
        "Domlur": 2,
        "Ulsoor": 2
    },

    "Domlur": {
        "Indiranagar": 2,
        "Koramangala": 3,
        "Marathahalli": 5
    },

    "Marathahalli": {
        "Domlur": 5,
        "Whitefield": 6,
        "Bellandur": 3,
        "Mahadevapura": 4
    },

    "Bellandur": {
        "Marathahalli": 3,
        "HSR Layout": 4
    },

    "Whitefield": {
        "Marathahalli": 6,
        "Kadugodi": 2,
        "Hoodi": 3
    },

    "KR Puram": {
        "Mahadevapura": 3,
        "Hoodi": 2
    },

    # NORTH
    "Hebbal": {
        "RT Nagar": 3,
        "Yeshwanthpur": 5,
        "Kalyan Nagar": 4
    },

    "Yeshwanthpur": {
        "Rajajinagar": 3,
        "Peenya": 4,
        "Hebbal": 5
    },

    "Peenya": {
        "Yeshwanthpur": 4,
        "Nagasandra": 3
    },

    "Nagasandra": {
        "Peenya": 3,
        "Jalahalli": 2
    },
    "Jalahalli": {
    "Nagasandra": 2,
    "Yeshwanthpur": 5
    },

    "Seshadripuram": {
        "Majestic": 2,
        "Malleshwaram": 2,
        "Rajajinagar": 2
    },

    "Town Hall": {
        "KR Market": 1,
        "Lalbagh": 2,
        "Richmond Town": 3
    },

    "Lalbagh": {
        "KR Market": 2,
        "Town Hall": 2,
        "Jayanagar": 3
    },

    "Richmond Town": {
        "MG Road": 2,
        "Town Hall": 3,
        "Cubbon Park": 2
    },

    "Ulsoor": {
        "MG Road": 2,
        "Indiranagar": 2,
        "Frazer Town": 3
    },

    "Frazer Town": {
        "Ulsoor": 3,
        "Shivajinagar": 2,
        "Banaswadi": 3
    },

    "Banaswadi": {
        "Frazer Town": 3,
        "Kalyan Nagar": 2,
        "KR Puram": 4
    },

    "Kalyan Nagar": {
        "Hebbal": 4,
        "Banaswadi": 2,
        "RT Nagar": 3
    },

    "RT Nagar": {
        "Hebbal": 3,
        "Vasanth Nagar": 4
    },

    "Vasanth Nagar": {
        "Cubbon Park": 2,
        "RT Nagar": 4,
        "Shivajinagar": 2
    },

    "Shivajinagar": {
        "MG Road": 2,
        "Frazer Town": 2,
        "Vasanth Nagar": 2
    },

    "Mahadevapura": {
        "Marathahalli": 4,
        "KR Puram": 3,
        "Brookefield": 3
    },

    "Brookefield": {
        "Mahadevapura": 3,
        "Kundalahalli": 2
    },

    "Kundalahalli": {
        "Brookefield": 2,
        "Whitefield": 4
    },

    "Hoodi": {
        "Whitefield": 3,
        "KR Puram": 2
    },

    "Bommanahalli": {
        "Silk Board": 2,
        "Hosur Road": 2
    },

    "Hosur Road": {
        "Bommanahalli": 2,
        "Electronic City": 5
    },

    "Bommasandra": {
        "Electronic City": 6,
        "Attibele": 5
    },

    "Attibele": {
        "Bommasandra": 5
    }
}