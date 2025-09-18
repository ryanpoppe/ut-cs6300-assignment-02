# Scuba Dive trip planner AI

This agent will help you plan a scuba diving trip

## Setup

Create .env file with Gemini API key. Store in `.env/OPENAI_API_KEY`

You can use Poetry to install dependencies, or pip if you prefer. To install Poetry, use:
```bash
pipx install poetry
```

## Install dependencies

To install dependencies, use:
```bash
poetry install
```

or 

```bash
pip install
```

### Playwright
This project uses playwright to navigate to kiwi to get flights details. After installing the Python dependencies, you must install playwright. First activate the virtual environment, then run:
```bash
playwright install
```

This will install the chromium automation driver.

## Usage

To run, either use Poetry:
```bash
poetry run python run.py
```

or activate your virtual environment and run:
```bash
python run.py
```

## Examples
Here a couple examples of user input:
### Fiji
```bash
Where do you want to dive? fiji
How many divers? 2
How many nights would you like to spend there? 7
Are there any specific marine animals you want to see? Give them as a comma delimited list (e.g., sharks, manta rays, turtles) turtles
Finding ideal months to see turtles in Fiji...
Ideal months to dive in Fiji: May, June, July, August, September, October
Which month would you like to go in? october
Which year? 2025
```
### Maldives
```bash
Where do you want to dive? Malidves
How many divers? 2
How many nights would you like to spend there? 5
Are there any specific marine animals you want to see? Give them as a comma delimited list (e.g., sharks, manta rays, turtles) sharks
Finding ideal months to see sharks in Malidves...
Ideal months to dive in Malidves: December, January, February, March, April, May
Which month would you like to go in? March
Which year? 2026
```

### Test results
Test results are included in the results directory
