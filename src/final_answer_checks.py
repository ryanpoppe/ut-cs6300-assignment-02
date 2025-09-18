from datetime import datetime
from json import loads as json_loads


def validate_at_least_one_result(data) -> bool:
    """
    Validate that there is at least one result in the output.
    """
    data = json_loads(data)
    results = data.get("results", [])
    return len(results) > 0


def validate_json_schema(data, schema) -> bool:
    from jsonschema import validate, ValidationError

    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False


def validate_sorted_by_cost(data) -> bool:
    """
    Validate that the results are sorted by total_package_cost in ascending order.
    """
    data = json_loads(data)
    costs = [item["total_package_cost"] for item in data.get("results", []) if "total_package_cost" in item]
    return costs == sorted(costs)


def validate_travel_dates(data) -> bool:
    """
    Validate that the travel dates in the itinerary line up correctly.
    The departing flight arrival date should be on the resort check-in date,
    and the returning flight departure date should be on the resort check-out date.

    This is the json schema:
        json_schema = {
        "results": [
            {
                "resort": {
                    "name": "string",
                    "location": "string",
                    "check_in": "YYYY-MM-DD",
                    "check_out": "YYYY-MM-DD",
                    "price_per_night": "number",
                    "total_resort_cost": "number",
                    "amenities": ["string"],
                    "dive_highlights": ["string"],
                    "url": "string"
                },
                "flights": {
                    "departing_flight": {
                        "departure_datetime": "YYYY-MM-DDTHH:MM",
                        "arrival_datetime": "YYYY-MM-DDTHH:MM",
                        "airline": "string",
                        "price": "number",
                        "layovers": ["string"],
                        "flight_time": "string"
                    },
                    "returning_flight": {
                        "departure_datetime": "YYYY-MM-DDTHH:MM",
                        "arrival_datetime": "YYYY-MM-DDTHH:MM",
                        "airline": "string",
                        "price": "number",
                        "layovers": ["string"],
                        "flight_time": "string"
                    },
                    "total_flight_cost": "number"
                },
                "itinerary": {
                    "departure_date": "YYYY-MM-DD",
                    "return_date": "YYYY-MM-DD",
                    "schedule": [
                        {
                            "day": "integer",
                            "date": "YYYY-MM-DD",
                            "activities": ["string"]
                        }
                    ]
                },
                "total_package_cost": "number",
                "currency": "string"
                }
        ]
    }
    """
    data = json_loads(data)

    results = data.get("results", [])

    for result in results:
        resort = result.get("resort", {})
        check_in = resort.get("check_in")
        check_in_date = datetime.fromisoformat(check_in).date()
        check_out = resort.get("check_out")
        check_out_date = datetime.fromisoformat(check_out).date()
        flights = result.get("flights", {})
        departing_flight = flights.get("departing_flight", {})
        returning_flight = flights.get("returning_flight", {})
        dep_flight_arrival = departing_flight.get("arrival_datetime")
        dep_flight_arrival_date = datetime.fromisoformat(dep_flight_arrival).date()
        ret_flight_departure = returning_flight.get("departure_datetime")
        ret_flight_departure_date = datetime.fromisoformat(ret_flight_departure).date()

        if dep_flight_arrival_date > check_in_date:
            return False
        if ret_flight_departure_date < check_out_date:
            return False

    return True
