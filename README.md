# TravelGenie

TravelGenie is a Streamlit multi-agent AI travel planner using Groq for planning agents and Open-Meteo for short-range weather forecasts.

## Agents
- Flights Agent
- Hotels Agent
- Activities Agent
- Weather Agent (only used when the complete trip is inside the available forecast window)
- Budget Agent
- Itinerary Agent

## Important weather behavior
The weather agent does not invent long-range weather. If the selected trip cannot be fully covered by the available Open-Meteo forecast window, TravelGenie continues normally and marks weather as unavailable. The itinerary agent then plans without making weather-specific claims.

## Local setup
1. Create a virtual environment.
2. Install requirements:
   `pip install -r requirements.txt`
3. Create `.env`:
   `GROQ_API_KEY=your_key_here`
   `GROQ_MODEL=openai/gpt-oss-120b`
4. Run:
   `streamlit run app.py`

## Streamlit Cloud
Put `GROQ_API_KEY` and optionally `GROQ_MODEL` in the app's Secrets settings. Do not commit secrets to GitHub.

## Note
Flights, hotels, and activities are AI-generated planning estimates, not live booking inventory.
