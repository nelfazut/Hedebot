import csv
import unidecode
import json
from utils.helpers import get_current_day
from tabulate import tabulate
from data.models import UserClassement

class LeaderboardManager:
    """
    Handles reading and writing leaderboard data to the CSV file.
    This hides all the messy file reading logic from the Discord Cogs.
    """
    def __init__(self, file_path="data/classement.csv", ui_path="data/classement.json"):
        self.file_path = file_path
        self.ui_path = ui_path
    def __repr__(self):
        data = self._read_data()
        data_utile = [[a[0], a[2]] for a in data]
        data_utile.insert(0, ["Joueur", "PRs"])
        return tabulate(data_utile, headers="firstrow", tablefmt="plain")

    def _read_data(self):
        """Helper method to read the CSV file and return a list of rows."""
        try:
            with open(self.file_path, "r", newline="") as f:
                return list(csv.reader(f, delimiter=";"))
        except FileNotFoundError:
            # If the file doesn't exist yet, return an empty list
            return []

    def _write_data(self, data):
        """Helper method to write the list of rows back to the CSV file."""
        with open(self.file_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerows(data)
    
    def get_ui_messages(self):
        """Helper method to read the json file and return a list of messages (IDs)."""
        try:
            with open(self.ui_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # If the file doesn't exist yet, return an empty list
            return []
    def save_ui_messages(self, liste):
        """Méthode pour modifier le json"""
        with open(self.ui_path, "w") as f:
            json.dump(liste, f)
    def get_all_players(self):
        """Returns the entire leaderboard list."""
        data = self._read_data()
        userlist = []
        for row in data:
            userlist.append(UserClassement(id=int(row[3]),nom=row[0],color=row[1],pr=int(row[2])))
        return userlist

    def get_player(self, discord_id):
        """Finds and returns a specific player by their Discord ID, or None if not found."""
        data = self._read_data()
        for row in data:
            # Check if row has enough elements to avoid index errors
            if len(row) >= 4 and int(row[3]) == discord_id:
                return UserClassement(id=int(row[3]),nom=row[0],color=row[1],pr=int(row[2]))
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
    
    def reset(self):
        return self._write_data([])