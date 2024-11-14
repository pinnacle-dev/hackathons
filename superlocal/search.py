from rcs_types import Coordinates, RCSMessage
from rcs import Action, Card
from messages import search_actions
import requests
import os
from math import radians, cos, sin, sqrt, atan2


nearby_search_dict = {
    "parks": {"type": "park", "keyword": ""},
    "parking": {"type": "parking", "keyword": ""},
    "fun_activities": {"type": "", "keyword": "fun activities"},
    "cafes": {"type": "cafe", "keyword": "wifi"},
    "restaurants": {"type": "restaurant", "keyword": ""},
}


def search(searchType: str, location: Coordinates) -> RCSMessage:
    if searchType == "restroom":
        return restroom_search(location)
    elif searchType in nearby_search_dict:
        return nearby_search(searchType, location)
    else:
        raise ValueError("Invalid search type: " + searchType)


def restroom_search(location: Coordinates) -> RCSMessage:
    print("Searching for a restroom near " + str(location))
    response = requests.get(
        "https://www.refugerestrooms.org/api/v1/restrooms/by_location",
        params={
            "lat": location["lat"],
            "lng": location["lng"],
            "page": 1,
            "per_page": 5,
        },
    )

    if response.status_code == 200:
        restrooms = response.json()[:5]
        return {
            "cards": [
                Card(
                    title=(
                        restroom["name"]
                        + f"{'🚻' if restroom['unisex'] else '🚹🚺'}"
                        + (f" {'🍼'}" if restroom["changing_table"] else "")
                    ),
                    subtitle=(
                        f"{restroom['street']}, {restroom['city']}, {restroom['state']}\n"
                        f"{round(restroom['distance'], 2)} miles away (~ {round(restroom['distance'] * 20)} mins)\n"
                        f"Directions: {restroom['directions']}"
                    ),
                    media_url="https://i.ibb.co/k45QW9B/restroom.webp",
                    buttons=[
                        Action(
                            title="Apple Maps",
                            type="openUrl",
                            payload=(
                                f"https://maps.apple.com/?daddr="
                                f"{restroom['latitude']},{restroom['longitude']}"
                            ),
                        ),
                        Action(
                            title="Google Maps",
                            type="openUrl",
                            payload=(
                                f"https://www.google.com/maps/dir/?api=1&destination="
                                f"{restroom['latitude']},{restroom['longitude']}"
                            ),
                        ),
                    ],
                )
                for restroom in restrooms
            ],
            "quick_replies": search_actions,
        }
    else:
        return {
            "text": "Sorry, I couldn't find any restrooms near you. Please try again later.",
            "quick_replies": search_actions,
        }


def nearby_search(searchType: str, location: Coordinates) -> RCSMessage:
    api_key = os.environ["GOOGLE_API_KEY"]
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{location['lat']},{location['lng']}",
        "radius": 1000,
        "type": nearby_search_dict[searchType]["type"],
        "keyword": nearby_search_dict[searchType]["keyword"],
        "opennow": True,
        "key": api_key,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        places = response.json().get("results", [])[:5]
        return {
            "cards": [
                Card(
                    title=place["name"],
                    subtitle=(
                        f"{place['vicinity']}\n"
                        f"Rating: {place.get('rating', 'N/A')} ({place.get('user_ratings_total', '0')} reviews)\n"
                        f"{distance_estimation(location, place['geometry']['location'])}"
                    ),
                    media_url=(
                        f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={place['photos'][0]['photo_reference']}&key={api_key}"
                        if "photos" in place and len(place["photos"]) > 0
                        else None
                    ),
                    buttons=[
                        Action(
                            title="Apple Maps",
                            type="openUrl",
                            payload=(
                                f"https://maps.apple.com/?daddr="
                                f"{place['geometry']['location']['lat']},{place['geometry']['location']['lng']}"
                            ),
                        ),
                        Action(
                            title="Google Maps",
                            type="openUrl",
                            payload=(
                                f"https://www.google.com/maps/dir/?api=1&destination="
                                f"{place['geometry']['location']['lat']},{place['geometry']['location']['lng']}"
                            ),
                        ),
                    ],
                )
                for place in places
            ],
            "quick_replies": search_actions,
        }
    else:
        return {
            "text": "Sorry, I couldn't find any places near you. Please try again later.",
            "quick_replies": search_actions,
        }


def distance_estimation(origin: Coordinates, destination: Coordinates):
    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 3958.8  # Radius of the Earth in miles

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    distance = haversine_distance(
        origin["lat"], origin["lng"], destination["lat"], destination["lng"]
    )
    return f"({round(distance, 2)} miles away, ~ {round(distance * 20)} mins walk)\n"
