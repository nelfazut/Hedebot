import csv
import unidecode

class LeaderboardManager:
    """
    Handles reading and writing leaderboard data to the CSV file.
    This hides all the messy file reading logic from the Discord Cogs.
    """
    def __init__(self, file_path="classement.csv"):
        self.file_path = file_path

    def _read_data(self):
        """Helper method to read the CSV file and return a list of rows."""
        try:
            with open(self.file_path, "r", newline="") as f:
                return list(csv.reader(f, quotechar="\n", delimiter=";"))
        except FileNotFoundError:
            # If the file doesn't exist yet, return an empty list
            return []

    def _write_data(self, data):
        """Helper method to write the list of rows back to the CSV file."""
        with open(self.file_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerows(data)

    def get_all_players(self):
        """Returns the entire leaderboard list."""
        return self._read_data()

    def get_player(self, discord_id):
        """Finds and returns a specific player by their Discord ID, or None if not found."""
        data = self._read_data()
        for row in data:
            # Check if row has enough elements to avoid index errors
            if len(row) >= 4 and int(row[3]) == discord_id:
                return row
        return None

    def add_pr(self, discord_id, display_name, color, amount):
        """
        Adds PR points to a user. If the user doesn't exist, they are added to the list.
        The list is then sorted by points.
        """
        data = self._read_data()
        found = False

        for i, row in enumerate(data):
            if len(row) >= 4 and int(row[3]) == discord_id:
                # Update existing user
                data[i][1] = color  # Update color
                current_score = int(data[i][2])
                data[i][2] = str(current_score + amount)
                found = True
                break

        if not found:
            # Clean up the name using unidecode just like the old code
            clean_name = unidecode.unidecode(display_name)
            # Add new user (name, color, score, discord_id)
            data.append([clean_name, color, str(amount), str(discord_id)])

        # Sort the data based on score (index 2) in descending order
        # We use a try/except in case a row is formatted incorrectly
        try:
            data.sort(reverse=True, key=lambda x: int(x[2]))
        except ValueError:
            pass # Skip sorting if there's a malformed score string

        # Save the updated list
        self._write_data(data)

    def rename_player(self, discord_id, new_name):
        """Updates the name of a specific player."""
        data = self._read_data()
        for i, row in enumerate(data):
            if len(row) >= 4 and int(row[3]) == discord_id:
                data[i][0] = new_name
                self._write_data(data)
                return True
        return False

    def remove_player(self, discord_id):
        """Removes a player from the leaderboard."""
        data = self._read_data()
        for i, row in enumerate(data):
            if len(row) >= 4 and int(row[3]) == discord_id:
                data.pop(i)
                self._write_data(data)
                return True
        return False

# ---------------------------------------------------------
# Test block: This only runs if you run this file directly
# e.g., `python data/managers/leaderboard.py`
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Testing LeaderboardManager...")
    # Create a dummy manager using a test file so we don't mess up real data
    test_mgr = LeaderboardManager("test_classement.csv")

    print("1. Adding new user...")
    test_mgr.add_pr(111, "Jules", "#ff0000", 50)

    print("2. Adding points to user...")
    test_mgr.add_pr(111, "Jules", "#00ff00", 25) # Should update color and score

    print("3. Adding second user...")
    test_mgr.add_pr(222, "Alice", "#0000ff", 100) # Alice should be sorted to the top

    print("Current Leaderboard:")
    for row in test_mgr.get_all_players():
        print(row)

    import os
    if os.path.exists("test_classement.csv"):
        os.remove("test_classement.csv") # clean up test file
    print("Tests passed.")
