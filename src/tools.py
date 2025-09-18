from calendar import monthrange
from datetime import date, timedelta, datetime
from google.genai import Client
from os import getenv
from pandas import read_csv
import requests
from smolagents import Tool, tool

from src.utils import get_slug


@tool
def get_country_id(location: str) -> dict:
    """
    Given a dive location (e.g., 'Red Sea', 'Fiji'), return the most likely country code
    from countries.csv using LLM reasoning.

    Args:
        location: The dive location as a string.
    """
    countries_df = read_csv("countries.csv")
    country_list = countries_df["country"].tolist()

    client = Client()

    prompt = f"""
    The user wants to dive in: "{location}".

    Here is the list of available countries:
    {", ".join(country_list)}

    Which country from the list best matches the dive location?
    Only return the country name exactly as in the list.
    If multiple countries are possible, return the first one in the list.
    """

    response = client.models.generate_content(
        model=getenv("MODEL_ID"),
        contents=prompt,
    )

    country_name = response.text.strip()

    row = countries_df[countries_df["country"] == country_name]
    if not row.empty:
        return {"countryId": int(row.iloc[0]["code"]), "country": country_name}
    else:
        return {"countryId": None, "country": None}


@tool
def get_possible_date_ranges(year: int, month_name: str, nights: int) -> list[dict]:
    """
    Given a year, month name, and number of nights, return possible date ranges
    for that month that are not in the past.

    Args:
        year: The year as an integer (e.g., 2024).
        month_name: The month name as a string (e.g., "October").
        nights: The number of nights as an integer.
    """
    # Convert month name (e.g. "October") to month number
    month = datetime.strptime(month_name, "%B").month

    today = date.today()
    _, days_in_month = monthrange(year, month)

    possible_ranges = []

    for day in range(1, days_in_month + 1):
        start_date = date(year, month, day)
        end_date = start_date + timedelta(days=nights)

        # Ensure start date is not in the past
        if start_date < today:
            continue

        # Ensure end date is still within the same month
        if end_date.month == month:
            possible_ranges.append({
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d")
            })

    return possible_ranges


class PadiResortsSearch(Tool):
    name = "padi_resorts_search"
    description = """Search available dive resorts in a given country from PADI Travel.
    Input: countryId (int), dateStart (YYYY-MM-DD), dateTo (YYYY-MM-DD), divers (int)
    Returns JSON of resorts with availability and pricing.
    """
    inputs = {
        "countryId": {"type": "integer", "description": "Country ID from countries.csv"},
        "dateStart": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
        "dateTo": {"type": "string", "description": "End date (YYYY-MM-DD)"},
        "divers": {"type": "integer", "description": "Number of divers"},
    }
    output_type = "array"

    def forward(self, countryId, dateStart, dateTo, divers):
        totalGuests = divers
        nights = (datetime.fromisoformat(dateTo) - datetime.fromisoformat(dateStart)).days
        split_guests = f"{{\"divers\":{divers},\"students\":0,\"nonDivers\":0,\"rooms\":1}}"
        url = f"https://travel.padi.com/api/v2/travel/search/country/{countryId}/resorts/?page_size=100&meal_plan=40&totalGuests={totalGuests}&dateStart={dateStart}&dateTo={dateTo}&nights={nights}&rooms=1&divers={divers}&nonDivers=0&students=0&guests_split={split_guests}&page=1"  # noqa: E501
        resp = requests.get(url)
        resp.raise_for_status()
        json_data = resp.json()
        trimmed_data = []
        if "results" in json_data:
            results = json_data["results"]
            for result in results:
                trimmed_result = {
                    "title": result.get("title"),
                    "diveCenterTitle": result.get("diveCenterTitle"),
                    "countryTitle": result.get("countryTitle"),
                    "minimalStay": result.get("minimalStay"),
                    "priceSum": result.get("priceSum"),
                    "url": result.get("url"),
                    "numberOfDives": result.get("numberOfDives"),
                }
                trimmed_data.append(trimmed_result)
        return trimmed_data


class KiwiFlightSearch(Tool):
    name = "kiwi_flight_search"
    description = """Search available flights on Kiwi.com.
    """
    inputs = {
        "adults": {"type": "integer", "description": "Number of adult travelers"},
        "children": {"type": "integer", "description": "Number of child travelers"},
        "dep_airport": {"type": "string", "description": "Departure airport IATA code (e.g. 'LAS')"},
        "arr_airport": {"type": "string", "description": "Arrival airport IATA code (e.g. 'NAN')"},
        "dep_date": {"type": "string", "description": "Departure date (YYYY-MM-DD)"},
        "ret_date": {"type": "string", "description": "Return date (YYYY-MM-DD)"},
    }
    output_type = "array"
    graphql_result = None

    def forward(self, adults, children, dep_airport, arr_airport, dep_date, ret_date):
        from playwright.sync_api import sync_playwright

        def intercept_request(route, request):
            # We can update requests with custom headers
            if "SearchReturnItinerariesQuery" in request.url and request.method == "POST":
                headers = request.headers.copy()
                print("Original headers:", headers)
                route.continue_(headers=headers)
            else:
                route.continue_()

        def intercept_response(response):
            # We can extract details from background requests
            if "SearchReturnItinerariesQuery" in response.url:
                self.graphql_result = response.text()
                if self.graphql_result:
                    print(f"GraphQL result length: {len(self.graphql_result)}")
            return response

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            # Intercept requesets and responses
            page.route("**/*", intercept_request)
            page.on("response", intercept_response)

            dep_slug = get_slug(dep_airport)
            arr_slug = get_slug(arr_airport)
            if not dep_slug or not arr_slug:
                print(f"Could not find slugs for airports: {dep_airport} ({dep_slug}), {arr_airport} ({arr_slug})")
                return None

            page.goto(f"https://www.kiwi.com/en/search/results/{dep_slug}/{arr_slug}/{dep_date}/{ret_date}?adults={adults}&children={children}&currency=USD")  # noqa: E501
            page.wait_for_timeout(10000)  # wait for 10 seconds to allow time for the request to complete
            return self.graphql_result
