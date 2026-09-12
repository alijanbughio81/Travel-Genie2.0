import os
from datetime import date, timedelta
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
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

st.set_page_config(page_title="TravelGenie", page_icon="✈️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:#F5F8FC;color:#10233F}
.stApp p,.stApp label{color:#10233F}
.stApp input,.stApp textarea{background:white!important;color:#10233F!important;border-color:#B8C4D6!important}
.stApp [data-baseweb="select"]>div{background:white!important;color:#10233F!important}
.stApp [data-baseweb="select"] input{color:#10233F!important}
.stApp .stButton button{color:white!important}
.stApp [data-testid="stAlert"]{color:#10233F}
.stApp [data-testid="stAlert"] p{color:inherit}
.stApp [data-testid="stProgress"]{color:#246BFE}
.block-container{max-width:1380px;padding:1.6rem 2.2rem 3rem}
section[data-testid="stSidebar"]{background:#0D1B32}
section[data-testid="stSidebar"] *{color:#F4F7FB!important}
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stNumberInput input,
section[data-testid="stSidebar"] .stDateInput input{background:#162845!important;border:1px solid #2A3E5F!important;color:white!important;border-radius:10px!important}
section[data-testid="stSidebar"] [data-baseweb="select"]>div{background:#162845!important;border-color:#2A3E5F!important;color:white!important} section[data-testid="stSidebar"] [data-baseweb="select"] *{color:white!important}
section[data-testid="stSidebar"] .stButton button{background:#246BFE;border:0;color:white;border-radius:11px;font-weight:700}
.hero{background:linear-gradient(110deg,#0D1B32,#153A78 60%,#246BFE);border-radius:26px;padding:2.5rem 2.7rem;color:white;margin-bottom:1.5rem;position:relative;overflow:hidden}
.hero:after{content:"✈";position:absolute;right:5%;top:-35px;font-size:170px;opacity:.08;transform:rotate(-18deg)}
.hero h1{font-family:'Plus Jakarta Sans';font-size:2.7rem;margin:0 0 .35rem;letter-spacing:-1px}
.hero p{margin:0;opacity:.82;font-size:1.05rem}
.eyebrow{text-transform:uppercase;letter-spacing:2px;font-size:.72rem;font-weight:800;opacity:.65;margin-bottom:.65rem}
.section-title{font-family:'Plus Jakarta Sans';color:#10233F;font-size:1.35rem;font-weight:800;margin:1.2rem 0 .8rem}
.metric-card,.card{background:white;border:1px solid #E5EAF1;border-radius:17px;padding:1.1rem 1.2rem;box-shadow:0 5px 18px rgba(24,49,87,.045)}
.metric-label,.muted{color:#718096;font-size:.82rem}
.metric-value{color:#10233F;font-size:1.3rem;font-weight:800;margin-top:.2rem}
.card{margin-bottom:.8rem}
.card-title{color:#10233F;font-weight:800;font-size:1.03rem}
.price{color:#246BFE;font-size:1.2rem;font-weight:800}
.badge{display:inline-block;background:#EAF2FF;color:#246BFE;border-radius:999px;padding:.28rem .62rem;font-size:.72rem;font-weight:700;margin-right:.3rem}
.day-card{background:white;border:1px solid #E5EAF1;border-left:4px solid #246BFE;border-radius:18px;padding:1.35rem 1.45rem;margin-bottom:.9rem;box-shadow:0 6px 20px rgba(24,49,87,.045)}
.day-number{color:#246BFE;font-size:.74rem;text-transform:uppercase;font-weight:800;letter-spacing:1.5px}
.day-title{color:#10233F;font-family:'Plus Jakarta Sans';font-size:1.25rem;font-weight:800;margin:.25rem 0 .7rem}
.route{background:#F0F5FF;border-radius:13px;padding:.75rem 1rem;text-align:center;color:#10233F;font-weight:700}
.weather{background:linear-gradient(135deg,#EAF2FF,#F7FAFF);border-color:#D9E6FF}
div[data-testid="stTabs"] button{font-weight:700}
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero">
<div class="eyebrow">AI-POWERED TRAVEL PLANNING</div>
<h1>Plan less. Travel more.</h1>
<p>Flights, stays, experiences, budget and a day-by-day itinerary — coordinated by AI agents.</p>
</div>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ✈️ TravelGenie")
    st.caption("Build your next trip")
    st.divider()
    origin = st.text_input("From", "Karachi, Pakistan")
    destination = st.text_input("Going to", "Istanbul, Turkey")
    travelers = st.number_input("Travelers", 1, 20, 2)
    duration = st.number_input("Trip length (days)", 1, 30, 5)
    start_date = st.date_input("Start date", date.today()+timedelta(days=3), min_value=date.today())
    budget = st.number_input("Total budget (PKR)", 0, value=500000, step=10000)
    interests = st.multiselect("Interests",
        ["Culture","Food","History","Nature","Shopping","Adventure","Relaxation"],
        default=["Culture","Food"])
    build = st.button("🚀  Build My Trip", use_container_width=True, type="primary")

if build:
    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY is not configured. Add it to Streamlit Secrets.")
        st.stop()
    try:
        with st.status("TravelGenie is planning your trip...", expanded=True) as status:
            st.write("✈️ Comparing flight options")
            flights = get_flights(origin,destination,budget,travelers,duration)
            st.write("🏨 Finding suitable stays")
            hotels = get_hotels(destination,budget,travelers,duration)
            st.write("🎯 Curating experiences")
            activities = get_activities(destination,budget,travelers,duration,interests)
            st.write("🌤️ Checking forecast availability")
            weather = get_weather(destination,duration,start_date)
            st.write("🌤️ Weather forecast included" if weather.get("available") else "🌤️ Outside forecast window — continuing without weather")
            st.write("💰 Optimizing your budget")
            budget_summary = calculate_budget(flights,hotels,activities,budget,travelers,duration)
            st.write("🗓️ Building your itinerary")
            itinerary = build_itinerary(budget_summary,weather,duration)
            status.update(label="Your trip is ready!",state="complete")
        st.session_state["results"]={"flights":flights,"hotels":hotels,"activities":activities,
            "weather":weather,"budget":budget_summary,"itinerary":itinerary,
            "meta":{"origin":origin,"destination":destination,"travelers":travelers,
                    "duration":duration,"start_date":start_date.isoformat()}}
    except Exception as exc:
        st.error(f"TravelGenie could not complete the plan: {exc}")
        st.stop()

results=st.session_state.get("results")
if not results:
    st.markdown('<div class="section-title">How TravelGenie works</div>',unsafe_allow_html=True)
    cols=st.columns(4)
    for col,(n,title,text) in zip(cols,[("01","Discover","AI explores flights, hotels and experiences."),
        ("02","Optimize","Your budget agent compares the complete trip."),
        ("03","Plan","The itinerary agent turns choices into a daily plan."),
        ("04","Go","Everything is organized in one dashboard.")]):
        with col:
            st.markdown(f'<div class="metric-card"><span class="badge">{n}</span><div class="card-title" style="margin-top:.65rem">{title}</div><div class="muted" style="margin-top:.35rem">{text}</div></div>',unsafe_allow_html=True)
    st.info("Enter your trip details in the sidebar and click **Build My Trip**.")
    st.stop()

meta=results["meta"]; bd=results["budget"]; weather=results["weather"]
st.markdown(f'<div class="section-title">Your trip to {meta["destination"]}</div>',unsafe_allow_html=True)
summary=[("📍 Route",f'{meta["origin"]} → {meta["destination"]}'),
("🗓️ Dates",f'{meta["start_date"]} · {meta["duration"]} days'),
("👥 Travelers",str(meta["travelers"])),("💳 Estimated cost",f'PKR {bd["total_estimated_cost"]:,.0f}')]
cols=st.columns(4)
for col,(label,value) in zip(cols,summary):
    with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',unsafe_allow_html=True)

tabs=st.tabs(["🗓️ Itinerary","💰 Budget","✈️ Flights","🏨 Hotels","🎯 Activities","🌤️ Weather"])

with tabs[0]:
    st.markdown('<div class="section-title">Day-by-day plan</div>',unsafe_allow_html=True)
    for d in results["itinerary"]:
        st.markdown(f'<div class="day-card"><div class="day-number">DAY {d.get("day")}</div><div class="day-title">{d.get("title","")}</div>',unsafe_allow_html=True)
        for item in d.get("activities",[]): st.markdown(f"**•** {item}")
        if d.get("notes"): st.caption(d["notes"])
        st.markdown("</div>",unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="section-title">Budget overview</div>',unsafe_allow_html=True)
    total=float(bd["total_estimated_cost"]); limit=float(bd["user_budget"])
    if bd["within_budget"]: st.success(f'✓ Within budget · PKR {max(limit-total,0):,.0f} remaining')
    else: st.warning(f'Over budget · PKR {total-limit:,.0f} above your limit')
    st.progress(min(total/limit,1) if limit else 0)
    cols=st.columns(3)
    for col,label,val in zip(cols,["Flights","Hotels","Experiences"],[bd["breakdown"]["flights"],bd["breakdown"]["hotel"],bd["breakdown"]["activities"]]):
        with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">PKR {val:,.0f}</div></div>',unsafe_allow_html=True)
    st.info(bd["suggestions"])

with tabs[2]:
    st.markdown('<div class="section-title">Flight options</div>',unsafe_allow_html=True)
    for f in results["flights"]:
        st.markdown(f'<div class="card"><div class="card-title">{f.get("airline","")}</div><div class="muted">Estimated price · per person</div><div style="margin:.65rem 0"><span class="price">PKR {float(f.get("price",0)):,.0f}</span></div><div class="route">{f.get("from","")} &nbsp; → &nbsp; {f.get("to","")}</div><div class="muted" style="margin-top:.65rem">Departure {f.get("departure_time","")} · Arrival {f.get("arrival_time","")}</div></div>',unsafe_allow_html=True)

with tabs[3]:
    st.markdown('<div class="section-title">Hotel options</div>',unsafe_allow_html=True)
    for h in results["hotels"]:
        st.markdown(f'<div class="card"><div class="card-title">{h.get("name","")}</div><div style="margin:.45rem 0"><span class="price">PKR {float(h.get("price_per_night",0)):,.0f}</span> <span class="muted">/ night</span> &nbsp; ⭐ {h.get("rating","")}</div><div class="muted">📍 {h.get("location","")}</div><div style="margin-top:.55rem"><span class="badge">Stay</span><span class="muted">{h.get("amenities","")}</span></div></div>',unsafe_allow_html=True)

with tabs[4]:
    st.markdown('<div class="section-title">Curated experiences</div>',unsafe_allow_html=True)
    cols=st.columns(2)
    for i,a in enumerate(results["activities"]):
        with cols[i%2]:
            st.markdown(f'<div class="card"><div class="card-title">{a.get("name","")}</div><div style="margin:.45rem 0"><span class="badge">{a.get("category","Experience")}</span><span class="badge">{a.get("indoor_outdoor","")}</span></div><div class="price">PKR {float(a.get("estimated_cost",0)):,.0f} <span class="muted">/ person</span></div><div class="muted" style="margin-top:.45rem">⏱ {a.get("duration","")}</div></div>',unsafe_allow_html=True)

with tabs[5]:
    st.markdown('<div class="section-title">Weather forecast</div>',unsafe_allow_html=True)
    if weather.get("available"):
        st.success("Forecast available for your selected travel dates.")
        cols=st.columns(min(4,max(1,len(weather["forecast"]))))
        for i,w in enumerate(weather["forecast"]):
            with cols[i%len(cols)]:
                rain=w.get("precipitation_probability")
                st.markdown(f'<div class="card weather"><div class="metric-label">{w["date"]}</div><div class="card-title" style="margin-top:.4rem">{w["condition"]}</div><div class="metric-value">{w["temp_min_c"]}°C – {w["temp_max_c"]}°C</div><div class="muted" style="margin-top:.45rem">Rain chance · {rain if rain is not None else "—"}%</div></div>',unsafe_allow_html=True)
    else:
        st.info(f'Weather is not displayed because the selected trip is outside the available {MAX_FORECAST_DAYS}-day forecast window.')
        st.caption(weather.get("reason",""))

st.divider()
left,right=st.columns([3,1])
with left: st.caption("TravelGenie · AI-generated planning estimates · Verify live prices and availability before booking.")
with right:
    if st.button("↻ Plan another trip",use_container_width=True):
        st.session_state.pop("results",None); st.rerun()
