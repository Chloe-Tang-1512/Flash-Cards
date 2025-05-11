import random
import difflib
import json
import os
import gzip
import hashlib
import csv
import datetime
import streamlit as st

# Utility Functions
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

# Streamlit Login Function
def login_ui(user_data):
    st.title("Flash Card Program")
    st.subheader("Login or Create an Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    action = st.radio("Action", ["Login", "Create Account"])

    if st.button("Submit"):
        if action == "Login":
            if username in user_data:
                if verify_password(user_data[username]["password"], password):
                    st.success(f"Welcome back, {username}!")
                    st.session_state["username"] = username
                    return username, user_data
                else:
                    st.error("Incorrect password. Please try again.")
            else:
                st.error("Username not found. Please create an account.")
        elif action == "Create Account":
            if username in user_data:
                st.error("This username already exists. Please choose a different username.")
            else:
                hashed_password = hash_password(password)
                user_data[username] = {"password": hashed_password, "flashcard_sets": {}}
                save_user_data(user_data)
                st.success(f"Account created successfully! Welcome, {username}!")
                st.session_state["username"] = username
                return username, user_data
    return None, user_data

# Flashcard Game with Automatic Flip on Incorrect Answer
def flash_card_game_ui(flash_cards):
    st.subheader("Flash Card Game")
    st.write("You will be shown a term, and you need to guess its definition.")

    # Check if the flashcard set is empty
    if not flash_cards["terms"]:
        st.warning("This flashcard set is empty. Please add terms before playing.")
        return

    # Shuffle terms for randomness
    if "shuffled_terms" not in st.session_state:
        st.session_state["shuffled_terms"] = random.sample(list(flash_cards["terms"].keys()), len(flash_cards["terms"]))

    # Initialize session state for tracking the current term
    if "current_index" not in st.session_state:
        st.session_state["current_index"] = 0

    # Ensure the index is within bounds
    if st.session_state["current_index"] >= len(st.session_state["shuffled_terms"]):
        st.success("You have completed all the flashcards!")
        return

    # Get the current term and definition
    current_term = st.session_state["shuffled_terms"][st.session_state["current_index"]]
    correct_answer = flash_cards["terms"][current_term]["definition"]

    # HTML, CSS, and JavaScript for the flip animation
    flip_card_html = f"""
    <div class="flip-card">
        <div class="flip-card-inner" id="flip-card-inner">
            <div class="flip-card-front">
                <h2>{current_term}</h2>
            </div>
            <div class="flip-card-back">
                <h3>{correct_answer}</h3>
            </div>
        </div>
    </div>
    <style>
        .flip-card {{
            background-color: transparent;
            width: 300px;
            height: 200px;
            perspective: 1000px;
            margin: auto;
        }}
        .flip-card-inner {{
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.6s;
            transform-style: preserve-3d;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        }}
        .flip-card-inner.flipped {{
            transform: rotateY(180deg);
        }}
        .flip-card-front, .flip-card-back {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: Arial, sans-serif;
        }}
        .flip-card-front {{
            background-color: #2980b9;
            color: white;
        }}
        .flip-card-back {{
            background-color: #f39c12;
            color: white;
            transform: rotateY(180deg);
        }}
    </style>
    <script>
        function flipCard() {{
            const card = document.getElementById('flip-card-inner');
            card.classList.add('flipped');
        }}
    </script>
    """

    # Embed the flip card in Streamlit
    st.components.v1.html(flip_card_html, height=250)

    # Input for user answer
    user_answer = st.text_input("Your definition:")

    if st.button("Submit"):
        similarity = difflib.SequenceMatcher(None, user_answer.lower(), correct_answer.lower()).ratio()

        flash_cards["terms"][current_term]["total"] += 1
        flash_cards["stats"]["total"] += 1
        if similarity > 0.7:
            st.success("Correct!")
            flash_cards["terms"][current_term]["correct"] += 1
            flash_cards["stats"]["correct"] += 1
        elif similarity > 0.4:
            st.warning(f"Almost correct! Here's a hint: {correct_answer[:len(correct_answer)//2]}...")
        else:
            st.error(f"Incorrect. The correct definition is: {correct_answer}")

            # Trigger the card flip when the answer is incorrect
            st.components.v1.html(
                f"""
                <script>
                    flipCard();
                </script>
                """,
                height=0,
            )

        # Move to the next term
        st.session_state["current_index"] += 1

    # Avoid division by zero
    if flash_cards["stats"]["total"] > 0:
        flash_cards["stats"]["percentage"] = (flash_cards["stats"]["correct"] / flash_cards["stats"]["total"]) * 100
    else:
        flash_cards["stats"]["percentage"] = 0.0

# Daily Challenge
def daily_challenge_ui(user_data, username):
    st.subheader("Daily Challenge")
    today = datetime.date.today().isoformat()

    # Initialize daily challenge in session state
    if "daily_challenge" not in st.session_state or st.session_state["daily_challenge"]["date"] != today:
        st.session_state["daily_challenge"] = {
            "date": today,
            "goal": 10,  # Example goal: Answer 10 questions correctly
            "progress": 0,
            "completed": False,
        }

    challenge = st.session_state["daily_challenge"]

    st.write(f"**Date:** {challenge['date']}")
    st.write(f"**Goal:** Answer {challenge['goal']} questions correctly")
    st.write(f"**Progress:** {challenge['progress']}/{challenge['goal']}")
    st.write(f"**Completed:** {'Yes' if challenge['completed'] else 'No'}")

    if st.button("Mark Progress"):
        if not challenge["completed"]:
            challenge["progress"] += 1
            if challenge["progress"] >= challenge["goal"]:
                challenge["completed"] = True
                st.success("Congratulations! You completed today's challenge!")
            else:
                st.info(f"Progress updated: {challenge['progress']}/{challenge['goal']}")
        else:
            st.info("Today's challenge is already completed!")

# Import Flashcard Set
def import_flashcard_set_ui(user_data, username):
    st.subheader("Import Flashcard Set")
    uploaded_file = st.file_uploader("Upload a JSON or CSV file:", type=["json", "csv"])
    if uploaded_file:
        set_name = st.text_input("Enter a name for the imported flashcard set:")
        if uploaded_file.name.endswith(".json"):
            try:
                flashcard_set = json.load(uploaded_file)
                if st.button("Import"):
                    user_data[username]["flashcard_sets"][set_name] = flashcard_set
                    save_user_data(user_data)
                    st.success(f"Flashcard set '{set_name}' imported successfully!")
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please upload a valid flashcard set.")
        elif uploaded_file.name.endswith(".csv"):
            flashcard_set = {"terms": {}, "stats": {"correct": 0, "total": 0, "percentage": 0.0}}
            try:
                reader = csv.DictReader(uploaded_file.read().decode("utf-8").splitlines())
                for row in reader:
                    term = row["Term"]
                    definition = row["Definition"]
                    correct = int(row["Correct"])
                    total = int(row["Total"])
                    flashcard_set["terms"][term] = {"definition": definition, "correct": correct, "total": total}
                if st.button("Import"):
                    user_data[username]["flashcard_sets"][set_name] = flashcard_set
                    save_user_data(user_data)
                    st.success(f"Flashcard set '{set_name}' imported successfully!")
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

# Export Flashcard Set
def export_flashcard_set_ui(user_data, username):
    st.subheader("Export Flashcard Set")
    flashcard_sets = user_data[username]["flashcard_sets"]
    set_name = st.selectbox("Select a flashcard set to export:", list(flashcard_sets.keys()))
    file_format = st.radio("Select file format:", ["JSON", "CSV"])
    if st.button("Export"):
        if file_format == "JSON":
            file_name = f"{set_name}.json"
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(flashcard_sets[set_name], file, indent=4)
            st.success(f"Flashcard set exported as {file_name}")
        elif file_format == "CSV":
            file_name = f"{set_name}.csv"
            with open(file_name, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Term", "Definition", "Correct", "Total"])
                for term, data in flashcard_sets[set_name]["terms"].items():
                    writer.writerow([term, data["definition"], data["correct"], data["total"]])
            st.success(f"Flashcard set exported as {file_name}")

# Main Function
def main():
    user_data = load_user_data()

    if "username" not in st.session_state:
        st.session_state["username"] = None

    if st.session_state["username"] is None:
        username, user_data = login_ui(user_data)
        if username:
            st.session_state["username"] = username
    else:
        username = st.session_state["username"]
        st.sidebar.title("Main Menu")
        menu = st.sidebar.radio(
            "Select an option:",
            [
                "Play Flashcard Game",
                "Daily Challenge",
                "Import Flashcard Set",
                "Export Flashcard Set",
            ],
        )
        if menu == "Play Flashcard Game":
            flashcard_sets = user_data[username]["flashcard_sets"]
            set_name = st.selectbox("Select a flashcard set to play:", list(flashcard_sets.keys()))
            if set_name:
                flash_card_game_ui(flashcard_sets[set_name])
        elif menu == "Daily Challenge":
            daily_challenge_ui(user_data, username)
        elif menu == "Import Flashcard Set":
            import_flashcard_set_ui(user_data, username)
        elif menu == "Export Flashcard Set":
            export_flashcard_set_ui(user_data, username)

if __name__ == "__main__":
    main()