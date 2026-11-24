
from gettext import install

import streamlit as st

st.set_page_config(
    page_title="30-Day Wellness Planner",
    page_icon="🌿",
    layout="wide",
)

MEALS = {
    "Breakfast": [
        ("Oatmeal with berries", "Oats, milk or soy milk, berries, chia seeds", {"vegan"}),
        ("Greek yogurt bowl", "Greek yogurt, berries, oats, nuts", {"vegetarian"}),
        ("Tofu scramble and toast", "Tofu, vegetables, bread", {"vegan"}),
        ("Egg and vegetable toast", "Eggs, vegetables, whole-grain bread", {"vegetarian"}),
        ("Peanut butter banana oats", "Oats, banana, peanut butter", {"vegan"}),
        ("Avocado and bean toast", "Bread, avocado, beans, tomato", {"vegan"}),
    ],
    "Lunch": [
        ("Chickpea and rice bowl", "Chickpeas, rice, vegetables, tahini", {"vegan"}),
        ("Lentil soup with bread", "Lentils, vegetables, bread", {"vegan"}),
        ("Chicken and quinoa bowl", "Chicken, quinoa, vegetables", set()),
        ("Black bean tacos", "Black beans, tortillas, salsa, vegetables", {"vegan"}),
        ("Tuna and potato salad", "Tuna, potatoes, vegetables", set()),
        ("Tofu noodle bowl", "Tofu, noodles, vegetables, soy sauce", {"vegan"}),
    ],
    "Dinner": [
        ("Baked salmon with vegetables", "Salmon, potatoes, vegetables", set()),
        ("Bean and vegetable chili", "Beans, tomatoes, vegetables", {"vegan"}),
        ("Chicken, rice, and vegetables", "Chicken, rice, vegetables", set()),
        ("Vegetable pasta with beans", "Pasta, beans, vegetables, tomato sauce", {"vegan"}),
        ("Tofu stir-fry", "Tofu, rice, vegetables, soy sauce", {"vegan"}),
        ("Egg and vegetable frittata", "Eggs, vegetables, cheese", {"vegetarian"}),
    ],
}


def meal_matches(meal, diet, avoid_terms):
    """Filter meal suggestions by diet choice and typed exclusion terms."""
    title, ingredients, tags = meal
    meal_text = f"{title} {ingredients}".casefold()

    if diet == "Vegetarian" and not ({"vegetarian", "vegan"} & tags):
        return False

    if diet == "Vegan" and "vegan" not in tags:
        return False

    if any(term in meal_text for term in avoid_terms):
        return False

    return True


def build_workout(session_number, experience, equipment):
    """Return a basic general-fitness activity suggestion."""
    sets = "2 sets" if experience == "Beginner" else "3 sets"

    if session_number % 3 == 2:
        return (
            "Walk and mobility",
            "Walk comfortably for 20–30 minutes, then do 5 minutes of gentle "
            "mobility. Keep the pace comfortable.",
        )

    if session_number % 3 == 0:
        if equipment == "Basic equipment":
            details = (
                f"{sets}: chair or bodyweight squats (8–12 reps), incline "
                "push-ups (6–10 reps), resistance-band or backpack rows "
                "(8–12 reps), and glute bridges (10–12 reps). Rest as needed."
            )
        else:
            details = (
                f"{sets}: chair squats (8–12 reps), wall or incline push-ups "
                "(6–10 reps), glute bridges (10–12 reps), and bird-dogs "
                "(6–8 per side). Rest as needed."
            )
        return "Strength routine A", details

    if equipment == "Basic equipment":
        details = (
            f"{sets}: hip hinges with a light backpack (8–12 reps), supported "
            "split squats (6–10 per side), band or backpack rows (8–12 reps), "
            "and dead bugs (6–8 per side). Rest as needed."
        )
    else:
        details = (
            f"{sets}: hip hinges (8–12 reps), supported sit-to-stands "
            "(8–12 reps), bird-dogs (6–8 per side), and calf raises "
            "(10–15 reps). Rest as needed."
        )

    return "Strength routine B", details


def build_plan(diet, avoid_terms, workouts_per_week, experience, equipment):
    filtered_meals = {
        category: [
            meal for meal in options
            if meal_matches(meal, diet, avoid_terms)
        ]
        for category, options in MEALS.items()
    }

    if any(not options for options in filtered_meals.values()):
        return None, "No meal ideas match those filters. Try fewer exclusions."

    activity_days = {
        round(index * 7 / workouts_per_week)
        for index in range(workouts_per_week)
    }

    plan = []
    session_number = 0
    categories = ("Breakfast", "Lunch", "Dinner")

    for day_index in range(30):
        meals_today = {}

        for category_index, category in enumerate(categories):
            options = filtered_meals[category]
            meal_index = (day_index + category_index) % len(options)
            meals_today[category] = options[meal_index][0]

        weekday_index = day_index % 7

        if weekday_index in activity_days:
            session_number += 1
            workout = build_workout(session_number, experience, equipment)
        else:
            workout = (
                "Rest or gentle movement",
                "Take a rest day, or do easy movement if comfortable.",
            )

        plan.append({
            "day": day_index + 1,
            "meals": meals_today,
            "workout": workout,
        })

    return plan, None


st.title("30-Day Wellness Planner")
st.info(
    "This prototype offers general wellness ideas, not medical advice. "
    "It does not analyze body photos, diagnose conditions, prescribe calories, "
    "or guarantee results."
)

st.caption(
    "Meal exclusions are a basic text filter, not an allergy-safety check. "
    "Always check labels and preparation practices; this app cannot account "
    "for ingredient aliases or cross-contamination."
)

with st.form("planner_form"):
    st.subheader("About you")

    age = st.number_input("Age", min_value=13, max_value=100, value=25)

    goal = st.selectbox(
        "Main goal",
        [
            "General fitness",
            "Build strength",
            "Improve activity habits",
            "Gradual weight management",
        ],
    )

    diet = st.selectbox(
        "Eating preference",
        ["Omnivore", "Vegetarian", "Vegan"],
    )

    exclusions = st.text_input(
        "Ingredients to avoid (comma-separated)",
        placeholder="For example: peanuts, shellfish",
    )

    workouts_per_week = st.slider(
        "Activity days per week",
        min_value=2,
        max_value=6,
        value=3,
    )

    experience = st.selectbox(
        "Exercise experience",
        ["Beginner", "Intermediate"],
    )

    equipment = st.selectbox(
        "Available equipment",
        ["None", "Basic equipment"],
    )

    needs_professional_advice = st.checkbox(
        "I am pregnant, have a relevant medical condition or injury, "
        "or have a history of disordered eating."
    )

    acknowledged = st.checkbox(
        "I understand this is general guidance, not medical advice."
    )

    submitted = st.form_submit_button("Create my 30-day plan")


if submitted:
    if age < 18:
        st.error(
            "This prototype is intended for adults. Please ask a parent or "
            "guardian and a qualified professional for guidance."
        )
    elif needs_professional_advice:
        st.warning(
            "This prototype will not generate a plan for the health or safety "
            "consideration you selected. Please consult a qualified healthcare "
            "professional for personalized guidance."
        )
    elif not acknowledged:
        st.error("Please confirm that you understand the plan's limitations.")
    else:
        avoid_terms = [
            term.strip().casefold()
            for term in exclusions.split(",")
            if term.strip()
        ]

        plan, error = build_plan(
            diet=diet,
            avoid_terms=avoid_terms,
            workouts_per_week=workouts_per_week,
            experience=experience,
            equipment=equipment,
        )

        if error:
            st.error(error)
        else:
            st.session_state["plan"] = plan
            st.session_state["goal"] = goal


if "plan" in st.session_state:
    st.header("Your 30-day plan")
    st.caption(
        f"Goal: {st.session_state['goal']}. Meal ideas are suggestions, "
        "not prescribed portions or calorie targets."
    )

    plan = st.session_state["plan"]

    for week_start in range(0, 30, 7):
        week_end = min(week_start + 7, 30)

        with st.expander(
            f"Week {week_start // 7 + 1} — Days {week_start + 1}–{week_end}"
        ):
            for item in plan[week_start:week_end]:
                st.markdown(f"### Day {item['day']}")
                meal_column, activity_column = st.columns(2)

                with meal_column:
                    st.markdown("**Meal ideas**")
                    for meal_name, suggestion in item["meals"].items():
                        st.write(f"- **{meal_name}:** {suggestion}")

                    st.checkbox(
                        "Mark meals complete",
                        key=f"meals_done_{item['day']}",
                    )

                with activity_column:
                    activity_name, details = item["workout"]
                    st.markdown(f"**{activity_name}**")
                    st.write(details)

                    st.checkbox(
                        "Mark activity complete",
                        key=f"activity_done_{item['day']}",
                    )

            st.text_area(
                "Weekly check-in: How did the plan feel? What would you change?",
                key=f"checkin_{week_start // 7}",
            )

    st.warning(
        "Stop exercising if you experience sharp pain, dizziness, chest pain, "
        "or unusual shortness of breath. Seek appropriate medical help if needed."
    )