import csv
import unidecode
from utils.helpers import get_current_day
class LeaderboardManager:
    """
    Handles reading and writing leaderboard data to the CSV file.
    This hides all the messy file reading logic from the Discord Cogs.
    """
    def __init__(self, csv_path="classement.csv", json_path = "classement.json", streak_path="streaks.json"):
        self.csv_path = csv_path = json_path
        self.json_path = json_path
        self.streak_path = streak_path      
    #Fichier csv classement

    def _read_data(self):
        """Helper method to read the CSV file and return a list of rows."""
        try:
            with open(self.csv_path, "r", newline="") as f:
                return list(csv.reader(f, delimiter=";"))
        except FileNotFoundError:
            # If the file doesn't exist yet, return an empty list
            return []

    def _write_data(self, data):
        """Helper method to write the list of rows back to the CSV file."""
        with open(self.csv_path, "w", newline="") as f:
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

    def rename_player(self, discord_id : int, new_name : str) -> bool:
        """Updates the name of a specific player."""
        data = self._read_data()
        for i, row in enumerate(data):
            if len(row) >= 4 and int(row[3]) == discord_id:
                data[i][0] = new_name
                self._write_data(data)
                return True
        return False

    def remove_player(self, discord_id : int):
        """Removes a player from the leaderboard."""
        data = self._read_data()
        for i, row in enumerate(data):
            if len(row) >= 4 and int(row[3]) == discord_id:
                data.pop(i)
                self._write_data(data)
                return True
        return False


    #images classement et messages discord
    def get_ui_state(self) -> (int,list[int]):
        """Récupère l'ID du salon et les IDs des messages du classement."""
        try:
            with open(self.json_path, "r", encoding="utf8") as f:
                data = json.load(f)
                return data[0], data[1] # (channel_id, liste_des_messages)
        except (FileNotFoundError, IndexError):
            return None, []
    def get_ui_channel(self) -> int: 
        """recupere l'id du salon du classement"""
        return self.get_ui_state()[0]

    def get_ui_messages(self) -> list[int]:
        """recupere les id des messages du classement"""
        return self.get_ui_state()[1]

    def save_ui_state(self, channel_id : int, message_ids : list[int]):
        """Sauvegarde les IDs pour pouvoir les supprimer plus tard."""
        with open(self.json_path, "w", encoding="utf8") as f:
            json.dump([channel_id, message_ids], f)
    def overwrite_ui_messages(self, messages_id):
        self.save_ui_state(self.get_ui_channel(), messages_id)
    

    #streaks
    def _get_streak_data(self) -> dict:
        """Renvoie le fichier streaks entier"""
        with open(self.streak_path, "r", encoding="utf8") as f:
            data = json.load(f)
        return data


    def _write_streak_data(self, data):
        """Ecrit dans le fichier streaks"""
        with open(self.streak_path, "w", encoding="utf8") as f:
            json.dump(data, f)

    
    def refresh_user_streak(self, user_id : int) -> None:
        if not (str(ctx.author.id) in data) or (data[str(ctx.author.id)][0] != get_current_day() and data[str(ctx.author.id)][0] != get_current_day()-1):
            self.reset_streak(user_id)
        else:
            data = _get_streak_data()
            data[str(user_id)][0] = get_current_day()
            _write_streak_data(data)

    
    def get_user_streak(self, user_id : int) -> None:
        """Renvoie la valeur de la streak de l'utilisateur"""
        data = self._get_streak_data()
        if not (str(ctx.author.id) in data) or (data[str(ctx.author.id)][0] != get_current_day() and data[str(ctx.author.id)][0] != get_current_day()-1):
            self.reset_streak(user_id)
        return self._get_streak_data()[str(user_id)][1]

    def get_user_last_day(self, user_id : int) -> None:
        """Renvoie le dernier jour ou l'utilisateur a joué"""
        return self._get_streak_data()[str(user_id)][0]

    def reset_streak(self, user_id : int) -> None:
        """Reinitialise la streak de l'utilisateur"""
        data = self._get_streak_data()
        data[str(user_id)] = [get_current_day(), 0]
    
    def increase_streak(self, user_id : int) -> None:
        """Actualise la streak"""
        self.refresh_user_streak(user_id)
        data = self._get_streak_data()
        data 
        

    


        
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
    print("Tests passed.")
