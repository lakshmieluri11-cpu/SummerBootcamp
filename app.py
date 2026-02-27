import streamlit as st
import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv

def create_agents(api_key: str):
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

# -----------------------------
# SETUP
# -----------------------------
load_dotenv()
client = OpenAI()

st.set_page_config(page_title="Brain Gym AI", layout="centered")

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "age_group" not in st.session_state:
    st.session_state.age_group = None

if "score" not in st.session_state:
    st.session_state.score = 0

if "child_name" not in st.session_state:
    st.session_state.child_name = None


# -----------------------------
# AGE LOGIC
# -----------------------------
def calculate_age(dob):
    today = datetime.date.today()
    age = today.year - dob.year
    if (dob.month, dob.day) > (today.month, today.day):
        age -= 1
    return age


def get_age_group(age):
    if age <= 7:
        return "A"
    elif age <= 12:
        return "B"
    else:
        return "C"


# -----------------------------
# DIFFICULTY LOGIC
# -----------------------------
def adjust_difficulty(score):
    if score < 20:
        return "Easy"
    elif score < 50:
        return "Medium"
    else:
        return "Hard"


# -----------------------------
# LLM ACTIVITY GENERATOR
# -----------------------------
def generate_activity(age_group, difficulty):

    prompt = f"""
    Create one short brain training activity for a child.

    Age Group A: 5-7 years (memory, colors).
    Age Group B: 8-12 years (logic, speed math).
    Age Group C: 13-16 years (advanced reasoning).

    Age Group: {age_group}
    Difficulty: {difficulty}

    Provide:
    1. Title
    2. Challenge question
    3. Correct answer
    4. Short explanation

    Keep it simple and short.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a child brain training expert."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# -----------------------------
# LOGIN SCREEN
# -----------------------------
if st.session_state.age_group is None:

    st.title("🧠 Brain Gym AI")
    st.subheader("Login")

    name = st.text_input("Child Name")
    dob = st.date_input("Date of Birth")

    if st.button("Start Training"):
        age = calculate_age(dob)
        age_group = get_age_group(age)

        st.session_state.age_group = age_group
        st.session_state.child_name = name

        st.success(f"Welcome {name}! Age Group: {age_group}")
        st.rerun()


# -----------------------------
# DASHBOARD
# -----------------------------
else:

    st.title(f"Welcome {st.session_state.child_name} 👋")
    st.write(f"Age Group: {st.session_state.age_group}")
    st.write(f"Current Score: {st.session_state.score}")

    difficulty = adjust_difficulty(st.session_state.score)
    st.write(f"Difficulty Level: {difficulty}")

    if st.button("🎯 Generate Brain Challenge"):

        with st.spinner("Creating brain activity..."):
            activity = generate_activity(st.session_state.age_group, difficulty)

        st.session_state.current_activity = activity

    if "current_activity" in st.session_state:
        st.subheader("Today's Brain Challenge")
        st.write(st.session_state.current_activity)

        result = st.radio("Did the child answer correctly?", ["Select", "Yes", "No"])

        if result == "Yes":
            st.session_state.score += 10
            st.success("Great Job! Score +10")
        elif result == "No":
            st.info("Keep practicing!")

    if st.button("Reset Session"):
        st.session_state.age_group = None
        st.session_state.score = 0

        st.rerun()
