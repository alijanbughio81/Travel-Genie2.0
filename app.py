import os
from datetime import date, timedelta

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Streamlit Cloud secrets -> environment variables before importing agents.
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
if "GROQ_MODEL" in st.secrets:
    os.environ["GROQ_MODEL"] = st.secrets["GROQ_MODEL"]

from flights_agent import get_flights
from hotels_agent import get_hotels
from activities_agent import get_activities
from weather_agent import get_weather, MAX_FORECAST_DAYS
from budget_agent import calculate_budget
from itinerary_agent import build_itinerary

st.set_page_config(
    page_title="TravelGenie",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 3rem;}
.hero {
    padding: 1.5rem 1.8rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #0f172a, #1e3a8a);
    color: white;
    margin-bottom: 1.5rem;
}
.card {
    padding: 1rem;
    border: 1px solid rgba(128,128,128,.2);
    border-radius: 14px;
    margin-bottom: .7rem;
}
.small {opacity: .75; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>✈️ TravelGenie</h1>
<p>Your multi-agent AI travel planner</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Trip Details")
    origin = st.text_input("Origin", "Karachi, Pakistan")
    destination = st.text_input("Destination", "Istanbul, Turkey")
    travelers = st.number_input("Travelers", min_value=1, max_value=20, value=2)
    duration = st.number_input("Duration (days)", min_value=1, max_value=30, value=5)
    start_date = st.date_input("Trip start date", value=date.today() + timedelta(days=3))
    budget = st.number_input("Total budget (PKR)", min_value=0, value=500000, step=10000)
    interests = st.multiselect(
        "Interests",
        ["Culture", "Food", "History", "Nature", "Shopping", "Adventure", "Relaxation"],
        default=["Culture", "Food"],
    )

    build = st.button("🚀 Build My Trip", use_container_width=True, type="primary")

if build:
    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY is not configured. Add it to Streamlit Secrets.")
        st.stop()

    try:
        with st.status("Building your trip...", expanded=True) as status:
            st.write("✈️ Finding flight options...")
            flights = get_flights(origin, destination, budget, travelers, duration)

            st.write("🏨 Finding hotel options...")
            hotels = get_hotels(destination, budget, travelers, duration)

            st.write("🎯 Finding activities...")
            activities = get_activities(
                destination, budget, travelers, duration, interests
            )

            st.write("🌤️ Checking weather forecast...")
            weather = get_weather(destination, duration, start_date)

            if weather.get("available"):
                st.write("Weather forecast is available for your trip.")
            else:
                st.write(
                    "Weather is outside the available forecast window. "
                    "Continuing without weather-specific planning."
                )

            st.write("💰 Calculating budget...")
            budget_summary = calculate_budget(
                flights, hotels, activities, budget, travelers, duration
            )

            st.write("🗓️ Creating itinerary...")
            itinerary = build_itinerary(budget_summary, weather, duration)

            status.update(label="Trip plan ready!", state="complete")

        st.session_state["results"] = {
            "flights": flights,
            "hotels": hotels,
            "activities": activities,
            "weather": weather,
            "budget": budget_summary,
            "itinerary": itinerary,
        }

    except Exception as exc:
        st.error(f"TravelGenie could not complete the plan: {exc}")
        st.stop()

results = st.session_state.get("results")

if results:
    budget_summary = results["budget"]
    weather = results["weather"]

    tabs = st.tabs([
        "🗓️ Itinerary",
        "💰 Budget",
        "✈️ Flights",
        "🏨 Hotels",
        "🎯 Activities",
        "🌤️ Weather",
    ])

    with tabs[0]:
        st.subheader("Your Itinerary")
        for day in results["itinerary"]:
            st.markdown(f"### Day {day.get('day')}: {day.get('title', '')}")
            for item in day.get("activities", []):
                st.markdown(f"- {item}")
            if day.get("notes"):
                st.caption(day["notes"])

    with tabs[1]:
        st.subheader("Budget Summary")
        total = budget_summary["total_estimated_cost"]
        st.metric("Estimated total", f"PKR {total:,.0f}")
        st.metric("Your budget", f"PKR {budget_summary['user_budget']:,.0f}")
        st.success("Within budget" if budget_summary["within_budget"] else "Over budget")

        breakdown = budget_summary["breakdown"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Flights", f"PKR {breakdown['flights']:,.0f}")
        c2.metric("Hotel", f"PKR {breakdown['hotel']:,.0f}")
        c3.metric("Activities", f"PKR {breakdown['activities']:,.0f}")
        st.info(budget_summary["suggestions"])

    with tabs[2]:
        st.subheader("Flight Options")
        for f in results["flights"]:
            st.markdown(
                f"""<div class="card"><b>{f.get('airline','')}</b><br>
                PKR {float(f.get('price',0)):,.0f} per person ·
                {f.get('departure_time','')} → {f.get('arrival_time','')}<br>
                <span class="small">{f.get('from','')} → {f.get('to','')}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    with tabs[3]:
        st.subheader("Hotel Options")
        for h in results["hotels"]:
            st.markdown(
                f"""<div class="card"><b>{h.get('name','')}</b><br>
                PKR {float(h.get('price_per_night',0)):,.0f} / night ·
                ⭐ {h.get('rating','')}<br>
                <span class="small">{h.get('location','')} · {h.get('amenities','')}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    with tabs[4]:
        st.subheader("Activity Options")
        for a in results["activities"]:
            st.markdown(
                f"""<div class="card"><b>{a.get('name','')}</b><br>
                PKR {float(a.get('estimated_cost',0)):,.0f} per person ·
                {a.get('category','')} · {a.get('duration','')}<br>
                <span class="small">{a.get('indoor_outdoor','')}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    with tabs[5]:
        st.subheader("Weather")
        if weather.get("available"):
            st.success("Weather forecast is available for this trip.")
            for day in weather["forecast"]:
                rain = day.get("precipitation_probability")
                rain_text = f"{rain}%" if rain is not None else "N/A"
                st.markdown(
                    f"""<div class="card"><b>{day['date']}</b><br>
                    {day['condition']} · {day['temp_min_c']}°C – {day['temp_max_c']}°C<br>
                    <span class="small">Precipitation probability: {rain_text}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.info(
                "Weather is not shown because the selected trip is outside "
                f"the available {MAX_FORECAST_DAYS}-day forecast window."
            )
            st.caption(weather.get("reason", ""))

    with st.expander("Raw agent output"):
        st.json(results)
else:
    st.info("Enter your trip details in the sidebar and click **Build My Trip** to start.")
