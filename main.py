import streamlit as st

# ---- Data Storage (in-memory for demo) ----
if "users" not in st.session_state:
    st.session_state.users = ["Mike", "Yvonne"]
if "selected_user" not in st.session_state:
    st.session_state.selected_user = st.session_state.users[0]
if "activities" not in st.session_state:
    st.session_state.activities = [
        {"name": "Run 5km", "points": 10},
        {"name": "Yoga 30min", "points": 5}
    ]
if "treats" not in st.session_state:
    st.session_state.treats = [
        {"name": "Ice Cream", "cost": 15, "purchased_by": []}
    ]
if "dreams" not in st.session_state:
    st.session_state.dreams = [
        {"name": "Weekend Trip", "cost": 100, "purchased_by": []}
    ]
if "user_banks" not in st.session_state:
    st.session_state.user_banks = {
        user: {"activity_points": 0, "dream_points": 0}
        for user in st.session_state.users
    }

# ---- User Selection ----
st.title("🏋️ Workout Motivation App")

user = st.selectbox("Select User", st.session_state.users, key="user_select")
st.session_state.selected_user = user
user_bank = st.session_state.user_banks[user]

st.header(f"Hello, {user}!")

# ---- Activities ----
st.subheader("Activities")
st.write("Complete activities to earn activity points.")

with st.expander("Current Activities"):
    for a in st.session_state.activities:
        st.write(f"- **{a['name']}**: {a['points']} points")
    with st.form(key="add_activity"):
        new_activity = st.text_input("New Activity Name")
        new_points = st.number_input("Points", min_value=1, step=1)
        if st.form_submit_button("Add Activity") and new_activity:
            st.session_state.activities.append(
                {"name": new_activity, "points": new_points}
            )
            st.success("Activity added!")

with st.form(key="complete_activity"):
    st.write("Mark an activity as complete:")
    activity_names = [a["name"] for a in st.session_state.activities]
    activity_choice = st.selectbox("Activity", activity_names)
    if st.form_submit_button("Complete Activity"):
        points = next(a["points"] for a in st.session_state.activities if a["name"] == activity_choice)
        user_bank["activity_points"] += points
        st.success(f"{activity_choice} completed! +{points} points.")

st.markdown(f"**Activity Points Bank:** {user_bank['activity_points']} points")

# ---- Treats ----
st.header("🎁 Treats")
with st.expander("Available Treats"):
    if not st.session_state.treats:
        st.write("_No treats yet!_")
    for treat in st.session_state.treats:
        purchased = user in treat["purchased_by"]
        st.write(f"**{treat['name']}** - Cost: {treat['cost']} pts")
        if purchased:
            st.success("Purchased!")
        else:
            points = user_bank["activity_points"]
            percent = min(points / treat["cost"], 1.0) * 100
            points_needed = max(treat["cost"] - points, 0)
            st.progress(percent / 100, text=f"{percent:.1f}% complete")
            st.write(f"Points needed: {points_needed}")
            if points >= treat["cost"]:
                if st.button(f"Buy {treat['name']}", key=f"buy_treat_{treat['name']}"):
                    treat["purchased_by"].append(user)
                    user_bank["activity_points"] -= treat["cost"]
                    user_bank["dream_points"] += treat["cost"]
                    st.success("Treat purchased! Points moved to Dream Bank.")

    with st.form(key="add_treat"):
        treat_name = st.text_input("New Treat Name")
        treat_cost = st.number_input("Treat Cost (points)", min_value=1, step=1)
        if st.form_submit_button("Add Treat") and treat_name:
            st.session_state.treats.append(
                {"name": treat_name, "cost": treat_cost, "purchased_by": []}
            )
            st.success("Treat added!")

# Treats purchased percentage
if st.session_state.treats:
    purchased = sum(user in t["purchased_by"] for t in st.session_state.treats)
    total = len(st.session_state.treats)
    percent = (purchased / total) * 100
    st.info(f"Treats Purchased: {purchased} / {total} ({percent:.1f}%)")

# ---- Dream Points ----
st.header("🌟 Dreams")
st.markdown(f"**Dream Points Bank:** {user_bank['dream_points']} points")

with st.expander("Dream List"):
    if not st.session_state.dreams:
        st.write("_No dreams yet!_")
    for dream in st.session_state.dreams:
        purchased = user in dream["purchased_by"]
        st.write(f"**{dream['name']}** - Cost: {dream['cost']} pts")
        if purchased:
            st.success("Purchased!")
        else:
            points = user_bank["dream_points"]
            percent = min(points / dream["cost"], 1.0) * 100
            points_needed = max(dream["cost"] - points, 0)
            st.progress(percent / 100, text=f"{percent:.1f}% complete")
            st.write(f"Points needed: {points_needed}")
            if points >= dream["cost"]:
                if st.button(f"Buy {dream['name']}", key=f"buy_dream_{dream['name']}"):
                    dream["purchased_by"].append(user)
                    user_bank["dream_points"] -= dream["cost"]
                    st.success("Dream purchased!")

    with st.form(key="add_dream"):
        dream_name = st.text_input("New Dream Name")
        dream_cost = st.number_input("Dream Cost (points)", min_value=1, step=1)
        if st.form_submit_button("Add Dream") and dream_name:
            st.session_state.dreams.append(
                {"name": dream_name, "cost": dream_cost, "purchased_by": []}
            )
            st.success("Dream added!")

# Dreams purchased percentage
if st.session_state.dreams:
    purchased = sum(user in d["purchased_by"] for d in st.session_state.dreams)
    total = len(st.session_state.dreams)
    percent = (purchased / total) * 100
    st.info(f"Dreams Purchased: {purchased} / {total} ({percent:.1f}%)")

st.markdown("---")
st.caption("Made with ❤️ using Streamlit. Data is session-based and resets on reload.")
