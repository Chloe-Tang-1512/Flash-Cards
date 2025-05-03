# Flash-Cards
A flash card website

import random
import difflib

def create_flashcards():
    """Allow the user to manually create a flashcard set."""
    flash_cards = {}
    print("Let's create your flashcard set!")
    print("Enter terms and their definitions. Type 'done' when you're finished.\n")

    while True:
        term = input("Enter a term (or type 'done' to finish): ").strip()
        if term.lower() == "done":
            break
        definition = input(f"Enter the definition for '{term}': ").strip()
        flash_cards[term] = definition
        print(f"Added: {term} -> {definition}\n")

    print("Flashcard set created successfully!\n")
    return flash_cards

def flash_card_game(flash_cards):
    """Main game logic with score-tracking."""
    print("Welcome to the Flash Card Program!")
    print("You will be shown a term, and you need to guess its definition.")
    print("Type 'exit' to quit the game.\n")

    # Convert the dictionary into a list of terms
    terms = list(flash_cards.keys())

    # Shuffle the terms for randomness
    random.shuffle(terms)

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
        correct_answer = flash_cards[term]
        similarity = difflib.SequenceMatcher(None, user_answer.lower(), correct_answer.lower()).ratio()

        if similarity > 0.7:  # 70% similarity
            print("Correct!\n")
            score += 1  # Increment score for a correct answer
        elif similarity > 0.4:  # Between 40% and 70% similarity
            print(f"Almost correct! Here's a hint: {correct_answer[:len(correct_answer)//2]}...\n")
        else:
            print(f"Incorrect. The correct definition is: {correct_answer}\n")

    # Display the final score
    print(f"You answered {score} out of {total_questions} questions correctly!")
    print("You've gone through all the flash cards. Great job!")

def main_menu():
    """Main menu for the flashcard program."""
    # Default flashcard set
    default_flash_cards = {
        "Python": "A high-level programming language.",
        "Variable": "A storage location paired with an associated symbolic name.",
        "Function": "A block of reusable code that performs a specific task.",
        "Loop": "A programming construct that repeats a block of code.",
        "Dictionary": "A data structure that stores key-value pairs.",
        "List": "A collection of ordered items in Python.",
        "Tuple": "An immutable collection of ordered items in Python.",
        "Class": "A blueprint for creating objects in object-oriented programming.",
        "Module": "A file containing Python code that can be imported and reused.",
        "Exception": "An error that occurs during the execution of a program."
    }

    # Dictionary to store multiple flashcard sets
    flashcard_sets = {"Default": default_flash_cards}

    while True:
        print("\nMain Menu:")
        print("1. Create a new flashcard set")
        print("2. View available flashcard sets")
        print("3. Play with a flashcard set")
        print("4. Delete a flashcard set")
        print("5. Exit")
        choice = input("Enter your choice (1/2/3/4/5): ").strip()

        if choice == "1":
            # Create a new flashcard set
            set_name = input("Enter a name for your new flashcard set: ").strip()
            if set_name in flashcard_sets:
                print(f"A flashcard set named '{set_name}' already exists. Please choose a different name.")
            else:
                flashcard_sets[set_name] = create_flashcards()
                print(f"Flashcard set '{set_name}' created successfully!")

        elif choice == "2":
            # View available flashcard sets
            print("\nAvailable Flashcard Sets:")
            for set_name in flashcard_sets:
                print(f"- {set_name}")
            print()

        elif choice == "3":
            # Play with a flashcard set
            set_name = input("Enter the name of the flashcard set you want to play with: ").strip()
            if set_name in flashcard_sets:
                flash_card_game(flashcard_sets[set_name])
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "4":
            # Delete a flashcard set
            set_name = input("Enter the name of the flashcard set you want to delete: ").strip()
            if set_name in flashcard_sets:
                if set_name == "Default":
                    print("The default flashcard set cannot be deleted.")
                else:
                    del flashcard_sets[set_name]
                    print(f"Flashcard set '{set_name}' deleted successfully!")
            else:
                print(f"No flashcard set named '{set_name}' found. Please try again.")

        elif choice == "5":
            # Exit the program
            print("Thank you for using the Flash Card Program! Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.\n")

# Main program
if __name__ == "__main__":
    main_menu()
