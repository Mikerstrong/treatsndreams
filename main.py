

import streamlit as st
import json
import os

# ---- Data Storage ----
DATA_DIR = os.getenv("DATA_DIR", "data")
os.makedirs(DATA_DIR, exist_ok=True)
USERS_FILE = os.path.join(DATA_DIR, "users.json")
BANK_FILE = os.path.join(DATA_DIR, "bank.json")
ACTIVITY_FILE = os.path.join(DATA_DIR, "activity.json")

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

def load_activity_logs():
    if os.path.exists(ACTIVITY_FILE):
        with open(ACTIVITY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_activity_logs():
    with open(ACTIVITY_FILE, "w") as f:
        json.dump(st.session_state.activity_logs, f)

def save_bank():
    with open(BANK_FILE, "w") as f:
        json.dump({
            "activities": st.session_state.activities,
            "dreams": st.session_state.dreams,
            "user_banks": st.session_state.user_banks,
            "dream_bank": st.session_state.dream_bank
        }, f)

 # ---- Level calculations ----
def calculate_points_needed(level):
    """
    Calculate points needed to reach a specific level
    """
    if level <= 1:
        return 0
    
    total_points = 5  # Points needed for level 2
    
    for l in range(3, level+1):
        total_points += 5 + ((l-1) * 5)  # (5, 10, 15, 20, 25...)
    
    return total_points

def calculate_level(total_points):
    """
    Calculate level based on points with increasing difficulty
    Level 1: 0-5 points
    Level 2: 6-15 points (+10)
    Level 3: 16-30 points (+15)
    Level 4: 31-50 points (+20)
    And so on with increasing difficulty
    """
    if total_points < 5:
        return 1, total_points, 5  # Level 1, current points, need 5 for next level
    
    level = 1
    points_needed = 5  # Points needed for first level
    previous_threshold = 0
    level_threshold = points_needed
    
    while total_points >= level_threshold:
        level += 1
        previous_threshold = level_threshold
        points_needed = 5 + (level * 5)  # Increasing difficulty (5, 10, 15, 20, 25...)
        level_threshold += points_needed
    
    # Calculate points in current level and points needed for next level
    points_in_current_level = total_points - previous_threshold
    
    return level, points_in_current_level, points_needed

# ---- Session State Initialization ----
st.session_state.users = load_users()
if "selected_user" not in st.session_state:
    st.session_state.selected_user = st.session_state.users[0] if st.session_state.users else None
bank_data = load_bank()
st.session_state.activity_logs = load_activity_logs()
if "activities" not in st.session_state:
    st.session_state.activities = bank_data.get("activities", [
        {"name": "Run 5km", "points": 10},
        {"name": "Yoga 30min", "points": 5}
    ])
if "dreams" not in st.session_state:
    st.session_state.dreams = bank_data.get("dreams", [
        {"name": "Weekend Trip", "cost": 100, "purchased_by": []}
    ])
if "user_banks" not in st.session_state:
    if "user_banks" in bank_data:
        st.session_state.user_banks = bank_data["user_banks"]
    else:
        # Initialize user banks with activity points and empty treats list for each user
        st.session_state.user_banks = {
            user: {
                "activity_points": 0, 
                "treats": [{"name": "Ice Cream", "cost": 15, "purchased": False}]
            } 
            for user in st.session_state.users
        }

if "activity_logs" not in st.session_state:
    st.session_state.activity_logs = {user: [] for user in st.session_state.users}
if "dream_bank" not in st.session_state:
    st.session_state.dream_bank = bank_data.get("dream_bank", 0)

# ---- User Selection ----
st.title("🏋️ Workout Motivation App")

st.subheader("Users")
if st.session_state.users:
    user = st.selectbox("Select User", st.session_state.users, key="user_select")
    st.session_state.selected_user = user
    user_bank = st.session_state.user_banks.get(user, {"activity_points": 0})

    # Calculate user level
    total_points = user_bank["activity_points"]
    user_level, points_in_level, points_needed = calculate_level(total_points)

    # Clamp points_in_level to [0, points_needed]
    points_in_level = max(0, min(points_in_level, points_needed))
    # Show level info at the top
    level_col1, level_col2 = st.columns([3, 1])
    with level_col1:
        st.header(f"Hello, {user}!")
        st.subheader(f"Level {user_level} - {points_in_level}/{points_needed} points to next level")
        # Progress bar for level
        level_progress = points_in_level / points_needed if points_needed > 0 else 0
        level_progress = max(0.0, min(level_progress, 1.0))
        st.progress(level_progress, text=f"{int(level_progress * 100)}% to Level {user_level + 1}")

        # Show rewards for leveling up (10% of points needed for next level, min 1)
        import math
        next_level_points = points_needed if points_needed > 0 else 1
        level_bonus = max(1, math.ceil(next_level_points * 0.10))
        st.info(f"🏆 Level rewards: +{level_bonus} bonus points at each new level!")
    with level_col2:
        st.metric("Total Points", total_points)
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
                    # Add to user_banks with default treats
                    st.session_state.user_banks[new_user] = {
                        "activity_points": 0,
                        "treats": [{"name": "Ice Cream", "cost": 15, "purchased": False}]
                    }
                    # Initialize empty activity log for the new user
                    st.session_state.activity_logs[new_user] = []
                    save_activity_logs()
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
        
        # Get current level
        current_level, _, _ = calculate_level(st.session_state.user_banks[user]["activity_points"])

        # Update user points
        st.session_state.user_banks[user]["activity_points"] += points

        # Check for level up
        new_level, _, _ = calculate_level(st.session_state.user_banks[user]["activity_points"])
        bonus_points = 0

        if new_level > current_level:
            # Award bonus points for leveling up (5% of current level, min 1)
            bonus_points = max(1, int(new_level * 0.05))
            st.session_state.user_banks[user]["activity_points"] += bonus_points

        # Add to activity log with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if user not in st.session_state.activity_logs:
            st.session_state.activity_logs[user] = []

        st.session_state.activity_logs[user].append({
            "timestamp": timestamp,
            "activity": activity_choice,
            "points": points
        })

        # If there was a level up, add a bonus entry
        if bonus_points > 0:
            st.session_state.activity_logs[user].append({
                "timestamp": timestamp,
                "activity": f"LEVEL UP BONUS (Level {new_level})",
                "points": bonus_points
            })

        save_bank()
        save_activity_logs()

        if bonus_points > 0:
            st.success(f"{activity_choice} completed! +{points} points. 🎉 LEVEL UP to Level {new_level}! +{bonus_points} bonus points!")
        else:
            st.success(f"{activity_choice} completed! +{points} points.")

if user:
    # Activity History dropdown
    with st.expander("📋 Activity History"):
        if user in st.session_state.activity_logs and st.session_state.activity_logs[user]:
            st.write("Your completed activities:")
            
            # Sort activity logs by timestamp (newest first)
            sorted_logs = sorted(
                st.session_state.activity_logs[user], 
                key=lambda x: x['timestamp'], 
                reverse=True
            )
            
            # Display total points from activities
            total_activity_points = sum(log['points'] for log in sorted_logs)
            st.info(f"Total points earned: {total_activity_points}")
            
            # Show each activity with its details
            for idx, activity_log in enumerate(sorted_logs):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{activity_log['activity']}** - {activity_log['points']} pts - {activity_log['timestamp']}")
                
                with col3:
                    # Delete activity log button
                    if st.button("🗑️", key=f"delete_activity_log_{idx}"):
                        # Find the original index in the unsorted list
                        original_idx = st.session_state.activity_logs[user].index(activity_log)
                        # Remove points from user's total
                        st.session_state.user_banks[user]["activity_points"] -= activity_log["points"]
                        # Delete the activity from logs
                        st.session_state.activity_logs[user].pop(original_idx)
                        save_bank()
                        save_activity_logs()
                        st.success(f"Activity log deleted and {activity_log['points']} points removed.")
                        st.rerun()
        else:
            st.info("No activity history yet. Complete activities to see them here.")

# ---- Treats ----
st.header("🎁 Treats")

# Only proceed if a user is selected
if user:
    user_treats = user_bank.get("treats", [])
    
    with st.expander("Your Treats"):
        if not user_treats:
            st.write("_No treats yet!_")
            
        for idx, treat in enumerate(user_treats):
            treat_cols = st.columns([4,1,1])
            with treat_cols[0]:
                purchased = treat.get("purchased", False)
                st.write(f"**{treat['name']}** - Cost: {treat['cost']} pts")
                if purchased:
                    st.success("Purchased!")
                else:
                    points = user_bank["activity_points"]
                    percent = min(max(points / treat["cost"], 0.0), 1.0) * 100
                    points_needed = max(treat["cost"] - points, 0)
                    st.progress(percent / 100, text=f"{percent:.1f}% complete")
                    st.write(f"Points needed: {points_needed}")
                    
                    # Add buy button directly under treat
                    if points >= treat["cost"]:
                        if st.button("Buy", key=f"buy_treat_{idx}"):
                            # Purchase the treat
                            user_bank["treats"][idx]["purchased"] = True
                            user_bank["activity_points"] -= treat["cost"]
                            st.session_state.dream_bank += treat["cost"]
                            save_bank()
                            st.success(f"Treat '{treat['name']}' purchased! Points moved to Dream Bank.")
                            st.rerun()
                    else:
                        st.button("Buy", key=f"buy_treat_{idx}", disabled=True)
            with treat_cols[1]:
                if st.button("✏️", key=f"edit_treat_btn_{idx}", help="Edit Treat"):
                    st.session_state[f"edit_treat_form_{idx}"] = True
            with treat_cols[2]:
                if st.button("🗑️", key=f"delete_treat_{idx}", help="Delete Treat"):
                    user_bank["treats"].pop(idx)
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
                            user_bank["treats"][idx] = {
                                "name": edit_name, 
                                "cost": edit_cost, 
                                "purchased": treat.get("purchased", False)
                            }
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
                if "treats" not in user_bank:
                    user_bank["treats"] = []
                    
                user_bank["treats"].append(
                    {"name": treat_name, "cost": treat_cost, "purchased": False}
                )
                save_bank()
                st.success("Treat added!")
                st.rerun()

    # Treats purchased percentage
    if user_treats:
        purchased = sum(1 for t in user_treats if t.get("purchased", False))
        total = len(user_treats)
        percent = (purchased / total) * 100 if total > 0 else 0
        st.info(f"Treats Purchased: {purchased} / {total} ({percent:.1f}%)")

    # Removed dropdown purchase section as we now have inline buy buttons
else:
    st.info("Please select a user to manage treats.")

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
                percent = min(max(points / dream["cost"], 0.0), 1.0) * 100
                points_needed = max(dream["cost"] - points, 0)
                st.progress(percent / 100, text=f"{percent:.1f}% complete")
                st.write(f"Points needed: {points_needed}")
                
                # Add buy button directly under dream
                if user and points >= dream["cost"]:
                    if st.button("Buy", key=f"buy_dream_{idx}"):
                        # Purchase the dream
                        dream["purchased_by"].append(user)
                        st.session_state.dream_bank -= dream["cost"]
                        save_bank()
                        st.success(f"Dream '{dream['name']}' purchased!")
                        st.rerun()
                elif user:
                    st.button("Buy", key=f"buy_dream_{idx}", disabled=True)
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

# Removed dropdown purchase section as we now have inline buy buttons

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
    st.markdown("### User Management")

    # Delete User
    if st.session_state.users:
        st.markdown("**Delete User**: Permanently remove a user account.")
        delete_user_col1, delete_user_col2 = st.columns([3, 1])
        
        with delete_user_col1:
            user_to_delete = st.selectbox(
                "Select User to Delete",
                options=st.session_state.users,
                key="admin_delete_user"
            )
        
        with delete_user_col2:
            st.write(" ")  # Spacer for alignment
            if st.button("Delete User"):
                # Show confirmation dialog
                st.session_state["show_delete_confirmation"] = True
                st.session_state["user_to_delete"] = user_to_delete
        
        # Delete User Confirmation dialog
        if st.session_state.get("show_delete_confirmation", False):
            user_to_delete = st.session_state.get("user_to_delete")
            
            st.error(f"⚠️ Are you sure you want to delete user **{user_to_delete}**? All their data will be lost. This cannot be undone.")
            
            delete_confirm_col1, delete_confirm_col2 = st.columns([1, 1])
            with delete_confirm_col1:
                if st.button("Yes, Delete User"):
                    if user_to_delete:
                        st.session_state.users.remove(user_to_delete)
                        save_users(st.session_state.users)
                        st.session_state.user_banks.pop(user_to_delete, None)
                        save_bank()
                        st.session_state.selected_user = st.session_state.users[0] if st.session_state.users else None
                        st.session_state["show_delete_confirmation"] = False
                        st.success(f"User '{user_to_delete}' deleted!")
                        st.rerun()
            
            with delete_confirm_col2:
                if st.button("Cancel Delete"):
                    st.session_state["show_delete_confirmation"] = False
                    st.rerun()

    st.markdown("---")
    st.markdown("### Reset User Activity Points")
    
    if st.session_state.users:
        user_to_reset = st.selectbox("Select User", 
                                    options=st.session_state.users,
                                    key="admin_user_reset",
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
                        # Reset purchased status on all treats
                        if "treats" in st.session_state.user_banks[user_to_reset]:
                            for treat in st.session_state.user_banks[user_to_reset]["treats"]:
                                treat["purchased"] = False
                        # Clear activity log for the user
                        if user_to_reset in st.session_state.activity_logs:
                            st.session_state.activity_logs[user_to_reset] = []
                            save_activity_logs()
                        save_bank()
                        st.session_state["show_user_reset_confirmation"] = False
                        st.success(f"{user_to_reset}'s activity points and activity log have been reset to 0 and treats marked as unpurchased!")
                        st.rerun()

            with user_confirm_col2:
                if st.button("Cancel Reset"):
                    st.session_state["show_user_reset_confirmation"] = False
                    st.rerun()
    else:
        st.info("No users available to reset.")

st.caption("Made with ❤️ using Streamlit. Data is session-based and resets on reload.")
