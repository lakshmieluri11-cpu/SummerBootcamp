import streamlit as st
import datetime
from openai import OpenAI

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Brain Gym AI", layout="centered")

# -----------------------------
# OPENAI CLIENT (STREAMLIT CLOUD SAFE)
# -----------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "age_group" not in st.session_state:
    st.session_state.age_group = None

if "score" not in st.session_state:
    st.session_state.score = 0

if "child_name" not in st.session_state:
    st.session_state.child_name = None

if "current_activity" not in st.session_state:
    st.session_state.current_activity = None


# -----------------------------
# AGE CALCULATION
# -----------------------------
def calculate_age(dob):
    today = datetime.date.today()
    age = today.year - dob.year
    if (dob.month, dob.day) > (today.month, today.day):
        age -= 1
    return age


def get_age_group(age):
    if age <= 7:
        return "A"  # Memory & Colors
    elif age <= 12:
        return "B"  # Logic & Math
    else:
        return "C"  # Advanced Reasoning


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

    Age Group A (5-7 years): memory games, colors.
    Age Group B (8-12 years): logic puzzles, speed math.
    Age Group C (13-16 years): reasoning, analytical thinking.

    Age Group: {age_group}
    Difficulty: {difficulty}

    Provide clearly:
    1. Title
    2. Challenge
    3. Correct Answer
    4. Short Explanation

    Keep it short and simple.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert brain trainer for children."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# -----------------------------
# LOGIN SCREEN
# -----------------------------
if st.session_state.age_group is None:

    st.title("🧠 Brain Gym AI")
    st.subheader("Child Login")

    name = st.text_input("Child Name")
    dob = st.date_input("Date of Birth")

    if st.button("Start Training"):
        if name and dob:
            age = calculate_age(dob)
            age_group = get_age_group(age)

            st.session_state.child_name = name
            st.session_state.age_group = age_group
            st.session_state.score = 0

            st.success(f"Welcome {name}! Age Group: {age_group}")
            st.rerun()
        else:
            st.warning("Please enter all details.")


# -----------------------------
# DASHBOARD
# -----------------------------
else:

    st.title(f"Welcome {st.session_state.child_name} 👋")
    st.write(f"Age Group: {st.session_state.age_group}")
    st.write(f"Score: {st.session_state.score}")

    difficulty = adjust_difficulty(st.session_state.score)
    st.write(f"Difficulty Level: {difficulty}")

    if st.button("🎯 Generate Brain Challenge"):
        with st.spinner("Creating challenge..."):
            activity = generate_activity(
                st.session_state.age_group,
                difficulty
            )
        st.session_state.current_activity = activity

    if st.session_state.current_activity:
        st.subheader("Today's Brain Challenge")
        st.write(st.session_state.current_activity)

        result = st.radio(
            "Did the child answer correctly?",
            ["Select", "Yes", "No"]
        )

        if result == "Yes":
            st.session_state.score += 10
            st.success("Great job! +10 points")
        elif result == "No":
            st.info("Keep practicing 💪")

    if st.button("🔄 Reset Session"):
        st.session_state.age_group = None
        st.session_state.score = 0
        st.session_state.current_activity = None
        st.rerun()
