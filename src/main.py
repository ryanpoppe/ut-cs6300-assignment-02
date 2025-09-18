
import dotenv
import json
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from os import getenv
from phoenix.otel import register
from smolagents import (
    CodeAgent,
    WebSearchTool,
    VisitWebpageTool,
    OpenAIServerModel,
)

from src.final_answer_checks import validate_json_schema, validate_sorted_by_cost, validate_travel_dates
from src.json_schema import output_schema
from src.tools import get_country_id, get_possible_date_ranges, PadiResortsSearch, KiwiFlightSearch
from src.utils import get_user_input

# Load environment variables from .env file
dotenv.load_dotenv()

# Initialize tools and agent
visit_website_tool = VisitWebpageTool()
padi_resorts_tool = PadiResortsSearch()
search_flights_tool = KiwiFlightSearch()
tools = [
    get_country_id,
    get_possible_date_ranges,
    padi_resorts_tool,
    search_flights_tool,
    WebSearchTool(),
    VisitWebpageTool(),
    ]
additional_authorized_imports = ['json']

# Specify final answer checks
final_answer_checks = [
    validate_json_schema,
    validate_sorted_by_cost,
    validate_travel_dates,
]

# Setup OpenTelemetry instrumentation
register()
SmolagentsInstrumentor().instrument()

# Initialize the CodeAgent with the OpenAIServerModel
model_id = getenv("MODEL_ID")
model = OpenAIServerModel(model_id=model_id,
                          api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
                          api_key=getenv("GEMINI_API_KEY"),
                          )
agent = CodeAgent(
    tools=tools,
    model=model,
    additional_authorized_imports=additional_authorized_imports,
    max_steps=5,
)


def run_agent(animals, location, num_divers, num_nights, month, year, departure_location):
    prompt = f"""
You are a scuba dive trip coordinator AI.
Your task is to help the user plan scuba diving vacations by finding the best budget-friendly options.

You will query the user for:
- Destination (country or specific dive region)
- Number of nights
- Month and year of travel
- Animals or marine life they want to see

User preferences:
- Location: {location}
- Animals to see: {', '.join(animals)}
- Number of divers: {num_divers}
- Number of nights: {num_nights}
- Month: {month}
- Year: {year}
- Departure airport: {departure_location}

Your goal:
1. Find the **top 3 most budget-friendly dive resorts** that match the user's preferences.
2. Include **round-trip flight options** from the departure location to the nearest airport.
3. Create a **detailed itinerary** for each option, making sure to:
   - Include all travel days, including flight days.
   - Include check-in and check-out dates.
   - Ensure enough travel time between airport arrival/departure and the resort.
   - Add scheduled dive days with chances to see the requested animals.
4. Return the results, sorted by total package cost (ascending), in **JSON format** matching this schema:

<JSON_SCHEMA>
{json.dumps(output_schema, indent=4)}
</JSON_SCHEMA>

Always output **only JSON**, without any additional text.
"""
    print(f"Running agent with prompt:\n{prompt}")
    answer = agent.run(prompt)
    print(f"Agent returned answer: {answer}")
    # strip ````json` from the beginning and ``` from the end if they exist
    if answer.startswith("```json"):
        answer = answer[len("```json"):].strip()
    if answer.endswith("```"):
        answer = answer[:-len("```")].strip()
    return answer


def main():
    animals, location, num_divers, num_nights, month, year, departure_location = get_user_input()
    run_agent(animals, location, num_divers, num_nights, month, year, departure_location)


if __name__ == "__main__":
    main()
