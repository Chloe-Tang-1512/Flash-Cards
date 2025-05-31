import random
import difflib
import json
import os
import gzip
import hashlib
import msvcrt  # Import for custom password masking with asterisks
import csv  # Import for CSV handling
import datetime  # Import for tracking daily challenges

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

def input_password(prompt="Enter your password: "):
    """Custom password input function that displays asterisks."""
    print(prompt, end="", flush=True)
    password = ""
    while True:
        char = msvcrt.getch()
        if char in {b"\r", b"\n"}:  # Enter key pressed
            print()  # Move to the next line
            break
        elif char == b"\x08":  # Backspace key pressed
            if len(password) > 0:
                password = password[:-1]
                print("\b \b", end="", flush=True)  # Erase the last asterisk
        elif char == b"\x03":  # Ctrl+C pressed
            raise KeyboardInterrupt  # Allow Ctrl+C to interrupt
        else:
            password += char.decode("utf-8")
            print("*", end="", flush=True)  # Display an asterisk
    return password

def login():
    """Prompt the user to log in or create a new account with a password."""
    user_data = load_user_data()
    print("Welcome to the Flash Card Program!")
    while True:
        username = input("Enter your username (or type 'new' to create an account): ").strip()
        if username.lower() == "new":
            new_username = input("Enter a new username: ").strip()
            if new_username in user_data:
                print("This username already exists. Please try again.")
            else:
                password = input_password("Enter a password: ").strip()
                hashed_password = hash_password(password)
                user_data[new_username] = {
                    "password": hashed_password,
                    "flashcard_sets": {}
                }
                save_user_data(user_data)
                print(f"Account created successfully! Welcome, {new_username}!")
                return new_username, user_data
        elif username in user_data:
            password = input_password("Enter your password: ").strip()
            stored_hashed_password = user_data[username]["password"]
            if verify_password(stored_hashed_password, password):
                print(f"Welcome back, {username}!")
                return username, user_data
            else:
                print("Incorrect password. Please try again.")
        else:
            print("Username not found. Please try again or type 'new' to create an account.")

def flash_card_game(flash_cards):
    """Play a flashcard game with shuffled terms and prioritize terms the user struggles with."""
    print("Welcome to the Flash Card Game!")
    print("You will be shown a term, and you need to guess its definition.")
    print("Type 'exit' to quit the game.\n")

    # Prioritize terms the user struggles with
    terms = sorted(
        flash_cards["terms"].keys(),
        key=lambda term: (
            flash_cards["terms"][term]["total"] - flash_cards["terms"][term]["correct"]
        ),
        reverse=True,
    )

    score = 0
    total_questions = len(terms)

    for term in terms:
        print(f"Term: {term}")
        user_answer = input("Your definition: ").strip()

        if user_answer.lower() == "exit":
            print("Thanks for playing! Returning to the main menu...\n")
            break

        correct_answer = flash_cards["terms"][term]["definition"]
        similarity = difflib.SequenceMatcher(None, user_answer.lower(), correct_answer.lower()).ratio()

        flash_cards["terms"][term]["total"] += 1
        flash_cards["stats"]["total"] += 1
        if similarity > 0.7:
            print("Correct!\n")
            score += 1
            flash_cards["terms"][term]["correct"] += 1
            flash_cards["stats"]["correct"] += 1
        elif similarity > 0.4:
            print(f"Almost correct! Here's a hint: {correct_answer[:len(correct_answer)//2]}...\n")
        else:
            print(f"Incorrect. The correct definition is: {correct_answer}\n")

    if flash_cards["stats"]["total"] > 0:  # Avoid division by zero
        flash_cards["stats"]["percentage"] = (flash_cards["stats"]["correct"] / flash_cards["stats"]["total"]) * 100
    else:
        flash_cards["stats"]["percentage"] = 0.0

    print(f"You answered {score} out of {total_questions} questions correctly!")
    print("You've gone through all the flash cards. Great job!")

def calculate_user_level(flashcard_sets):
    """Calculate the user's level based on their overall performance."""
    total_correct = 0
    total_attempts = 0

    for set_name, flash_cards in flashcard_sets.items():
        total_correct += flash_cards["stats"]["correct"]
        total_attempts += flash_cards["stats"]["total"]

    if total_attempts == 0:  # Avoid division by zero
        return "Unranked"

    overall_percentage = (total_correct / total_attempts) * 100
    if overall_percentage <= 40:
        return "Beginner"
    elif overall_percentage <= 70:
        return "Intermediate"
    elif overall_percentage <= 90:
        return "Advanced"
    else:
        return "Expert"

def track_progress(flashcard_set):
    """Display progress for a specific flashcard set."""
    total_terms = len(flashcard_set["terms"])
    learned_terms = sum(1 for term in flashcard_set["terms"].values() if term["correct"] > 0)
    total_attempts = flashcard_set["stats"]["total"]
    correct_answers = flashcard_set["stats"]["correct"]
    accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0

    print("\nProgress Report:")
    print(f"- Total terms: {total_terms}")
    print(f"- Learned terms: {learned_terms}/{total_terms}")
    print(f"- Total attempts: {total_attempts}")
    print(f"- Correct answers: {correct_answers}")
    print(f"- Accuracy: {accuracy:.2f}%")

    # Identify terms that need more practice
    print("\nTerms that need more practice:")
    for term, data in flashcard_set["terms"].items():
        if data["total"] > 0 and (data["correct"] / data["total"]) < 0.5:  # Less than 50% accuracy
            print(f"- {term}: {data['correct']}/{data['total']} correct")
    print()

def edit_flashcard_set(flashcard_set):
    """Edit terms and definitions in a flashcard set."""
    while True:
        print("\nEdit Flashcard Set:")
        print("1. Add a new term")
        print("2. Edit an existing term")
        print("3. Delete a term")
        print("4. Return to the main menu")
        choice = input("Enter your choice (1/2/3/4): ").strip()

        if choice == "1":
            term = input("Enter the new term: ").strip()
            if term in flashcard_set["terms"]:
                print(f"The term '{term}' already exists. Please choose a different term.")
            else:
                definition = input(f"Enter the definition for '{term}': ").strip()
                flashcard_set["terms"][term] = {"definition": definition, "correct": 0, "total": 0}
                print(f"Added: {term} -> {definition}")

        elif choice == "2":
            term = input("Enter the term you want to edit: ").strip()
            if term in flashcard_set["terms"]:
                new_definition = input(f"Enter the new definition for '{term}': ").strip()
                flashcard_set["terms"][term]["definition"] = new_definition
                print(f"Updated: {term} -> {new_definition}")
            else:
                print(f"The term '{term}' does not exist in this flashcard set.")

        elif choice == "3":
            term = input("Enter the term you want to delete: ").strip()
            if term in flashcard_set["terms"]:
                del flashcard_set["terms"][term]
                print(f"The term '{term}' has been deleted.")
            else:
                print(f"The term '{term}' does not exist in this flashcard set.")

        elif choice == "4":
            print("Returning to the main menu...\n")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.\n")

def manage_account(username, user_data):
    """Allow the user to view, edit, or delete their account."""
    while True:
        print("\nAccount Management:")
        print("1. View account details")
        print("2. Edit account details")
        print("3. Delete account")
        print("4. Return to the main menu")
        choice = input("Enter your choice (1/2/3/4): ").strip()

        if choice == "1":
            flashcard_sets = user_data[username]["flashcard_sets"]
            user_level = calculate_user_level(flashcard_sets)
            achievements = calculate_achievements(flashcard_sets)
            print(f"\nAccount Details for '{username}':")
            print(f"- Level: {user_level}")
            print(f"- Number of flashcard sets: {len(flashcard_sets)}")
            print("- Flashcard sets:")
            for set_name in flashcard_sets:
                print(f"  - {set_name}")
            print("\nAchievements:")
            for achievement in achievements:
                print(f"- {achievement}")
            print()

        elif choice == "2":
            print("\nEdit Account Details:")
            print("1. Change username")
            print("2. Change password")
            edit_choice = input("Enter your choice (1/2): ").strip()

            if edit_choice == "1":
                new_username = input("Enter your new username: ").strip()
                if new_username in user_data:
                    print("This username is already taken. Please try again.")
                else:
                    user_data[new_username] = user_data.pop(username)
                    username = new_username
                    save_user_data(user_data)
                    print(f"Your username has been updated to '{new_username}'.")

            elif edit_choice == "2":
                new_password = input_password("Enter your new password: ").strip()
                user_data[username]["password"] = hash_password(new_password)
                save_user_data(user_data)
                print("Your password has been updated successfully.")

            else:
                print("Invalid choice. Please enter 1 or 2.\n")

        elif choice == "3":
            confirm = input("Are you sure you want to delete your account? This action cannot be undone (yes/no): ").strip().lower()
            if confirm == "yes":
                final_confirm = input("Type your username to confirm account deletion: ").strip()
                if final_confirm == username:
                    del user_data[username]
                    save_user_data(user_data)
                    print("Your account has been deleted. Goodbye!")
                    exit()
                else:
                    print("Account deletion canceled. Username did not match.")
            else:
                print("Account deletion canceled.")

        elif choice == "4":
            print("Returning to the main menu...\n")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.\n")
    """Allow the user to view, edit, or delete their account."""
    while True:
        print("\nAccount Management:")
        print("1. View account details")
        print("2. Edit account details")
        print("3. Delete account")
        print("4. Return to the main menu")
        choice = input("Enter your choice (1/2/3/4): ").strip()

        if choice == "1":
            flashcard_sets = user_data[username]["flashcard_sets"]
            user_level = calculate_user_level(flashcard_sets)
            achievements = calculate_achievements(flashcard_sets)
            print(f"\nAccount Details for '{username}':")
            print(f"- Level: {user_level}")
            print(f"- Number of flashcard sets: {len(flashcard_sets)}")
            print("- Flashcard sets:")
            for set_name in flashcard_sets:
                print(f"  - {set_name}")
            print("\nAchievements:")
            for achievement in achievements:
                print(f"- {achievement}")
            print()

        elif choice == "2":
            print("\nEdit Account Details:")
            print("1. Change username")
            print("2. Change password")
            edit_choice = input("Enter your choice (1/2): ").strip()

            if edit_choice == "1":
                new_username = input("Enter your new username: ").strip()
                if new_username in user_data:
                    print("This username is already taken. Please try again.")
                else:
                    user_data[new_username] = user_data.pop(username)
                    username = new_username
                    save_user_data(user_data)
                    print(f"Your username has been updated to '{new_username}'.")

            elif edit_choice == "2":
                new_password = input_password("Enter your new password: ").strip()
                user_data[username]["password"] = hash_password(new_password)
                save_user_data(user_data)
                print("Your password has been updated successfully.")

            else:
                print("Invalid choice. Please enter 1 or 2.\n")

        elif choice == "3":
            confirm = input("Are you sure you want to delete your account? This action cannot be undone (yes/no): ").strip().lower()
            if confirm == "yes":
                del user_data[username]
                save_user_data(user_data)
                print("Your account has been deleted. Goodbye!")
                exit()
            else:
                print("Account deletion canceled.")

        elif choice == "4":
            print("Returning to the main menu...\n")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.\n")

def calculate_achievements(flashcard_sets):
    """Calculate achievements based on the user's progress."""
    achievements = []
    total_flashcard_sets = len(flashcard_sets)
    total_correct = sum(flashcard_sets[set_name]["stats"]["correct"] for set_name in flashcard_sets)
    total_attempts = sum(flashcard_sets[set_name]["stats"]["total"] for set_name in flashcard_sets)

    # Achievement: Completed 5 flashcard sets
    if total_flashcard_sets >= 5:
        achievements.append("Completed 5 flashcard sets!")

    # Achievement: Answered 100 questions
    if total_attempts >= 100:
        achievements.append("Answered 100 questions!")

    # Achievement: 80% or higher accuracy
    if total_attempts > 0 and (total_correct / total_attempts) >= 0.8:
        achievements.append("Achieved 80% or higher accuracy!")

    # Achievement: Mastered all terms in a set
    for set_name, flashcard_set in flashcard_sets.items():
        if all(term["correct"] > 0 for term in flashcard_set["terms"].values()):
            achievements.append(f"Mastered all terms in '{set_name}'!")

    return achievements
    """Allow the user to view, edit, or delete their account."""
    while True:
        print("\nAccount Management:")
        print("1. View account details")
        print("2. Edit account details")
        print("3. Delete account")
        print("4. Return to the main menu")
        choice = input("Enter your choice (1/2/3/4): ").strip()

        if choice == "1":
            flashcard_sets = user_data[username]["flashcard_sets"]
            user_level = calculate_user_level(flashcard_sets)
            print(f"\nAccount Details for '{username}':")
            print(f"- Level: {user_level}")
            print(f"- Number of flashcard sets: {len(flashcard_sets)}")
            print("- Flashcard sets:")
            for set_name in flashcard_sets:
                print(f"  - {set_name}")
            print()

        elif choice == "2":
            print("\nEdit Account Details:")
            print("1. Change username")
            print("2. Change password")
            edit_choice = input("Enter your choice (1/2): ").strip()

            if edit_choice == "1":
                new_username = input("Enter your new username: ").strip()
                if new_username in user_data:
                    print("This username is already taken. Please try again.")
                else:
                    user_data[new_username] = user_data.pop(username)
                    username = new_username
                    save_user_data(user_data)
                    print(f"Your username has been updated to '{new_username}'.")

            elif edit_choice == "2":
                new_password = input_password("Enter your new password: ").strip()
                user_data[username]["password"] = hash_password(new_password)
                save_user_data(user_data)
                print("Your password has been updated successfully.")

            else:
                print("Invalid choice. Please enter 1 or 2.\n")

        elif choice == "3":
            confirm = input("Are you sure you want to delete your account? This action cannot be undone (yes/no): ").strip().lower()
            if confirm == "yes":
                del user_data[username]
                save_user_data(user_data)
                print("Your account has been deleted. Goodbye!")
                exit()
            else:
                print("Account deletion canceled.")

        elif choice == "4":
            print("Returning to the main menu...\n")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.\n")

def export_flashcard_set(flashcard_set, file_format="json"):
    """Export a flashcard set to a JSON or CSV file."""
    set_name = flashcard_set.get("name", "flashcard_set")
    if file_format.lower() == "json":
        file_name = f"{set_name}.json"
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(flashcard_set, file, indent=4)
        print(f"Flashcard set exported as {file_name}")
    elif file_format.lower() == "csv":
        file_name = f"{set_name}.csv"
        with open(file_name, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Term", "Definition", "Correct", "Total"])
            for term, data in flashcard_set["terms"].items():
                writer.writerow([term, data["definition"], data["correct"], data["total"]])
        print(f"Flashcard set exported as {file_name}")
    else:
        print("Unsupported file format. Please choose 'json' or 'csv'.")

def import_flashcard_set(file_name):
    """Import a flashcard set from a JSON or CSV file."""
    if file_name.endswith(".json"):
        with open(file_name, "r", encoding="utf-8") as file:
            flashcard_set = json.load(file)
        print(f"Flashcard set imported from {file_name}")
        return flashcard_set
    elif file_name.endswith(".csv"):
        flashcard_set = {"terms": {}, "stats": {"correct": 0, "total": 0, "percentage": 0.0}}
        with open(file_name, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                term = row["Term"]
                definition = row["Definition"]
                correct = int(row["Correct"])
                total = int(row["Total"])
                flashcard_set["terms"][term] = {"definition": definition, "correct": correct, "total": total}
        print(f"Flashcard set imported from {file_name}")
        return flashcard_set
    else:
        print("Unsupported file format. Please provide a '.json' or '.csv' file.")
        return None

def manage_flashcard_import_export(flashcard_sets):
    """Allow users to import or export flashcard sets."""
    while True:
        print("\nImport/Export Flashcard Sets:")
        print("1. Export a flashcard set")
        print("2. Import a flashcard set")
        print("3. Return to the main menu")
        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            set_name = input("Enter the name of the flashcard set to export: ").strip()
            if set_name in flashcard_sets:
                file_format = input("Enter the file format (json/csv): ").strip().lower()
                export_flashcard_set(flashcard_sets[set_name], file_format)
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "2":
            file_name = input("Enter the file name to import (with extension): ").strip()
            imported_set = import_flashcard_set(file_name)
            if imported_set:
                set_name = input("Enter a name for the imported flashcard set: ").strip()
                if set_name in flashcard_sets:
                    print(f"A flashcard set named '{set_name}' already exists. Please choose a different name.")
                else:
                    flashcard_sets[set_name] = imported_set
                    print(f"Flashcard set '{set_name}' imported successfully!")

        elif choice == "3":
            print("Returning to the main menu...\n")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.\n")

def generate_daily_challenge():
    """Generate a daily challenge for the user."""
    today = datetime.date.today()
    challenge = {
        "date": today.isoformat(),
        "goal": 10,  # Example goal: Answer 10 questions correctly
        "progress": 0,  # Track progress toward the goal
        "completed": False
    }
    return challenge

def update_daily_challenge(challenge, correct_answers):
    """Update the progress of the daily challenge."""
    if correct_answers is None:  # Ensure correct_answers is not None
        correct_answers = 0

    if challenge["completed"]:
        print("Today's challenge is already completed!")
        return challenge

    challenge["progress"] += correct_answers
    if challenge["progress"] >= challenge["goal"]:
        challenge["completed"] = True
        print(f"Congratulations! You completed today's challenge: Answer {challenge['goal']} questions correctly!")
    else:
        print(f"Daily Challenge Progress: {challenge['progress']}/{challenge['goal']} correct answers.")
    return challenge

def display_daily_challenge(challenge):
    """Display the current daily challenge."""
    print("\nDaily Challenge:")
    print(f"- Goal: Answer {challenge['goal']} questions correctly")
    print(f"- Progress: {challenge['progress']}/{challenge['goal']}")
    print(f"- Completed: {'Yes' if challenge['completed'] else 'No'}\n")

def calculate_leaderboard(user_data):
    """Calculate and display a leaderboard ranking users by their levels and scores."""
    leaderboard = []

    for username, data in user_data.items():
        flashcard_sets = data.get("flashcard_sets", {})
        total_correct = sum(flashcard_sets[set_name]["stats"]["correct"] for set_name in flashcard_sets)
        total_attempts = sum(flashcard_sets[set_name]["stats"]["total"] for set_name in flashcard_sets)
        level = calculate_user_level(flashcard_sets)
        accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        leaderboard.append({
            "username": username,
            "level": level,
            "total_correct": total_correct,
            "total_attempts": total_attempts,
            "accuracy": accuracy
        })

    # Sort leaderboard by level and total_correct in descending order
    leaderboard.sort(key=lambda x: (x["level"], x["total_correct"]), reverse=True)

    print("\nLeaderboard:")
    print(f"{'Rank':<5} {'Username':<15} {'Level':<12} {'Correct':<10} {'Attempts':<10} {'Accuracy (%)':<12}")
    for rank, entry in enumerate(leaderboard, start=1):
        print(f"{rank:<5} {entry['username']:<15} {entry['level']:<12} {entry['total_correct']:<10} {entry['total_attempts']:<10} {entry['accuracy']:<12.2f}")
    print()
    
def search_flashcard_set(flashcard_set):
    """Search for terms or definitions in a flashcard set."""
    query = input("Enter a term or definition to search for: ").strip().lower()
    results = []

    for term, data in flashcard_set["terms"].items():
        if query in term.lower() or query in data["definition"].lower():
            results.append((term, data["definition"]))

    if results:
        print("\nSearch Results:")
        for term, definition in results:
            print(f"- {term}: {definition}")
    else:
        print("No matching terms or definitions found.")

def revision_mode(flash_cards):
    """Allow users to review flashcards without affecting their stats."""
    print("Welcome to Revision Mode!")
    print("You will be shown a term, and you can review its definition.")
    print("Type 'exit' to quit revision mode.\n")

    terms = list(flash_cards["terms"].keys())
    random.shuffle(terms)

    for term in terms:
        print(f"Term: {term}")
        user_input = input("Press Enter to reveal the definition or type 'exit' to quit: ").strip()

        if user_input.lower() == "exit":
            print("Exiting Revision Mode...\n")
            break

        print(f"Definition: {flash_cards['terms'][term]['definition']}\n")

def quiz_mode(flash_cards):
    """Allow users to take a multiple-choice quiz based on their flashcards."""
    print("Welcome to Quiz Mode!")
    print("You will be shown a term and four possible definitions.")
    print("Type the number corresponding to your answer or 'exit' to quit the quiz.\n")

    terms = list(flash_cards["terms"].keys())
    random.shuffle(terms)

    score = 0
    total_questions = len(terms)

    for term in terms:
        print(f"Term: {term}")
        correct_answer = flash_cards["terms"][term]["definition"]

        # Generate multiple-choice options
        options = [correct_answer]
        while len(options) < 4:
            random_term = random.choice(terms)
            random_definition = flash_cards["terms"][random_term]["definition"]
            if random_definition not in options:
                options.append(random_definition)
        random.shuffle(options)

        # Display options
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        # Get user input
        user_input = input("Your choice (1/2/3/4 or 'exit'): ").strip()
        if user_input.lower() == "exit":
            print("Exiting Quiz Mode...\n")
            break

        # Check the answer
        if user_input.isdigit() and 1 <= int(user_input) <= 4:
            selected_option = options[int(user_input) - 1]
            if selected_option == correct_answer:
                print("Correct!\n")
                score += 1
            else:
                print(f"Incorrect. The correct answer was: {correct_answer}\n")
        else:
            print("Invalid input. Please enter a number between 1 and 4 or 'exit'.\n")

    print(f"Quiz completed! You answered {score} out of {total_questions} questions correctly.\n")

def fill_in_the_blank_mode(flash_cards):
    """Allow users to guess missing words in definitions."""
    print("Welcome to Fill in the Blank Mode!")
    print("You will be shown a term and a definition with missing words, and you need to fill in the blanks.")
    print("Type 'exit' to quit this mode.\n")

    terms = list(flash_cards["terms"].keys())
    random.shuffle(terms)

    score = 0
    total_questions = len(terms)

    for term in terms:
        definition = flash_cards["terms"][term]["definition"]
        words = definition.split()
        if len(words) < 3:
            # Skip definitions that are too short to create blanks
            continue

        # Randomly select a word to blank out
        blank_index = random.randint(0, len(words) - 1)
        blanked_definition = words[:]
        blanked_definition[blank_index] = "____"
        print(f"Term: {term}")
        print(f"Definition: {' '.join(blanked_definition)}")

        user_input = input("Fill in the blank: ").strip()
        if user_input.lower() == "exit":
            print("Exiting Fill in the Blank Mode...\n")
            break

        correct_word = words[blank_index]
        if user_input.lower() == correct_word.lower():
            print("Correct!\n")
            score += 1
        else:
            print(f"Incorrect. The correct word was: {correct_word}\n")

    print(f"Fill in the Blank Mode completed! You answered {score} out of {total_questions} questions correctly.\n")
    
def main_menu():
    """Main menu for the flashcard program."""
    username, user_data = login()
    flashcard_sets = user_data[username]["flashcard_sets"]

    # Generate a daily challenge when the program starts
    daily_challenge = generate_daily_challenge()

    if "Python (default)" not in flashcard_sets:
        flashcard_sets["Python (default)"] = {
            "category": "Programming",
            "terms": {
                "Python": {"definition": "A high-level programming language.", "correct": 0, "total": 0},
                "Variable": {"definition": "A storage location paired with an associated symbolic name.", "correct": 0, "total": 0},
                "Function": {"definition": "A block of reusable code that performs a specific task.", "correct": 0, "total": 0},
                "Loop": {"definition": "A programming construct that repeats a block of code.", "correct": 0, "total": 0},
            },
            "stats": {"correct": 0, "total": 0, "percentage": 0.0}
        }
        save_user_data(user_data)  # Save the default flashcard set

    while True:
        user_level = calculate_user_level(flashcard_sets)
        print(f"\nMain Menu (Logged in as: {username} - Level: {user_level}):")
        print("1. Create a new flashcard set")
        print("2. View available flashcard sets")
        print("3. Play with a flashcard set")
        print("4. Edit a flashcard set")
        print("5. Delete a flashcard set")
        print("6. Manage account")
        print("7. View progress")
        print("8. Import/Export flashcard sets")
        print("9. View Daily Challenge")
        print("10. View Leaderboard")
        print("11. Search within a flashcard set")
        print("12. Revision Mode")
        print("13. Quiz Mode")
        print("14. Fill in the Blank Mode")  # Added option for Fill in the Blank Mode
        print("15. Save and Exit")
        choice = input("Enter your choice (1/2/3/4/5/6/7/8/9/10/11/12/13/14/15): ").strip()

        if choice == "1":
            set_name = input("Enter a name for your new flashcard set: ").strip()
            if set_name in flashcard_sets:
                print(f"A flashcard set named '{set_name}' already exists. Please choose a different name.")
            else:
                category = input("Enter a category for this flashcard set (e.g., Math, Science, History): ").strip()
                flashcard_sets[set_name] = {
                    "category": category,
                    "terms": {},
                    "stats": {"correct": 0, "total": 0, "percentage": 0.0}
                }
                save_user_data(user_data)  # Save after creating a new flashcard set
                print(f"Flashcard set '{set_name}' created successfully under the category '{category}'!")

                while True:
                    term = input("Enter a term (or type 'done' to finish adding terms): ").strip()
                    if term.lower() == "done":
                        print(f"Finished adding terms to '{set_name}'.")
                        break
                    if term in flashcard_sets[set_name]["terms"]:
                        print(f"The term '{term}' already exists. Please enter a different term.")
                    else:
                        definition = input(f"Enter the definition for '{term}': ").strip()
                        flashcard_sets[set_name]["terms"][term] = {"definition": definition, "correct": 0, "total": 0}
                        save_user_data(user_data)  # Save after adding a term
                        print(f"Added: {term} -> {definition}")

        elif choice == "2":
            print("\nView Flashcard Sets:")
            print("1. View all flashcard sets")
            print("2. View flashcard sets by category")
            view_choice = input("Enter your choice (1/2): ").strip()

            if view_choice == "1":
                print("\nAvailable Flashcard Sets:")
                for set_name, flash_cards in flashcard_sets.items():
                    correct = flash_cards["stats"]["correct"]
                    total = flash_cards["stats"]["total"]
                    percentage = flash_cards["stats"]["percentage"]
                    category = flash_cards.get("category", "Uncategorized")
                    print(f"- {set_name} (Category: {category}): {correct}/{total} correct ({percentage:.2f}%)")
                print()

            elif view_choice == "2":
                categories = set(flash_cards.get("category", "Uncategorized") for flash_cards in flashcard_sets.values())
                print("\nAvailable Categories:")
                for category in categories:
                    print(f"- {category}")
                selected_category = input("Enter the category you want to view: ").strip()

                print(f"\nFlashcard Sets in Category '{selected_category}':")
                for set_name, flash_cards in flashcard_sets.items():
                    if flash_cards.get("category", "Uncategorized") == selected_category:
                        correct = flash_cards["stats"]["correct"]
                        total = flash_cards["stats"]["total"]
                        percentage = flash_cards["stats"]["percentage"]
                        print(f"- {set_name}: {correct}/{total} correct ({percentage:.2f}%)")
                print()
            else:
                print("Invalid choice. Returning to the main menu.\n")

        elif choice == "3":
            set_name = input("Enter the name of the flashcard set you want to play with: ").strip()
            if set_name in flashcard_sets:
                score = flash_card_game(flashcard_sets[set_name])  # Capture the score from the game
                daily_challenge = update_daily_challenge(daily_challenge, score)  # Update daily challenge progress
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "4":
            set_name = input("Enter the name of the flashcard set you want to edit: ").strip()
            if set_name in flashcard_sets:
                edit_flashcard_set(flashcard_sets[set_name])
                save_user_data(user_data)  # Save after editing a flashcard set
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "5":
            set_name = input("Enter the name of the flashcard set you want to delete: ").strip()
            if set_name in flashcard_sets:
                if set_name == "Python (default)":
                    print("The default flashcard set cannot be deleted.")
                else:
                    del flashcard_sets[set_name]
                    save_user_data(user_data)  # Save after deleting a flashcard set
                    print(f"Flashcard set '{set_name}' deleted successfully!")
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "6":
            manage_account(username, user_data)

        elif choice == "7":
            print("\nView Progress:")
            print("1. View progress for all flashcard sets")
            print("2. View progress for a specific flashcard set")
            progress_choice = input("Enter your choice (1/2): ").strip()

            if progress_choice == "1":
                print("\nProgress for All Flashcard Sets:")
                for set_name, flash_cards in flashcard_sets.items():
                    print(f"\nFlashcard Set: {set_name}")
                    track_progress(flash_cards)

            elif progress_choice == "2":
                set_name = input("Enter the name of the flashcard set: ").strip()
                if set_name in flashcard_sets:
                    print(f"\nProgress for Flashcard Set: {set_name}")
                    track_progress(flashcard_sets[set_name])
                else:
                    print(f"No flashcard set named '{set_name}' found. Please try again.")
            else:
                print("Invalid choice. Returning to the main menu.\n")

        elif choice == "8":
            manage_flashcard_import_export(flashcard_sets)

        elif choice == "9":
            display_daily_challenge(daily_challenge)  # Display the daily challenge

        elif choice == "10":
            calculate_leaderboard(load_user_data())  # Display the leaderboard

        elif choice == "11":
            set_name = input("Enter the name of the flashcard set you want to search in: ").strip()
            if set_name in flashcard_sets:
                search_flashcard_set(flashcard_sets[set_name])  # Call the search function
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "12":
            set_name = input("Enter the name of the flashcard set you want to review: ").strip()
            if set_name in flashcard_sets:
                revision_mode(flashcard_sets[set_name])  # Call the revision mode function
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")
        elif choice == "13":
            set_name = input("Enter the name of the flashcard set you want to quiz with: ").strip()
            if set_name in flashcard_sets:
                quiz_mode(flashcard_sets[set_name])  # Call the quiz mode function
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")
        elif choice == "14":
            set_name = input("Enter the name of the flashcard set you want to use for Fill in the Blank Mode: ").strip()
            if set_name in flashcard_sets:
                fill_in_the_blank_mode(flashcard_sets[set_name])  # Call the Fill in the Blank Mode function
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")
        elif choice == "15":
            user_data[username]["flashcard_sets"] = flashcard_sets
            save_user_data(user_data)
            print("Your progress has been saved. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a valid option.\n")

    exit()
    """Main menu for the flashcard program."""
    username, user_data = login()
    flashcard_sets = user_data[username]["flashcard_sets"]

    # Generate a daily challenge when the program starts
    daily_challenge = generate_daily_challenge()

    if "Python (default)" not in flashcard_sets:
        flashcard_sets["Python (default)"] = {
            "category": "Programming",
            "terms": {
                "Python": {"definition": "A high-level programming language.", "correct": 0, "total": 0},
                "Variable": {"definition": "A storage location paired with an associated symbolic name.", "correct": 0, "total": 0},
                "Function": {"definition": "A block of reusable code that performs a specific task.", "correct": 0, "total": 0},
                "Loop": {"definition": "A programming construct that repeats a block of code.", "correct": 0, "total": 0},
            },
            "stats": {"correct": 0, "total": 0, "percentage": 0.0}
        }

    while True:
        user_level = calculate_user_level(flashcard_sets)
        print(f"\nMain Menu (Logged in as: {username} - Level: {user_level}):")
        print("1. Create a new flashcard set")
        print("2. View available flashcard sets")
        print("3. Play with a flashcard set")
        print("4. Edit a flashcard set")
        print("5. Delete a flashcard set")
        print("6. Manage account")
        print("7. View progress")
        print("8. Import/Export flashcard sets")
        print("9. View Daily Challenge")
        print("10. View Leaderboard")
        print("11. Save and Exit")
        choice = input("Enter your choice (1/2/3/4/5/6/7/8/9/10/11): ").strip()

        if choice == "1":
            set_name = input("Enter a name for your new flashcard set: ").strip()
            if set_name in flashcard_sets:
                print(f"A flashcard set named '{set_name}' already exists. Please choose a different name.")
            else:
                category = input("Enter a category for this flashcard set (e.g., Math, Science, History): ").strip()
                flashcard_sets[set_name] = {
                    "category": category,
                    "terms": {},
                    "stats": {"correct": 0, "total": 0, "percentage": 0.0}
                }
                save_user_data(user_data)  # Save after creating a new flashcard set
                print(f"Flashcard set '{set_name}' created successfully under the category '{category}'!")

                while True:
                    term = input("Enter a term (or type 'done' to finish adding terms): ").strip()
                    if term.lower() == "done":
                        print(f"Finished adding terms to '{set_name}'.")
                        break
                    if term in flashcard_sets[set_name]["terms"]:
                        print(f"The term '{term}' already exists. Please enter a different term.")
                    else:
                        definition = input(f"Enter the definition for '{term}': ").strip()
                        flashcard_sets[set_name]["terms"][term] = {"definition": definition, "correct": 0, "total": 0}
                        save_user_data(user_data)  # Save after adding a term
                        print(f"Added: {term} -> {definition}")

        elif choice == "2":
            print("\nView Flashcard Sets:")
            print("1. View all flashcard sets")
            print("2. View flashcard sets by category")
            view_choice = input("Enter your choice (1/2): ").strip()

            if view_choice == "1":
                print("\nAvailable Flashcard Sets:")
                for set_name, flash_cards in flashcard_sets.items():
                    correct = flash_cards["stats"]["correct"]
                    total = flash_cards["stats"]["total"]
                    percentage = flash_cards["stats"]["percentage"]
                    category = flash_cards.get("category", "Uncategorized")
                    print(f"- {set_name} (Category: {category}): {correct}/{total} correct ({percentage:.2f}%)")
                print()

            elif view_choice == "2":
                categories = set(flash_cards.get("category", "Uncategorized") for flash_cards in flashcard_sets.values())
                print("\nAvailable Categories:")
                for category in categories:
                    print(f"- {category}")
                selected_category = input("Enter the category you want to view: ").strip()

                print(f"\nFlashcard Sets in Category '{selected_category}':")
                for set_name, flash_cards in flashcard_sets.items():
                    if flash_cards.get("category", "Uncategorized") == selected_category:
                        correct = flash_cards["stats"]["correct"]
                        total = flash_cards["stats"]["total"]
                        percentage = flash_cards["stats"]["percentage"]
                        print(f"- {set_name}: {correct}/{total} correct ({percentage:.2f}%)")
                print()
            else:
                print("Invalid choice. Returning to the main menu.\n")

        elif choice == "3":
            set_name = input("Enter the name of the flashcard set you want to play with: ").strip()
            if set_name in flashcard_sets:
                score = flash_card_game(flashcard_sets[set_name])  # Capture the score from the game
                daily_challenge = update_daily_challenge(daily_challenge, score)  # Update daily challenge progress
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "4":
            set_name = input("Enter the name of the flashcard set you want to edit: ").strip()
            if set_name in flashcard_sets:
                edit_flashcard_set(flashcard_sets[set_name])
                save_user_data(user_data)  # Save after editing a flashcard set
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "5":
            set_name = input("Enter the name of the flashcard set you want to delete: ").strip()
            if set_name in flashcard_sets:
                if set_name == "Python (default)":
                    print("The default flashcard set cannot be deleted.")
                else:
                    del flashcard_sets[set_name]
                    save_user_data(user_data)  # Save after deleting a flashcard set
                    print(f"Flashcard set '{set_name}' deleted successfully!")
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "6":
            manage_account(username, user_data)

        elif choice == "7":
            print("\nView Progress:")
            print("1. View progress for all flashcard sets")
            print("2. View progress for a specific flashcard set")
            progress_choice = input("Enter your choice (1/2): ").strip()

            if progress_choice == "1":
                print("\nProgress for All Flashcard Sets:")
                for set_name, flash_cards in flashcard_sets.items():
                    print(f"\nFlashcard Set: {set_name}")
                    track_progress(flash_cards)

            elif progress_choice == "2":
                set_name = input("Enter the name of the flashcard set: ").strip()
                if set_name in flashcard_sets:
                    print(f"\nProgress for Flashcard Set: {set_name}")
                    track_progress(flashcard_sets[set_name])
                else:
                    print(f"No flashcard set named '{set_name}' found. Please try again.")
            else:
                print("Invalid choice. Returning to the main menu.\n")

        elif choice == "8":
            manage_flashcard_import_export(flashcard_sets)

        elif choice == "9":
            display_daily_challenge(daily_challenge)  # Display the daily challenge

        elif choice == "10":
            calculate_leaderboard(load_user_data())  # Display the leaderboard

        elif choice == "11":
            set_name = input("Enter the name of the flashcard set you want to search in: ").strip()
            if set_name in flashcard_sets:
                search_flashcard_set(flashcard_sets[set_name])  # Call the search function
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "12":
            set_name = input("Enter the name of the flashcard set you want to review: ").strip()
            if set_name in flashcard_sets:
                revision_mode(flashcard_sets[set_name])  # Call the revision mode function
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")
        elif choice == "13":
            set_name = input("Enter the name of the flashcard set you want to quiz with: ").strip()
            if set_name in flashcard_sets:
                quiz_mode(flashcard_sets[set_name])  # Call the quiz mode function
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")
        elif choice == "14":
            set_name = input("Enter the name of the flashcard set you want to use for Fill in the Blank Mode: ").strip()
            if set_name in flashcard_sets:
                fill_in_the_blank_mode(flashcard_sets[set_name])  # Call the Fill in the Blank Mode function
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")
        elif choice == "15":
            user_data[username]["flashcard_sets"] = flashcard_sets
            save_user_data(user_data)
            print("Your progress has been saved. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a valid option.\n")

    exit()

# Main program
if __name__ == "__main__":
    main_menu()
