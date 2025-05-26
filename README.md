# Flashcard Program

This is a Python-based flashcard application designed to help users learn and track their progress through interactive flashcard sets. The program includes features for creating, editing, and managing flashcard sets, as well as tracking user performance and achievements.

Note to my teacher Kyle: When I edit a file, it doesn't show, so when you see "2 weeks ago" that just means I uploaded the file 2 weeks ago, but I edit them quite often, so please ignore the dates next to the file, you can view the last commit elsewhere.
## Features

- **User Authentication**: Secure login and account creation with password hashing.
- **Flashcard Management**:
  - Create, edit, and delete flashcard sets.
  - Import and export flashcard sets in JSON or CSV format.
- **Interactive Flashcard Game**:
  - Play with flashcards and receive feedback on your answers.
  - Prioritize terms based on user performance.
- **Progress Tracking**:
  - View detailed progress reports for flashcard sets.
  - Track accuracy and identify terms that need more practice.
- **Daily Challenges**:
  - Set and track daily learning goals.
- **Achievements**:
  - Earn achievements based on milestones and performance.
- **Leaderboard**:
  - Compare your performance with other users.
- **Search Functionality**:
  - Search for terms or definitions within a flashcard set.

## Installation

1. Clone the repository or download the source code.
2. Ensure you have Python 3.x installed on your system.
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: If `requirements.txt` is not provided, ensure the following libraries are installed: `json`, `gzip`, `csv`, `datetime`, `hashlib`, `difflib`, and `msvcrt`.)*

## Usage

1. Run the program:
   ```bash
   python flashcards.py
   ```
2. Log in or create a new account.
3. Use the main menu to navigate through the program:
   - Create or manage flashcard sets.
   - Play the flashcard game.
   - View progress and achievements.
   - Import/export flashcard sets.
   - Manage your account or view the leaderboard.

## File Structure

- **flashcards.py**: The main program file containing all functionality.
- **user_data.json.gz**: A compressed file used to store user data securely.

## Example Flashcard Set

The program includes a default flashcard set for Python programming:
- **Category**: Programming
- **Terms**:
  - Python: A high-level programming language.
  - Variable: A storage location paired with an associated symbolic name.
  - Function: A block of reusable code that performs a specific task.
  - Loop: A programming construct that repeats a block of code.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

Special thanks to the developers and contributors who made this project possible.
