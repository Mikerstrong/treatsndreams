

import streamlit as st
import json
import os

# ---- Data Storage ----
DATA_DIR = os.getenv("DATA_DIR", "data")
os.makedirs(DATA_DIR, exist_ok=True)
USERS_FILE = os.path.join(DATA_DIR, "users.json")
BANK_FILE = os.path.join(DATA_DIR, "bank.json")

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def load_bank():
    if os.path.exists(BANK_FILE):
        with open(BANK_FILE, "r") as f:
            return json.load(f)
    return {}

def save_bank():
    with open(BANK_FILE, "w") as f:
        json.dump({
            "activities": st.session_state.activities,
            "treats": st.session_state.treats,
            "dreams": st.session_state.dreams,
            "user_banks": st.session_state.user_banks,
            "dream_bank": st.session_state.dream_bank
        }, f)

 # ---- Session State Initialization ----
st.session_state.users = load_users()
if "selected_user" not in st.session_state:
    st.session_state.selected_user = st.session_state.users[0] if st.session_state.users else None
bank_data = load_bank()
if "activities" not in st.session_state:
    st.session_state.activities = bank_data.get("activities", [
        {"name": "Run 5km", "points": 10},
        {"name": "Yoga 30min", "points": 5}
    ])
if "treats" not in st.session_state:
    st.session_state.treats = bank_data.get("treats", [
        {"name": "Ice Cream", "cost": 15, "purchased_by": []}
    ])
if "dreams" not in st.session_state:
    st.session_state.dreams = bank_data.get("dreams", [
        {"name": "Weekend Trip", "cost": 100, "purchased_by": []}
    ])
if "user_banks" not in st.session_state:
    if "user_banks" in bank_data:
        st.session_state.user_banks = bank_data["user_banks"]
    else:
        st.session_state.user_banks = {user: {"activity_points": 0} for user in st.session_state.users}
if "dream_bank" not in st.session_state:
    st.session_state.dream_bank = bank_data.get("dream_bank", 0)

# ---- User Selection ----
st.title("🏋️ Workout Motivation App")

st.subheader("Users")
if st.session_state.users:
    user_cols = st.columns([4,1])
    with user_cols[0]:
        user = st.selectbox("Select User", st.session_state.users, key="user_select")
        st.session_state.selected_user = user
        user_bank = st.session_state.user_banks.get(user, {"activity_points": 0})
        st.header(f"Hello, {user}!")
    with user_cols[1]:
        if st.button("🗑️ Delete User", key="delete_user"):
            if user:
                st.session_state.users.remove(user)
                save_users(st.session_state.users)
                st.session_state.user_banks.pop(user, None)
                save_bank()
                st.session_state.selected_user = st.session_state.users[0] if st.session_state.users else None
                st.success(f"User '{user}' deleted!")
                st.rerun()
else:
    st.info("No users yet. Please add a user to get started.")
    user = None
    user_bank = {"activity_points": 0}

if st.button("➕ Add New User", key="add_user_button"):
    st.session_state["add_user_form_visible"] = True

if st.session_state.get("add_user_form_visible", False):
    with st.form(key="add_user_form"):
        new_user = st.text_input("Add New User")
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Add User") and new_user:
                if new_user not in st.session_state.users:
                    st.session_state.users.append(new_user)
                    save_users(st.session_state.users)
                    # Add to user_banks
                    st.session_state.user_banks[new_user] = {"activity_points": 0}
                    st.session_state["add_user_form_visible"] = False
                    st.success(f"User '{new_user}' added!")
                    st.rerun()
                else:
                    st.warning("User already exists.")
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state["add_user_form_visible"] = False
                st.rerun()

# ---- Activities ----
st.subheader("Activities")
st.write("Complete activities to earn activity points.")

with st.expander("Current Activities"):
    for idx, a in enumerate(st.session_state.activities):
        col1, col2 = st.columns([4,1])
        with col1:
            st.write(f"- **{a['name']}**: {a['points']} points")
        with col2:
            if st.button("🗑️", key=f"delete_activity_{idx}"):
                st.session_state.activities.pop(idx)
                save_bank()
                st.rerun()
    import random
    activity_form_key = f"add_activity_{random.randint(0, 1_000_000)}" if st.session_state.get("reset_activity_form") else "add_activity"
    with st.form(key=activity_form_key):
        new_activity = st.text_input("New Activity Name")
        new_points = st.number_input("Points", min_value=1, step=1)
        if st.form_submit_button("Add Activity") and new_activity:
            st.session_state.activities.append(
                {"name": new_activity, "points": new_points}
            )
            save_bank()
            st.success("Activity added!")
            st.session_state["reset_activity_form"] = True
            st.rerun()
    if st.session_state.get("reset_activity_form"):
        del st.session_state["reset_activity_form"]

with st.form(key="complete_activity"):
    st.write("Mark an activity as complete:")
    activity_names = [a["name"] for a in st.session_state.activities]
    activity_choice = st.selectbox("Activity", activity_names)
    if st.form_submit_button("Complete Activity") and user:
        points = next(a["points"] for a in st.session_state.activities if a["name"] == activity_choice)
        st.session_state.user_banks[user]["activity_points"] += points
        save_bank()
        st.success(f"{activity_choice} completed! +{points} points.")

if user:
    st.markdown(f"**Activity Points Bank:** {user_bank['activity_points']} points")

# ---- Treats ----
st.header("🎁 Treats")

with st.expander("Available Treats"):
    if not st.session_state.treats:
        st.write("_No treats yet!_")
    for idx, treat in enumerate(st.session_state.treats):
        treat_cols = st.columns([4,1])
        with treat_cols[0]:
            purchased = user in treat["purchased_by"]
            st.write(f"**{treat['name']}** - Cost: {treat['cost']} pts")
            if purchased:
                st.success("Purchased!")
            else:
                points = user_bank["activity_points"] if user else 0
                percent = min(points / treat["cost"], 1.0) * 100
                points_needed = max(treat["cost"] - points, 0)
                st.progress(percent / 100, text=f"{percent:.1f}% complete")
                st.write(f"Points needed: {points_needed}")
                if points >= treat["cost"]:
                    if st.button(f"Buy {treat['name']}", key=f"buy_treat_{treat['name']}"):
                        treat["purchased_by"].append(user)
                        st.session_state.user_banks[user]["activity_points"] -= treat["cost"]
                        st.session_state.dream_bank += treat["cost"]
                        save_bank()
                        st.success("Treat purchased! Points moved to Dream Bank.")
        with treat_cols[1]:
            if st.button("🗑️", key=f"delete_treat_{idx}"):
                st.session_state.treats.pop(idx)
                save_bank()
                st.rerun()

    with st.form(key="add_treat"):
        treat_name = st.text_input("New Treat Name")
        treat_cost = st.number_input("Treat Cost (points)", min_value=1, step=1)
        if st.form_submit_button("Add Treat") and treat_name:
            st.session_state.treats.append(
                {"name": treat_name, "cost": treat_cost, "purchased_by": []}
            )
            save_bank()
            st.success("Treat added!")
            st.rerun()

# Treats purchased percentage
if st.session_state.treats:
    purchased = sum(user in t["purchased_by"] for t in st.session_state.treats)
    total = len(st.session_state.treats)
    percent = (purchased / total) * 100
    st.info(f"Treats Purchased: {purchased} / {total} ({percent:.1f}%)")

# ---- Dream Points ----
st.header("🌟 Dreams")
st.markdown(f"**Combined Dream Bank:** {st.session_state.dream_bank} points")

with st.expander("Dream List"):
    if not st.session_state.dreams:
        st.write("_No dreams yet!_")
    for idx, dream in enumerate(st.session_state.dreams):
        dream_cols = st.columns([4,1])
        with dream_cols[0]:
            purchased = user in dream["purchased_by"]
            st.write(f"**{dream['name']}** - Cost: {dream['cost']} pts")
            if purchased:
                st.success("Purchased!")
            else:
                points = st.session_state.dream_bank
                percent = min(points / dream["cost"], 1.0) * 100
                points_needed = max(dream["cost"] - points, 0)
                st.progress(percent / 100, text=f"{percent:.1f}% complete")
                st.write(f"Points needed: {points_needed}")
                if points >= dream["cost"]:
                    if st.button(f"Buy {dream['name']}", key=f"buy_dream_{dream['name']}"):
                        dream["purchased_by"].append(user)
                        st.session_state.dream_bank -= dream["cost"]
                        save_bank()
                        st.success("Dream purchased!")
        with dream_cols[1]:
            if st.button("🗑️", key=f"delete_dream_{idx}"):
                st.session_state.dreams.pop(idx)
                save_bank()
                st.rerun()

    with st.form(key="add_dream"):
        dream_name = st.text_input("New Dream Name")
        dream_cost = st.number_input("Dream Cost (points)", min_value=1, step=1)
        if st.form_submit_button("Add Dream") and dream_name:
            st.session_state.dreams.append(
                {"name": dream_name, "cost": dream_cost, "purchased_by": []}
            )
            save_bank()
            st.success("Dream added!")

# Dreams purchased percentage
if st.session_state.dreams:
    purchased = sum(user in d["purchased_by"] for d in st.session_state.dreams)
    total = len(st.session_state.dreams)
    percent = (purchased / total) * 100
    st.info(f"Dreams Purchased: {purchased} / {total} ({percent:.1f}%)")

st.markdown("---")
st.caption("Made with ❤️ using Streamlit. Data is session-based and resets on reload.")
