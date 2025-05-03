# Flash-Cards
A flash card website

This is the code:
import random

# Define a dictionary of flash cards (term: definition)
flash_cards = {
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

def flash_card_game():
    print("Welcome to the Flash Card Program!")
    print("You will be shown a term, and you need to guess its definition.")
    print("Type 'exit' to quit the game.\n")

    # Convert the dictionary into a list of terms
    terms = list(flash_cards.keys())

    # Shuffle the terms for randomness
    random.shuffle(terms)

    # Loop through the terms
    for term in terms:
        print(f"Term: {term}")
        user_answer = input("Your definition: ").strip()

        if user_answer.lower() == "exit":
            print("Thanks for playing! Goodbye!")
            break

        # Check if the user's answer matches the correct definition
        correct_answer = flash_cards[term]
        if user_answer.lower() == correct_answer.lower():
            print("Correct!\n")
        else:
            print(f"Incorrect. The correct definition is: {correct_answer}\n")

    print("You've gone through all the flash cards. Great job!")

# Run the game
if __name__ == "__main__":
    flash_card_game()
