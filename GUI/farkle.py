import random
from collections import Counter

# Function to roll a single die
def roll_die():
    return random.randint(1, 6)

# Function to initialize six dice
def initialize_dice():
    return [roll_die() for _ in range(6)]

# Function to determine the first player
def determine_first_player(players):
    print("\nDetermining who goes first...")
    while True:
        rolls = {player: roll_die() for player in players}
        for player, roll in rolls.items():
            print(f"{player} rolled a {roll}")
        max_roll = max(rolls.values())
        tied_players = [player for player, roll in rolls.items() if roll == max_roll]
        if len(tied_players) == 1:
            print(f"{tied_players[0]} goes first!")
            return tied_players[0]
        else:
            print("It's a tie! Re-rolling for tied players...\n")
            players = tied_players

# Function to display the current game state
def display_state(first_list, second_list):
    print(f"[Banked] {first_list} [Rollable] {second_list}")

# Function to reset all dice to the second list
def reset_dice(first_list, second_list):
    second_list.extend(first_list)
    first_list.clear()

# Parse dice numbers entered by the player
def parse_input(input_string):
    input_string = input_string.replace(",", "").replace(" ", "")
    return [int(char) for char in input_string if char.isdigit()]

# Function to calculate the score from a list of dice
def calculate_score(dice):
    if not dice:
        return 0
    score = 0
    counts = Counter(dice)
    # Straight
    if sorted(counts.keys()) == [1, 2, 3, 4, 5, 6]:
        return 1500
    # Three pairs
    if len(counts) == 3 and all(val == 2 for val in counts.values()):
        return 1500
    for num, count in counts.items():
        if count >= 3:
            if num == 1:
                score += 1000 * (count - 2)
            else:
                score += num * 100 * (count - 2)
            count -= 3
        if num == 1:
            score += count * 100
        elif num == 5:
            score += count * 50
    return score

# Main game logic
def start_game():
    num_players = int(input("Enter the number of players: "))
    players = [input(f"Enter the name of player {i + 1}: ") for i in range(num_players)]
    first_player = determine_first_player(players)
    current_player_index = players.index(first_player)
    player_points = {player: 0 for player in players}

    while True:
        current_player = players[current_player_index]
        print(f"\n{current_player}'s turn!")
        first_list = []
        second_list = initialize_dice()
        display_state(first_list, second_list)

        while True:
            command = input("Enter 'r' to roll, numbers to bank dice, 'turn' to end turn, or 'reset': ").strip()

            if command == "r":
                second_list = [roll_die() for _ in second_list]
                print("------ROLLED------")
            elif command == "reset":
                reset_dice(first_list, second_list)
            elif command == "turn":
                turn_score = calculate_score(first_list)
                if player_points[current_player] == 0 and turn_score < 500:
                    print(f"{current_player} must score at least 500 points to get on the board. You scored {turn_score}.")
                elif turn_score == 0:
                    print("No valid scoring combination in banked dice. You lose this round's points.")
                else:
                    player_points[current_player] += turn_score
                    print(f"{current_player} scored {turn_score} points this turn.")
                    print(f"Total score: {player_points[current_player]}")
                break
            else:
                try:
                    numbers = parse_input(command)
                    for num in numbers:
                        if num in second_list:
                            second_list.remove(num)
                            first_list.append(num)
                except ValueError:
                    print("Invalid input. Please enter 'r', numbers, 'turn', or 'reset'.")

            if len(first_list) == 6:
                print("All six dice are banked. Moving them back to rollable dice.")
                reset_dice(first_list, second_list)

            display_state(first_list, second_list)
            current_bank_score = calculate_score(first_list)
            print(f"Potential bank score: {current_bank_score}")

        # Check for winner
        winner = None
        for player, points in player_points.items():
            if points >= 10000:
                winner = player
                break

        if winner:
            print(f"\n{winner} has reached 10,000 points! Final round begins.")
            print(f"Other players have one turn to try to beat {winner}'s score.")
            for player in players:
                if player != winner:
                    first_list = []
                    second_list = initialize_dice()
                    print(f"\n{player}'s turn in the final round!")
                    display_state(first_list, second_list)
                    while True:
                        command = input("Enter 'r' to roll, numbers to bank dice, 'turn' to end turn, or 'reset': ").strip()

                        if command == "r":
                            second_list = [roll_die() for _ in second_list]
                            print("------ROLLED------")
                        elif command == "reset":
                            reset_dice(first_list, second_list)
                        elif command == "turn":
                            turn_score = calculate_score(first_list)
                            player_points[player] += turn_score
                            print(f"{player} scored {turn_score} this turn.")
                            print(f"Total score: {player_points[player]}")
                            break
                        else:
                            try:
                                numbers = parse_input(command)
                                for num in numbers:
                                    if num in second_list:
                                        second_list.remove(num)
                                        first_list.append(num)
                            except ValueError:
                                print("Invalid input.")

                        if len(first_list) == 6:
                            print("All six dice are banked. Moving them back to rollable dice.")
                            reset_dice(first_list, second_list)

                        display_state(first_list, second_list)
                        print(f"Potential bank score: {calculate_score(first_list)}")

            final_winner = max(player_points, key=player_points.get)
            print(f"\nThe final winner is {final_winner} with {player_points[final_winner]} points!")
            break

        current_player_index = (current_player_index + 1) % num_players

# Start the game
if __name__ == "__main__":
    start_game()
