import pytest
from pathlib import Path


from src.final_answer_checks import (
    validate_json_schema,
    validate_sorted_by_cost,
    validate_travel_dates,
    validate_at_least_one_result,
)
from src.json_schema import output_schema
from src.main import run_agent


# Define a set of test cases with diverse inputs
test_cases = [
    {
        "name": "Test Case 1 - Fiji",
        "inputs": {
            "animals": ["sharks"],
            "location": "Fiji",
            "num_divers": 2,
            "num_nights": 5,
            "month": "October",
            "year": 2026,
            "departure_location": "LAX",
        },
    },
    {
        "name": "Test Case 2 - Red Sea",
        "inputs": {
            "animals": ["turtles"],
            "location": "Red Sea",
            "num_divers": 4,
            "num_nights": 3,
            "month": "December",
            "year": 2026,
            "departure_location": "JFK",
        },
    },
    {
        "name": "Test Case 3 - Great Barrier Reef",
        "inputs": {
            "animals": ["coral", "dolphins"],
            "location": "Great Barrier Reef",
            "num_divers": 4,
            "num_nights": 7,
            "month": "June",
            "year": 2026,
            "departure_location": "SFO",
        },
    },
    {
        "name": "Test Case 4 - Maldives",
        "inputs": {
            "animals": ["whale sharks"],
            "location": "Maldives",
            "num_divers": 1,
            "num_nights": 10,
            "month": "March",
            "year": 2026,
            "departure_location": "ORD",
        },
    },
    {
        "name": "Test Case 5 - Bali",
        "inputs": {
            "animals": ["seahorses", "nudibranchs"],
            "location": "Bali",
            "num_divers": 3,
            "num_nights": 4,
            "month": "September",
            "year": 2026,
            "departure_location": "SEA",
        },
    },
]


@pytest.fixture(params=test_cases, ids=[case["name"] for case in test_cases])
def test_case(request):
    return request.param


def test_run_agent(test_case):
    result = run_agent(**test_case["inputs"])
    test_name = test_case["name"].replace(" ", "_")
    # using Path, create results directory if it doesn't exist
    results_path = Path("results")
    results_file = results_path / f"{test_name}_results.json"
    # write result to file for inspection
    results_path.mkdir(parents=True, exist_ok=True)
    with open(results_file, "w") as f:
        f.write(result)

    assert validate_json_schema(result, output_schema), "Output does not match JSON schema"
    assert validate_sorted_by_cost(result), "Results are not sorted by total package cost"
    assert validate_travel_dates(result), "Travel dates do not line up correctly"
    assert validate_at_least_one_result(result), "No results found"
