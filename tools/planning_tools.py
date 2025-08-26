# tools/planning_tools.py

import datetime
import random
from typing import List, Optional, Dict, Any

FlightDetails = str
HotelDetails = str

def flight_search_tool(
    origin_city: str,
    destination_city: str,
    start_date: str,
    end_date: str,
    adults: int,
) -> List[Dict[str, Any]]:
    """
    Searches for flights and returns a list of dictionaries,
    each representing a flight option.
    """
    is_round_trip = True
    if not end_date or end_date.strip() == "":
        is_round_trip = False

    airlines = ["Indigo", "Vistara", "Air India", "SpiceJet", "Emirates",
                "Singapore Airlines", "Qatar Airways", "Lufthansa", "British Airways"]
    mock_flight_options = []

    for _ in range(random.randint(2, 4)):
        airline = random.choice(airlines)
        price = random.randint(150, 650) * 100
        dep_flight_num = f"{airline[:2].upper()}-{random.randint(100, 999)}"
        dep_hour = random.randint(5, 20)
        dep_minute = random.choice([0, 15, 30, 45])
        arr_hour = dep_hour + random.randint(2, 8)
        arr_minute = random.choice([0, 15, 30, 45])

        departure_str = (
            f"DEPART: {airline} {dep_flight_num} from {origin_city} at {dep_hour:02d}:{dep_minute:02d}, "
            f"arriving {destination_city} at {arr_hour % 24:02d}:{arr_minute:02d}."
        )

        option_dict = {
            "airline": airline,
            "total_price": 0,
            "outbound": {
                "flight_number": dep_flight_num,
                "from": origin_city,
                "to": destination_city,
                "depart_time": f"{dep_hour:02d}:{dep_minute:02d}",
                "arrive_time": f"{arr_hour % 24:02d}:{arr_minute:02d}"
            },
            "return": None,
            "description": ""
        }

        if is_round_trip:
            price += random.randint(140, 600) * 100
            ret_flight_num = f"{airline[:2].upper()}-{random.randint(100, 999)}"
            ret_dep_hour = random.randint(5, 20)
            ret_dep_minute = random.choice([0, 15, 30, 45])
            ret_arr_hour = ret_dep_hour + random.randint(2, 8)
            ret_arr_minute = random.choice([0, 15, 30, 45])

            return_str = (
                f"RETURN: {airline} {ret_flight_num} from {destination_city} at {ret_dep_hour:02d}:{ret_dep_minute:02d}, "
                f"arriving {origin_city} at {ret_arr_hour % 24:02d}:{ret_arr_minute:02d}."
            )

            option_dict["return"] = {
                "flight_number": ret_flight_num,
                "from": destination_city,
                "to": origin_city,
                "depart_time": f"{ret_dep_hour:02d}:{ret_dep_minute:02d}",
                "arrive_time": f"{ret_arr_hour % 24:02d}:{ret_arr_minute:02d}"
            }
            option_dict["description"] = f"Round-Trip with {airline}: {departure_str} {return_str} Total Price: ₹{price}"
        else:
            option_dict["description"] = f"One-Way with {airline}: {departure_str} Price: ₹{price}"

        option_dict["total_price"] = price
        mock_flight_options.append(option_dict)

    return mock_flight_options


def hotel_search_tool(
    location: str,
    check_in_date: str,
    check_out_date: str,
    number_of_adults: int,
    budget_per_night: int
) -> List[Dict[str, Any]]:
    """
    Searches for hotels and returns a list of structured dictionaries.
    """
    hotel_database = {
        "okinawa": [
            {"name": "Halekulani Okinawa", "price": 35000, "desc": "Luxury 5-star hotel with stunning ocean views."},
            {"name": "Hyatt Regency Seragaki Island", "price": 25000, "desc": "Resort on its own private island."}
        ],
        "paris": [{"name": "Ritz Paris", "price": 80000, "desc": "Iconic luxury hotel near the Louvre."}],
        "london": [{"name": "The Savoy", "price": 65000, "desc": "Legendary hotel on the River Thames."}],
    }

    location_key = location.lower()
    options_in_location = []
    for key in hotel_database:
        if key in location_key:
            options_in_location = hotel_database[key]
            break

    if not options_in_location:
        return []

    final_options = []
    for hotel in options_in_location:
        if budget_per_night == 0 or hotel["price"] <= budget_per_night:
            hotel_dict = {
                "name": hotel["name"],
                "price_per_night": hotel["price"],
                "description": hotel["desc"],
                "full_details_string": f"{hotel['name']}: {hotel['desc']} Price: ₹{hotel['price']}/night."
            }
            final_options.append(hotel_dict)

    if not final_options:
        return []

    return final_options


def mock_book_flight(flight_details: str, number_of_adults: int, trip_type: str) -> str:
    """
    Simulates booking a selected flight for a number of adults.
    """
    flight_number = flight_details.split(':')[0]
    confirmation_id = f"HLD{random.randint(100000, 999999)}"

    return (
        f"Alright, I've placed a temporary hold on the {trip_type} reservation for {number_of_adults} adult(s) on {flight_number}. "
        f"Your reservation ID is {confirmation_id}. "
        "To complete the booking, you'll need to follow the payment link I've sent to your email. What's next?"
    )


def mock_book_hotel(hotel_details: str, number_of_adults: int) -> str:
    """
    Simulates placing a hold on a selected hotel room.
    """
    hotel_name = hotel_details.split(':')[0]
    confirmation_id = f"STAY{random.randint(100000, 999999)}"

    return (
        f"Okay, I've successfully placed a hold on your stay for {number_of_adults} adult(s) at {hotel_name}. "
        f"Your reservation ID is {confirmation_id}. "
        "Please follow the secure payment link I've sent to your email to confirm your booking. Can I help with anything else?"
    )
