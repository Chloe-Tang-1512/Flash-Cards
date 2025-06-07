import streamlit as st
import hashlib
import json
import os
import gzip
import csv
import datetime
import random
import difflib

# Helper functions
def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a provided password against the stored hashed password."""
    return stored_password == hash_password(provided_password)

def load_user_data():
    """Load user data from a compressed JSON file."""
    if os.path.exists("user_data.json.gz"):
        with gzip.open("user_data.json.gz", "rt", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_user_data(user_data):
    """Save user data to a compressed JSON file."""
    with gzip.open("user_data.json.gz", "wt", encoding="utf-8") as file:
        json.dump(user_data, file, indent=4)

# Streamlit app
st.title("Flashcards Application")

# Authentication
user_data = load_user_data()
if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:
    st.subheader("Login or Create an Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in user_data and verify_password(user_data[username]["password"], password):
            st.session_state.username = username
            st.success(f"Welcome back, {username}!")
        else:
            st.error("Invalid username or password.")
    if st.button("Create Account"):
        if username in user_data:
            st.error("Username already exists.")
        else:
            hashed_password = hash_password(password)
            user_data[username] = {"password": hashed_password, "flashcard_sets": {}}
            save_user_data(user_data)
            st.session_state.username = username
            st.success(f"Account created successfully! Welcome, {username}!")

if st.session_state.username:
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    user_flashcard_sets = user_data[st.session_state.username]["flashcard_sets"]

    # Sidebar navigation
    menu = st.sidebar.radio("Menu", ["Create Flashcard Set", "View Flashcard Sets", "Play Flashcards", "Edit Flashcard Set", "Delete Flashcard Set", "Account Management", "Daily Challenge", "Leaderboard", "Import/Export Flashcards"])

    if menu == "Create Flashcard Set":
        st.subheader("Create a New Flashcard Set")
        set_name = st.text_input("Flashcard Set Name")
        category = st.text_input("Category")
        if st.button("Create Set"):
            if set_name in user_flashcard_sets:
                st.error("Flashcard set already exists.")
            else:
                user_flashcard_sets[set_name] = {"category": category, "terms": {}, "stats": {"correct": 0, "total": 0, "percentage": 0.0}}
                save_user_data(user_data)
                st.success(f"Flashcard set '{set_name}' created successfully!")

    elif menu == "View Flashcard Sets":
        st.subheader("View Flashcard Sets")
        for set_name, flashcard_set in user_flashcard_sets.items():
            st.write(f"Set: {set_name}, Category: {flashcard_set.get('category', 'Uncategorized')}, Correct: {flashcard_set['stats']['correct']}, Total: {flashcard_set['stats']['total']}")

    elif menu == "Play Flashcards":
        st.subheader("Play Flashcards")
        set_name = st.selectbox("Select a Flashcard Set", list(user_flashcard_sets.keys()))
        if set_name:
            flashcard_set = user_flashcard_sets[set_name]
            terms = list(flashcard_set["terms"].keys())
            random.shuffle(terms)
            for term in terms:
                st.write(f"Term: {term}")
                user_answer = st.text_input("Your Answer")
                if st.button("Submit"):
                    correct_answer = flashcard_set["terms"][term]["definition"]
                    similarity = difflib.SequenceMatcher(None, user_answer.lower(), correct_answer.lower()).ratio()
                    flashcard_set["terms"][term]["total"] += 1
                    flashcard_set["stats"]["total"] += 1
                    if similarity > 0.7:
                        flashcard_set["terms"][term]["correct"] += 1
                        flashcard_set["stats"]["correct"] += 1
                        st.success("Correct!")
                    else:
                        st.error(f"Incorrect. Correct answer: {correct_answer}")
                    save_user_data(user_data)

    elif menu == "Edit Flashcard Set":
        st.subheader("Edit Flashcard Set")
        set_name = st.selectbox("Select a Flashcard Set", list(user_flashcard_sets.keys()))
        if set_name:
            flashcard_set = user_flashcard_sets[set_name]
            term = st.text_input("Term")
            definition = st.text_input("Definition")
            if st.button("Add Term"):
                flashcard_set["terms"][term] = {"definition": definition, "correct": 0, "total": 0}
                save_user_data(user_data)
                st.success(f"Term '{term}' added successfully!")

    elif menu == "Delete Flashcard Set":
        st.subheader("Delete Flashcard Set")
        set_name = st.selectbox("Select a Flashcard Set", list(user_flashcard_sets.keys()))
        if st.button("Delete Set"):
            del user_flashcard_sets[set_name]
            save_user_data(user_data)
            st.success(f"Flashcard set '{set_name}' deleted successfully!")

    elif menu == "Account Management":
        st.subheader("Account Management")
        new_password = st.text_input("New Password", type="password")
        if st.button("Change Password"):
            user_data[st.session_state.username]["password"] = hash_password(new_password)
            save_user_data(user_data)
            st.success("Password updated successfully!")

    elif menu == "Daily Challenge":
        st.subheader("Daily Challenge")
        today = datetime.date.today()
        daily_challenge = {"date": today.isoformat(), "goal": 10, "progress": 0, "completed": False}
        st.write(f"Date: {daily_challenge['date']}")
        st.write(f"Goal: {daily_challenge['goal']}, Progress: {daily_challenge['progress']}, Completed: {daily_challenge['completed']}")

    elif menu == "Leaderboard":
        st.subheader("Leaderboard")
        leaderboard = [{"username": username, "correct": sum(set["stats"]["correct"] for set in user_data[username]["flashcard_sets"].values())} for username in user_data]
        leaderboard.sort(key=lambda x: x["correct"], reverse=True)
        for rank, entry in enumerate(leaderboard, start=1):
            st.write(f"{rank}. {entry['username']} - Correct Answers: {entry['correct']}")

    elif menu == "Import/Export Flashcards":
        st.subheader("Import/Export Flashcards")
        uploaded_file = st.file_uploader("Upload a Flashcard Set (JSON or CSV)")
        if uploaded_file:
            if uploaded_file.name.endswith(".json"):
                flashcard_set = json.load(uploaded_file)
                set_name = st.text_input("Set Name")
                if st.button("Import"):
                    user_flashcard_sets[set_name] = flashcard_set
                    save_user_data(user_data)
                    st.success(f"Flashcard set '{set_name}' imported successfully!")
            elif uploaded_file.name.endswith(".csv"):
                flashcard_set = {"terms": {}, "stats": {"correct": 0, "total": 0, "percentage": 0.0}}
                reader = csv.DictReader(uploaded_file)
                for row in reader:
                    flashcard_set["terms"][row["Term"]] = {"definition": row["Definition"], "correct": int(row["Correct"]), "total": int(row["Total"])}
                set_name = st.text_input("Set Name")
                if st.button("Import"):
                    user_flashcard_sets[set_name] = flashcard_set
                    save_user_data(user_data)
                    st.success(f"Flashcard set '{set_name}' imported successfully!")
