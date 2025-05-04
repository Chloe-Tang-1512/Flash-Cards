# Flash-Cards
A flash card website

import random
import difflib
import json
import os
import gzip
import hashlib
import msvcrt  # Import for custom password masking with asterisks

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
                password = input_password("Enter a password: ").strip()  # Use custom password input
                hashed_password = hash_password(password)
                user_data[new_username] = {
                    "password": hashed_password,  # Store the hashed password
                    "flashcard_sets": {}  # Initialize an empty dictionary for the user's flashcard sets
                }
                save_user_data(user_data)
                print(f"Account created successfully! Welcome, {new_username}!")
                return new_username, user_data
        elif username in user_data:
            password = input_password("Enter your password: ").strip()  # Use custom password input
            stored_hashed_password = user_data[username]["password"]
            if verify_password(stored_hashed_password, password):
                print(f"Welcome back, {username}!")
                return username, user_data
            else:
                print("Incorrect password. Please try again.")
        else:
            print("Username not found. Please try again or type 'new' to create an account.")

def flash_card_game(flash_cards):
    """Play a flashcard game with shuffled terms and compare user input with correct answers."""
    print("Welcome to the Flash Card Game!")
    print("You will be shown a term, and you need to guess its definition.")
    print("Type 'exit' to quit the game.\n")

    terms = list(flash_cards["terms"].keys())  # Get the terms from the set
    random.shuffle(terms)  # Shuffle the terms for randomness

    # Initialize score
    score = 0
    total_questions = len(terms)

    # Loop through the terms
    for term in terms:
        print(f"Term: {term}")
        user_answer = input("Your definition: ").strip()

        if user_answer.lower() == "exit":
            print("Thanks for playing! Returning to the main menu...\n")
            break  # Exit the game and return to the main menu

        # Check if the user's answer matches the correct definition
        correct_answer = flash_cards["terms"][term]["definition"]
        similarity = difflib.SequenceMatcher(None, user_answer.lower(), correct_answer.lower()).ratio()

        # Update term stats
        flash_cards["terms"][term]["total"] += 1  # Increment total attempts for the term
        flash_cards["stats"]["total"] += 1  # Increment total attempts for the set
        if similarity > 0.7:  # 70% similarity
            print("Correct!\n")
            score += 1  # Increment score for a correct answer
            flash_cards["terms"][term]["correct"] += 1  # Increment correct attempts for the term
            flash_cards["stats"]["correct"] += 1  # Increment correct attempts for the set
        elif similarity > 0.4:  # Between 40% and 70% similarity
            print(f"Almost correct! Here's a hint: {correct_answer[:len(correct_answer)//2]}...\n")
        else:
            print(f"Incorrect. The correct definition is: {correct_answer}\n")

    # Update overall percentage for the set
    if flash_cards["stats"]["total"] > 0:
        flash_cards["stats"]["percentage"] = (flash_cards["stats"]["correct"] / flash_cards["stats"]["total"]) * 100

    # Display the final score
    print(f"You answered {score} out of {total_questions} questions correctly!")
    print("You've gone through all the flash cards. Great job!")

def edit_flashcard_set(flashcard_sets):
    """Edit an existing flashcard set."""
    set_name = input("Enter the name of the flashcard set you want to edit: ").strip()
    if set_name in flashcard_sets:
        flash_cards = flashcard_sets[set_name]
        while True:
            print(f"\nEditing Flashcard Set: {set_name}")
            print("1. Add a new term")
            print("2. Update an existing term")
            print("3. Delete a term")
            print("4. View all terms")
            print("5. Return to the main menu")
            choice = input("Enter your choice (1/2/3/4/5): ").strip()

            if choice == "1":
                term = input("Enter the new term: ").strip()
                if term in flash_cards["terms"]:
                    print(f"The term '{term}' already exists. Use the update option to modify it.")
                else:
                    definition = input(f"Enter the definition for '{term}': ").strip()
                    flash_cards["terms"][term] = {"definition": definition, "correct": 0, "total": 0}
                    print(f"Added: {term} -> {definition}")

            elif choice == "2":
                term = input("Enter the term you want to update: ").strip()
                if term in flash_cards["terms"]:
                    definition = input(f"Enter the new definition for '{term}': ").strip()
                    flash_cards["terms"][term]["definition"] = definition
                    print(f"Updated: {term} -> {definition}")
                else:
                    print(f"The term '{term}' does not exist in the flashcard set.")

            elif choice == "3":
                term = input("Enter the term you want to delete: ").strip()
                if term in flash_cards["terms"]:
                    del flash_cards["terms"][term]
                    print(f"Deleted the term '{term}' from the flashcard set.")
                else:
                    print(f"The term '{term}' does not exist in the flashcard set.")

            elif choice == "4":
                print(f"\nTerms in Flashcard Set: {set_name}")
                for term, data in flash_cards["terms"].items():
                    correct = data["correct"]
                    total = data["total"]
                    percentage = (correct / total * 100) if total > 0 else 0
                    print(f"- {term}: {data['definition']} (Learned: {percentage:.2f}%)")
                print()

            elif choice == "5":
                print("Returning to the main menu...\n")
                break

            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, or 5.\n")
    else:
        print(f"No flashcard set named '{set_name}' found. Please try again.")

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
            # View account details
            flashcard_sets = user_data[username]["flashcard_sets"]
            print(f"\nAccount Details for '{username}':")
            print(f"- Number of flashcard sets: {len(flashcard_sets)}")
            print("- Flashcard sets:")
            for set_name in flashcard_sets:
                print(f"  - {set_name}")
            print()

        elif choice == "2":
            # Edit account details
            print("\nEdit Account Details:")
            print("1. Change username")
            print("2. Change password")
            edit_choice = input("Enter your choice (1/2): ").strip()

            if edit_choice == "1":
                # Change username
                new_username = input("Enter your new username: ").strip()
                if new_username in user_data:
                    print("This username is already taken. Please try again.")
                else:
                    user_data[new_username] = user_data.pop(username)
                    username = new_username
                    save_user_data(user_data)
                    print(f"Your username has been updated to '{new_username}'.")

            elif edit_choice == "2":
                # Change password
                new_password = input_password("Enter your new password: ").strip()
                user_data[username]["password"] = hash_password(new_password)
                save_user_data(user_data)
                print("Your password has been updated successfully.")

            else:
                print("Invalid choice. Please enter 1 or 2.\n")

        elif choice == "3":
            # Delete account
            confirm = input("Are you sure you want to delete your account? This action cannot be undone (yes/no): ").strip().lower()
            if confirm == "yes":
                del user_data[username]
                save_user_data(user_data)
                print("Your account has been deleted. Goodbye!")
                exit()  # Exit the program after account deletion
            else:
                print("Account deletion canceled.")

        elif choice == "4":
            # Return to the main menu
            print("Returning to the main menu...\n")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.\n")

def main_menu():
    """Main menu for the flashcard program."""
    username, user_data = login()  # Log in or create an account
    flashcard_sets = user_data[username]["flashcard_sets"]  # Load the user's flashcard sets

    # Ensure the default set exists for the user
    if "Python (default)" not in flashcard_sets:
        flashcard_sets["Python (default)"] = {
            "terms": {
                "Python": {"definition": "A high-level programming language.", "correct": 0, "total": 0},
                "Variable": {"definition": "A storage location paired with an associated symbolic name.", "correct": 0, "total": 0},
                "Function": {"definition": "A block of reusable code that performs a specific task.", "correct": 0, "total": 0},
                "Loop": {"definition": "A programming construct that repeats a block of code.", "correct": 0, "total": 0},
            },
            "stats": {"correct": 0, "total": 0, "percentage": 0.0}
        }

    while True:  # Main menu loop
        print(f"\nMain Menu (Logged in as: {username}):")
        print("1. Create a new flashcard set")
        print("2. View available flashcard sets")
        print("3. Play with a flashcard set")
        print("4. Edit a flashcard set")
        print("5. Delete a flashcard set")
        print("6. Manage account")
        print("7. Save and Exit")
        choice = input("Enter your choice (1/2/3/4/5/6/7): ").strip()

        if choice == "1":
            set_name = input("Enter a name for your new flashcard set: ").strip()
            if set_name in flashcard_sets:
                print(f"A flashcard set named '{set_name}' already exists. Please choose a different name.")
            else:
                flashcard_sets[set_name] = {
                    "terms": {},
                    "stats": {"correct": 0, "total": 0, "percentage": 0.0}
                }
                print(f"Flashcard set '{set_name}' created successfully!")

        elif choice == "2":
            print("\nAvailable Flashcard Sets:")
            for set_name, flash_cards in flashcard_sets.items():
                correct = flash_cards["stats"]["correct"]
                total = flash_cards["stats"]["total"]
                percentage = flash_cards["stats"]["percentage"]
                print(f"- {set_name}: {correct}/{total} correct ({percentage:.2f}%)")
            print()

        elif choice == "3":
            set_name = input("Enter the name of the flashcard set you want to play with: ").strip()
            if set_name in flashcard_sets:
                flash_card_game(flashcard_sets[set_name])
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "4":
            edit_flashcard_set(flashcard_sets)

        elif choice == "5":
            set_name = input("Enter the name of the flashcard set you want to delete: ").strip()
            if set_name in flashcard_sets:
                if set_name == "Python (default)":
                    print("The default flashcard set cannot be deleted.")
                else:
                    del flashcard_sets[set_name]
                    print(f"Flashcard set '{set_name}' deleted successfully!")
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "6":
            manage_account(username, user_data)  # Call the account management function

        elif choice == "7":
            user_data[username]["flashcard_sets"] = flashcard_sets  # Save the user's flashcard sets
            save_user_data(user_data)  # Save the data to the file
            print("Your progress has been saved. Goodbye!")  # Confirm to the user
            break  # Exit the main menu loop

        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.\n")
    """Main menu for the flashcard program."""
    username, user_data = login()  # Log in or create an account
    flashcard_sets = user_data[username]["flashcard_sets"]  # Load the user's flashcard sets

    # Ensure the default set exists for the user
    if "Python (default)" not in flashcard_sets:
        flashcard_sets["Python (default)"] = {
            "terms": {
                "Python": {"definition": "A high-level programming language.", "correct": 0, "total": 0},
                "Variable": {"definition": "A storage location paired with an associated symbolic name.", "correct": 0, "total": 0},
                "Function": {"definition": "A block of reusable code that performs a specific task.", "correct": 0, "total": 0},
                "Loop": {"definition": "A programming construct that repeats a block of code.", "correct": 0, "total": 0},
            },
            "stats": {"correct": 0, "total": 0, "percentage": 0.0}
        }

    while True:  # Main menu loop
        print(f"\nMain Menu (Logged in as: {username}):")
        print("1. Create a new flashcard set")
        print("2. View available flashcard sets")
        print("3. Play with a flashcard set")
        print("4. Edit a flashcard set")
        print("5. Delete a flashcard set")
        print("6. Manage account")
        print("7. Save and Exit")
        choice = input("Enter your choice (1/2/3/4/5/6/7): ").strip()

        if choice == "1":
            set_name = input("Enter a name for your new flashcard set: ").strip()
            if set_name in flashcard_sets:
                print(f"A flashcard set named '{set_name}' already exists. Please choose a different name.")
            else:
                flashcard_sets[set_name] = {
                    "terms": {},
                    "stats": {"correct": 0, "total": 0, "percentage": 0.0}
                }
                print(f"Flashcard set '{set_name}' created successfully!")

        elif choice == "2":
            print("\nAvailable Flashcard Sets:")
            for set_name, flash_cards in flashcard_sets.items():
                correct = flash_cards["stats"]["correct"]
                total = flash_cards["stats"]["total"]
                percentage = flash_cards["stats"]["percentage"]
                print(f"- {set_name}: {correct}/{total} correct ({percentage:.2f}%)")
            print()

        elif choice == "3":
            set_name = input("Enter the name of the flashcard set you want to play with: ").strip()
            if set_name in flashcard_sets:
                flash_card_game(flashcard_sets[set_name])
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "4":
            edit_flashcard_set(flashcard_sets)

        elif choice == "5":
            set_name = input("Enter the name of the flashcard set you want to delete: ").strip()
            if set_name in flashcard_sets:
                if set_name == "Python (default)":
                    print("The default flashcard set cannot be deleted.")
                else:
                    del flashcard_sets[set_name]
                    print(f"Flashcard set '{set_name}' deleted successfully!")
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "6":
            manage_account(username, user_data)  # Call the account management function

        elif choice == "7":
            user_data[username]["flashcard_sets"] = flashcard_sets  # Save the user's flashcard sets
            save_user_data(user_data)  # Save the data to the file
            print("Your progress has been saved. Goodbye!")  # Confirm to the user
            break  # Exit the main menu loop

        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.\n")
    """Main menu for the flashcard program."""
    username, user_data = login()  # Log in or create an account
    flashcard_sets = user_data[username]["flashcard_sets"]  # Load the user's flashcard sets

    # Ensure the default set exists for the user
    if "Python (default)" not in flashcard_sets:
        flashcard_sets["Python (default)"] = {
            "terms": {
                "Python": {"definition": "A high-level programming language.", "correct": 0, "total": 0},
                "Variable": {"definition": "A storage location paired with an associated symbolic name.", "correct": 0, "total": 0},
                "Function": {"definition": "A block of reusable code that performs a specific task.", "correct": 0, "total": 0},
                "Loop": {"definition": "A programming construct that repeats a block of code.", "correct": 0, "total": 0},
            },
            "stats": {"correct": 0, "total": 0, "percentage": 0.0}
        }

    while True:
        print(f"\nMain Menu (Logged in as: {username}):")
        print("1. Create a new flashcard set")
        print("2. View available flashcard sets")
        print("3. Play with a flashcard set")
        print("4. Edit a flashcard set")
        print("5. Delete a flashcard set")
        print("6. Manage account")
        print("7. Save and Exit")
        choice = input("Enter your choice (1/2/3/4/5/6/7): ").strip()

        if choice == "1":
            set_name = input("Enter a name for your new flashcard set: ").strip()
            if set_name in flashcard_sets:
                print(f"A flashcard set named '{set_name}' already exists. Please choose a different name.")
            else:
                flashcard_sets[set_name] = {
                    "terms": {},
                    "stats": {"correct": 0, "total": 0, "percentage": 0.0}
                }
                print(f"Flashcard set '{set_name}' created successfully!")

                # Ask the user if they want to add terms
                add_terms = input("Would you like to add terms to this set now? (yes/no): ").strip().lower()
                if add_terms == "yes":
                    while True:
                        term = input("Enter a term (or type 'done' to finish): ").strip()
                        if term.lower() == "done":
                            print(f"Finished adding terms to '{set_name}'.")
                            break
                        definition = input(f"Enter the definition for '{term}': ").strip()
                        flashcard_sets[set_name]["terms"][term] = {"definition": definition, "correct": 0, "total": 0}
                        print(f"Added: {term} -> {definition}")

        elif choice == "2":
            print("\nAvailable Flashcard Sets:")
            for set_name, flash_cards in flashcard_sets.items():
                correct = flash_cards["stats"]["correct"]
                total = flash_cards["stats"]["total"]
                percentage = flash_cards["stats"]["percentage"]
                print(f"- {set_name}: {correct}/{total} correct ({percentage:.2f}%)")
            print()

        elif choice == "3":
            set_name = input("Enter the name of the flashcard set you want to play with: ").strip()
            if set_name in flashcard_sets:
                flash_card_game(flashcard_sets[set_name])
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "4":
            edit_flashcard_set(flashcard_sets)

        elif choice == "5":
            set_name = input("Enter the name of the flashcard set you want to delete: ").strip()
            if set_name in flashcard_sets:
                if set_name == "Python (default)":
                    print("The default flashcard set cannot be deleted.")
                else:
                    del flashcard_sets[set_name]
                    print(f"Flashcard set '{set_name}' deleted successfully!")
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "6":
            manage_account(username, user_data)  # Call the account management function

        elif choice == "7":
            user_data[username]["flashcard_sets"] = flashcard_sets  # Save the user's flashcard sets
            save_user_data(user_data)  # Save the data to the file
            print("Your progress has been saved. Goodbye!")
            break  # Exit the main menu loop

        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.\n")
    """Main menu for the flashcard program."""
    username, user_data = login()  # Log in or create an account
    flashcard_sets = user_data[username]["flashcard_sets"]  # Load the user's flashcard sets

    # Ensure the default set exists for the user
    if "Python (default)" not in flashcard_sets:
        flashcard_sets["Python (default)"] = {
            "terms": {
                "Python": {"definition": "A high-level programming language.", "correct": 0, "total": 0},
                "Variable": {"definition": "A storage location paired with an associated symbolic name.", "correct": 0, "total": 0},
                "Function": {"definition": "A block of reusable code that performs a specific task.", "correct": 0, "total": 0},
                "Loop": {"definition": "A programming construct that repeats a block of code.", "correct": 0, "total": 0},
            },
            "stats": {"correct": 0, "total": 0, "percentage": 0.0}
        }

    while True:
        print(f"\nMain Menu (Logged in as: {username}):")
        print("1. Create a new flashcard set")
        print("2. View available flashcard sets")
        print("3. Play with a flashcard set")
        print("4. Edit a flashcard set")
        print("5. Delete a flashcard set")
        print("6. Manage account")
        print("7. Save and Exit")
        choice = input("Enter your choice (1/2/3/4/5/6/7): ").strip()

        if choice == "1":
            set_name = input("Enter a name for your new flashcard set: ").strip()
            if set_name in flashcard_sets:
                print(f"A flashcard set named '{set_name}' already exists. Please choose a different name.")
            else:
                flashcard_sets[set_name] = {
                    "terms": {},
                    "stats": {"correct": 0, "total": 0, "percentage": 0.0}
                }
                print(f"Flashcard set '{set_name}' created successfully!")

        elif choice == "2":
            print("\nAvailable Flashcard Sets:")
            for set_name, flash_cards in flashcard_sets.items():
                correct = flash_cards["stats"]["correct"]
                total = flash_cards["stats"]["total"]
                percentage = flash_cards["stats"]["percentage"]
                print(f"- {set_name}: {correct}/{total} correct ({percentage:.2f}%)")
            print()

        elif choice == "3":
            set_name = input("Enter the name of the flashcard set you want to play with: ").strip()
            if set_name in flashcard_sets:
                flash_card_game(flashcard_sets[set_name])
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "4":
            edit_flashcard_set(flashcard_sets)

        elif choice == "5":
            set_name = input("Enter the name of the flashcard set you want to delete: ").strip()
            if set_name in flashcard_sets:
                if set_name == "Python (default)":
                    print("The default flashcard set cannot be deleted.")
                else:
                    del flashcard_sets[set_name]
                    print(f"Flashcard set '{set_name}' deleted successfully!")
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "6":
            manage_account(username, user_data)  # Call the account management function

        elif choice == "7":
            user_data[username]["flashcard_sets"] = flashcard_sets  # Save the user's flashcard sets
            save_user_data(user_data)
            print("Your progress has been saved. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.\n")
    """Main menu for the flashcard program."""
    username, user_data = login()  # Log in or create an account
    flashcard_sets = user_data[username]["flashcard_sets"]  # Load the user's flashcard sets

    # Ensure the default set exists for the user
    if "Python (default)" not in flashcard_sets:
        flashcard_sets["Python (default)"] = {
            "terms": {
                "Python": {"definition": "A high-level programming language.", "correct": 0, "total": 0},
                "Variable": {"definition": "A storage location paired with an associated symbolic name.", "correct": 0, "total": 0},
                "Function": {"definition": "A block of reusable code that performs a specific task.", "correct": 0, "total": 0},
                "Loop": {"definition": "A programming construct that repeats a block of code.", "correct": 0, "total": 0},
            },
            "stats": {"correct": 0, "total": 0, "percentage": 0.0}
        }

    while True:
        print(f"\nMain Menu (Logged in as: {username}):")
        print("1. Create a new flashcard set")
        print("2. View available flashcard sets")
        print("3. Play with a flashcard set")
        print("4. Edit a flashcard set")
        print("5. Delete a flashcard set")
        print("6. Save and Exit")
        choice = input("Enter your choice (1/2/3/4/5/6): ").strip()

        if choice == "1":
            set_name = input("Enter a name for your new flashcard set: ").strip()
            if set_name in flashcard_sets:
                print(f"A flashcard set named '{set_name}' already exists. Please choose a different name.")
            else:
                flashcard_sets[set_name] = {
                    "terms": {},
                    "stats": {"correct": 0, "total": 0, "percentage": 0.0}
                }
                print(f"Flashcard set '{set_name}' created successfully!")

        elif choice == "2":
            print("\nAvailable Flashcard Sets:")
            for set_name, flash_cards in flashcard_sets.items():
                correct = flash_cards["stats"]["correct"]
                total = flash_cards["stats"]["total"]
                percentage = flash_cards["stats"]["percentage"]
                print(f"- {set_name}: {correct}/{total} correct ({percentage:.2f}%)")
            print()

        elif choice == "3":
            set_name = input("Enter the name of the flashcard set you want to play with: ").strip()
            if set_name in flashcard_sets:
                flash_card_game(flashcard_sets[set_name])
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "4":
            edit_flashcard_set(flashcard_sets)

        elif choice == "5":
            set_name = input("Enter the name of the flashcard set you want to delete: ").strip()
            if set_name in flashcard_sets:
                if set_name == "Python (default)":
                    print("The default flashcard set cannot be deleted.")
                else:
                    del flashcard_sets[set_name]
                    print(f"Flashcard set '{set_name}' deleted successfully!")
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "6":
            user_data[username]["flashcard_sets"] = flashcard_sets  # Save the user's flashcard sets
            save_user_data(user_data)
            print("Your progress has been saved. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.\n")

# Main program
if __name__ == "__main__":
    main_menu()
