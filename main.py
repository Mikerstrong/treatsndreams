

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
        col1, col2, col3 = st.columns([4,1,1])
        with col1:
            st.write(f"- **{a['name']}**: {a['points']} points")
        with col2:
            if st.button("✏️", key=f"edit_activity_btn_{idx}", help="Edit Activity"):
                st.session_state[f"edit_activity_form_{idx}"] = True
        with col3:
            if st.button("🗑️", key=f"delete_activity_{idx}", help="Delete Activity"):
                st.session_state.activities.pop(idx)
                save_bank()
                st.rerun()
        
        # Edit form for this activity
        if st.session_state.get(f"edit_activity_form_{idx}", False):
            with st.form(key=f"edit_activity_form_submit_{idx}"):
                st.write(f"**Editing: {a['name']}**")
                edit_name = st.text_input("Activity Name", value=a['name'])
                edit_points = st.number_input("Points", value=a['points'], min_value=1, step=1)
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Save Changes"):
                        st.session_state.activities[idx] = {"name": edit_name, "points": edit_points}
                        st.session_state[f"edit_activity_form_{idx}"] = False
                        save_bank()
                        st.success("Activity updated!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_activity_form_{idx}"] = False
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
        treat_cols = st.columns([4,1,1])
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
        with treat_cols[1]:
            if st.button("✏️", key=f"edit_treat_btn_{idx}", help="Edit Treat"):
                st.session_state[f"edit_treat_form_{idx}"] = True
        with treat_cols[2]:
            if st.button("🗑️", key=f"delete_treat_{idx}", help="Delete Treat"):
                st.session_state.treats.pop(idx)
                save_bank()
                st.rerun()
        
        # Edit form for this treat
        if st.session_state.get(f"edit_treat_form_{idx}", False):
            with st.form(key=f"edit_treat_form_submit_{idx}"):
                st.write(f"**Editing: {treat['name']}**")
                edit_name = st.text_input("Treat Name", value=treat['name'])
                edit_cost = st.number_input("Treat Cost (points)", value=treat['cost'], min_value=1, step=1)
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Save Changes"):
                        st.session_state.treats[idx] = {"name": edit_name, "cost": edit_cost, "purchased_by": treat["purchased_by"]}
                        st.session_state[f"edit_treat_form_{idx}"] = False
                        save_bank()
                        st.success("Treat updated!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_treat_form_{idx}"] = False
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

# Purchase treats with dropdown
if user and st.session_state.treats:
    st.subheader("Purchase Treats")
    available_treats = [t for t in st.session_state.treats if user not in t["purchased_by"]]
    affordable_treats = [t for t in available_treats if user_bank["activity_points"] >= t["cost"]]
    
    if affordable_treats:
        with st.form(key="purchase_treat_form"):
            treat_options = [f"{t['name']} - {t['cost']} points" for t in affordable_treats]
            selected_treat = st.selectbox("Select a treat to purchase:", treat_options)
            
            if st.form_submit_button("Purchase Treat"):
                # Find the selected treat
                treat_name = selected_treat.split(" - ")[0]
                treat = next(t for t in st.session_state.treats if t["name"] == treat_name)
                
                # Purchase the treat
                treat["purchased_by"].append(user)
                st.session_state.user_banks[user]["activity_points"] -= treat["cost"]
                st.session_state.dream_bank += treat["cost"]
                save_bank()
                st.success(f"Treat '{treat['name']}' purchased! Points moved to Dream Bank.")
                st.rerun()
    else:
        if available_treats:
            st.info("You don't have enough points to purchase any available treats.")
        else:
            st.info("You have purchased all available treats!")

# ---- Dream Points ----
st.header("🌟 Dreams")
st.markdown(f"**Combined Dream Bank:** {st.session_state.dream_bank} points")

with st.expander("Dream List"):
    if not st.session_state.dreams:
        st.write("_No dreams yet!_")
    for idx, dream in enumerate(st.session_state.dreams):
        dream_cols = st.columns([4,1,1])
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
        with dream_cols[1]:
            if st.button("✏️", key=f"edit_dream_btn_{idx}", help="Edit Dream"):
                st.session_state[f"edit_dream_form_{idx}"] = True
        with dream_cols[2]:
            if st.button("🗑️", key=f"delete_dream_{idx}", help="Delete Dream"):
                st.session_state.dreams.pop(idx)
                save_bank()
                st.rerun()
        
        # Edit form for this dream
        if st.session_state.get(f"edit_dream_form_{idx}", False):
            with st.form(key=f"edit_dream_form_submit_{idx}"):
                st.write(f"**Editing: {dream['name']}**")
                edit_name = st.text_input("Dream Name", value=dream['name'])
                edit_cost = st.number_input("Dream Cost (points)", value=dream['cost'], min_value=1, step=1)
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Save Changes"):
                        st.session_state.dreams[idx] = {"name": edit_name, "cost": edit_cost, "purchased_by": dream["purchased_by"]}
                        st.session_state[f"edit_dream_form_{idx}"] = False
                        save_bank()
                        st.success("Dream updated!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"edit_dream_form_{idx}"] = False
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
            st.rerun()

# Dreams purchased percentage
if st.session_state.dreams:
    purchased = sum(user in d["purchased_by"] for d in st.session_state.dreams)
    total = len(st.session_state.dreams)
    percent = (purchased / total) * 100
    st.info(f"Dreams Purchased: {purchased} / {total} ({percent:.1f}%)")

# Purchase dreams with dropdown
if user and st.session_state.dreams:
    st.subheader("Purchase Dreams")
    available_dreams = [d for d in st.session_state.dreams if user not in d["purchased_by"]]
    affordable_dreams = [d for d in available_dreams if st.session_state.dream_bank >= d["cost"]]
    
    if affordable_dreams:
        with st.form(key="purchase_dream_form"):
            dream_options = [f"{d['name']} - {d['cost']} points" for d in affordable_dreams]
            selected_dream = st.selectbox("Select a dream to purchase:", dream_options)
            
            if st.form_submit_button("Purchase Dream"):
                # Find the selected dream
                dream_name = selected_dream.split(" - ")[0]
                dream = next(d for d in st.session_state.dreams if d["name"] == dream_name)
                
                # Purchase the dream
                dream["purchased_by"].append(user)
                st.session_state.dream_bank -= dream["cost"]
                save_bank()
                st.success(f"Dream '{dream['name']}' purchased!")
                st.rerun()
    else:
        if available_dreams:
            st.info("Not enough points in the Dream Bank to purchase any available dreams.")
        else:
            st.info("All dreams have been purchased!")

st.markdown("---")

# Admin Section
with st.expander("⚙️ Admin Controls"):
    st.warning("**Warning**: Admin actions affect all users and data.")
    
    st.markdown("### Reset Dream Bank")
    admin_col1, admin_col2 = st.columns([3, 1])
    
    with admin_col1:
        st.markdown("Resets the shared dream bank to 0 points.")
    
    with admin_col2:
        if st.button("Reset Dream Bank"):
            # Show confirmation dialog using session state
            st.session_state["show_reset_confirmation"] = True
    
    # Dream Bank Confirmation dialog
    if st.session_state.get("show_reset_confirmation", False):
        st.error("⚠️ Are you sure you want to reset the Dream Bank to 0 points? This cannot be undone.")
        
        confirm_col1, confirm_col2 = st.columns([1, 1])
        with confirm_col1:
            if st.button("Yes, Reset Dream Bank"):
                # Reset dream bank
                st.session_state.dream_bank = 0
                save_bank()
                st.session_state["show_reset_confirmation"] = False
                st.success("Dream Bank has been reset to 0 points!")
                st.rerun()
        
        with confirm_col2:
            if st.button("Cancel"):
                st.session_state["show_reset_confirmation"] = False
                st.rerun()
    
    st.markdown("---")
    st.markdown("### Reset User Activity Points")
    
    if st.session_state.users:
        user_to_reset = st.selectbox("Select User", 
                                    options=st.session_state.users,
                                    key="admin_user_select",
                                    format_func=lambda x: f"{x} - {st.session_state.user_banks.get(x, {}).get('activity_points', 0)} points")
        
        reset_user_col1, reset_user_col2 = st.columns([3, 1])
        
        with reset_user_col1:
            st.markdown(f"Reset activity points for **{user_to_reset}** to 0.")
        
        with reset_user_col2:
            if st.button("Reset User Points"):
                # Show confirmation dialog
                st.session_state["show_user_reset_confirmation"] = True
                st.session_state["user_to_reset"] = user_to_reset
        
        # User Points Confirmation dialog
        if st.session_state.get("show_user_reset_confirmation", False):
            user_to_reset = st.session_state.get("user_to_reset")
            current_points = st.session_state.user_banks.get(user_to_reset, {}).get('activity_points', 0)
            
            st.error(f"⚠️ Are you sure you want to reset **{user_to_reset}**'s activity points from {current_points} to 0? This cannot be undone.")
            
            user_confirm_col1, user_confirm_col2 = st.columns([1, 1])
            with user_confirm_col1:
                if st.button("Yes, Reset User Points"):
                    # Reset user points
                    if user_to_reset in st.session_state.user_banks:
                        st.session_state.user_banks[user_to_reset]["activity_points"] = 0
                        save_bank()
                        st.session_state["show_user_reset_confirmation"] = False
                        st.success(f"{user_to_reset}'s activity points have been reset to 0!")
                        st.rerun()
            
            with user_confirm_col2:
                if st.button("Cancel Reset"):
                    st.session_state["show_user_reset_confirmation"] = False
                    st.rerun()
    else:
        st.info("No users available to reset.")

st.caption("Made with ❤️ using Streamlit. Data is session-based and resets on reload.")
