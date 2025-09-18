from datetime import datetime
from google.genai import Client
from os import getenv
import requests
from typing import List


def get_ideal_dive_months(animals: List[str], country: str) -> dict:
    """
    Given a country name, return the ideal months to dive there.

    Args:
        animals: A list of marine animals the user wants to see.
        country: The country name as a string.
    """

    client = Client()

    prompt = f"""
    The user wants to dive in: "{country}".
    The user wants to see these marine animals: {", ".join(animals)}.

    What are the ideal months to see those animals while scuba diving in that location?
    Return the months as a comma-separated list of month names (e.g., "June, July, August").
    Only return the month names, nothing else.
    """

    response = client.models.generate_content(
        model=getenv("MODEL_ID"),
        contents=prompt,
    )

    months = response.text.strip()
    return months


def get_slug(airport_code):
    url = f"https://api.skypicker.com/umbrella/v2/graphql?featureName=UmbrellaPlacesTermQuery&query=query+UmbrellaPlacesTermQuery%28+%24search%3A+PlacesSearchInput+%24filter%3A+PlacesFilterInput+%24options%3A+PlacesOptionsInput+%29+%7B+places%28search%3A+%24search%2C+filter%3A+%24filter%2C+options%3A+%24options%2C+first%3A+20%29+%7B+__typename+...+on+AppError+%7B+error%3A+message+%7D+...+on+PlaceConnection+%7B+metadata+%7B+firstResultStations+%7B+edges+%7B+node+%7B+...+on+Place+%7B+__isPlace%3A+__typename+__typename+id+legacyId+name+slug+slugEn+gps+%7B+lat+lng+%7D+rank+...+on+City+%7B+code+autonomousTerritory+%7B+legacyId+id+%7D+subdivision+%7B+legacyId+name+id+%7D+country+%7B+legacyId+name+slugEn+region+%7B+legacyId+continent+%7B+legacyId+id+%7D+id+%7D+id+%7D+airportsCount+groundStationsCount+%7D+...+on+Station+%7B+type+code+gps+%7B+lat+lng+%7D+city+%7B+legacyId+name+slug+autonomousTerritory+%7B+legacyId+id+%7D+subdivision+%7B+legacyId+name+id+%7D+country+%7B+legacyId+name+region+%7B+legacyId+continent+%7B+legacyId+id+%7D+id+%7D+id+%7D+id+%7D+%7D+...+on+Region+%7B+continent+%7B+legacyId+id+%7D+%7D+...+on+Country+%7B+code+region+%7B+legacyId+continent+%7B+legacyId+id+%7D+id+%7D+%7D+...+on+AutonomousTerritory+%7B+country+%7B+legacyId+name+region+%7B+legacyId+continent+%7B+legacyId+id+%7D+id+%7D+id+%7D+%7D+...+on+Subdivision+%7B+country+%7B+legacyId+name+region+%7B+legacyId+continent+%7B+legacyId+id+%7D+id+%7D+id+%7D+%7D+%7D+id+%7D+sphericalDistance+%7B+distance+%7D+carDirections+%7B+distance+duration+%7D+%7D+%7D+%7D+edges+%7B+rank+distance+%7B+__typename+distance+%7D+isAmbiguous+node+%7B+__typename+__isPlace%3A+__typename+id+legacyId+name+slug+slugEn+gps+%7B+lat+lng+%7D+rank+...+on+City+%7B+code+autonomousTerritory+%7B+legacyId+id+%7D+subdivision+%7B+legacyId+name+id+%7D+country+%7B+legacyId+name+slugEn+region+%7B+legacyId+continent+%7B+legacyId+id+%7D+id+%7D+id+%7D+airportsCount+groundStationsCount+%7D+...+on+Station+%7B+type+code+gps+%7B+lat+lng+%7D+city+%7B+legacyId+name+slug+autonomousTerritory+%7B+legacyId+id+%7D+subdivision+%7B+legacyId+name+id+%7D+country+%7B+legacyId+name+region+%7B+legacyId+continent+%7B+legacyId+id+%7D+id+%7D+id+%7D+id+%7D+%7D+...+on+Region+%7B+continent+%7B+legacyId+id+%7D+%7D+...+on+Country+%7B+code+region+%7B+legacyId+continent+%7B+legacyId+id+%7D+id+%7D+%7D+...+on+AutonomousTerritory+%7B+country+%7B+legacyId+name+region+%7B+legacyId+continent+%7B+legacyId+id+%7D+id+%7D+id+%7D+%7D+...+on+Subdivision+%7B+country+%7B+legacyId+name+region+%7B+legacyId+continent+%7B+legacyId+id+%7D+id+%7D+id+%7D+%7D+%7D+%7D+%7D+%7D+%7D&variables=%7B%22search%22%3A%7B%22term%22%3A%22{airport_code}%22%7D%2C%22filter%22%3A%7B%22onlyTypes%22%3A%5B%22AIRPORT%22%5D%7D%2C%22options%22%3A%7B%22locale%22%3A%22en%22%2C%22stationsQueryOptimisation%22%3Atrue%2C%22position%22%3A%7B%22lat%22%3A37%2C%22lng%22%3A-114%7D%2C%22sortBy%22%3A%22RANK_DISTANCE_TERM%22%7D%7D"  # noqa: E501
    resp = requests.get(url)

    data = resp.json()
    try:
        places = data["data"]["places"]["edges"]
        for place in places:
            node = place["node"]
            if node.get("code") == airport_code:
                return node.get("slug")
    except (KeyError, IndexError, TypeError):
        return None


def get_user_input():
    MAX_LOCATION_LENGTH = 50
    MAX_DIVERS = 4
    MAX_NIGHTS = 14
    MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]  # noqa: E501

    # ask user where they want to dive
    location = input("Where do you want to dive? ")
    if len(location) > MAX_LOCATION_LENGTH:
        print(f"Location is too long. Truncating to {MAX_LOCATION_LENGTH} characters.")
        location = location[:MAX_LOCATION_LENGTH]

    # ask user how many divers
    num_divers = int(input("How many divers? "))
    if num_divers <= 0:
        print("You must have at least one diver. Setting to 1.")
        num_divers = 1
    elif num_divers > MAX_DIVERS:
        print(f"Too many divers. Setting to maximum of {MAX_DIVERS}.")
        num_divers = MAX_DIVERS

    # ask user how many days
    num_nights = int(input("How many nights would you like to spend there? "))
    if num_nights <= 0:
        print("You must stay at least one night. Setting to 1.")
        num_nights = 1
    elif num_nights > MAX_NIGHTS:
        print(f"Too many nights. Setting to maximum of {MAX_NIGHTS}.")
        num_nights = MAX_NIGHTS

    # ask user what animals they want to see
    animals = input("Are there any specific marine animals you want to see? Give them as a comma delimited list (e.g., sharks, manta rays, turtles) ")  # noqa: E501
    animals = [a.strip() for a in animals.split(",") if a.strip()]
    if not animals:
        print("You must specify at least one marine animal. Setting to 'sharks'.")
        animals = ["sharks"]
    elif len(animals) > 5:
        print("Too many animals. Setting to first 5.")
        animals = animals[:5]
    print(f"Animals to see: {', '.join(animals)}")

    # find out which month they want to go
    print(f"Finding ideal months to see {', '.join(animals)} in {location}...")
    ideal_months = get_ideal_dive_months(animals, location)
    print(f"Ideal months to dive in {location.title()}: {ideal_months}")
    month = input("Which month would you like to go in? ")
    if month.title() not in MONTHS:
        first_month = ideal_months.split(",")[0].strip()
        print(f"{month} is not a valid month. Setting to {first_month}.")
        month = first_month
    if month.title() not in ideal_months:
        print(f"Warning: {month} is not in the ideal months to dive in {location}.")
    year = input("Which year? ")
    if int(year) < datetime.now().year or (int(year) == datetime.now().year and datetime.now().month > datetime.strptime(month, "%B").month):  # noqa: E501
        print("You cannot book a trip in the past. Setting year to next year.")
        year = str(datetime.now().year + 1)
    departure_location = input("What is your departure airport (3-letter IATA code, e.g. LAS)? ")
    if len(departure_location) != 3 or not departure_location.isalpha():
        print("Invalid IATA code. Setting to LAS.")
        departure_location = "LAS"
    departure_location = departure_location.upper()

    return animals, location, num_divers, num_nights, month, year, departure_location
