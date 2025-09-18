output_schema = {
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
