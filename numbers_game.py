import random

def number_guessing_game():
    print("Number Guessing Game!")
    print("You have 7 chances to guess the number between 0 and 99")

    number_to_guess = random.randint(0, 99)
    max_attempts = 7

    for attempt in range(1, max_attempts + 1):
        try:
            guess = int(input(f"Attempt {attempt}: Enter your guess: "))

            if guess == number_to_guess:
                print(f"Congratulations! You guessed the number {number_to_guess} correctly in {attempt} attempt(s).")
                break

            elif guess > number_to_guess:
                print("Your guess is too high.")

            else:
                print("Your guess is too low.")
        
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            continue

        if attempt == max_attempts:
            print(f"Sorry, you've used all your attempts. The correct number was {number_to_guess}. Better luck next time!")

# Start the game
number_guessing_game()
