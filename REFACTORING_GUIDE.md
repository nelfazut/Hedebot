# Step-by-Step Refactoring Guide for Hedebot

If you are a beginner to Python and Object-Oriented Programming (OOP), rewriting an entire bot can seem overwhelming. The key is to take it **one step at a time**, ensuring the bot still works after each small change.

Here is a step-by-step roadmap for you to gradually transform your bot into the new architecture.

---

## Step 1: Create the New Folders
Before writing any code, set up the new folder structure. Keep your existing files where they are for now, but create empty folders alongside them.

**Action:**
Create these new folders in your project directory:
- `core/`
- `cogs/`
- `services/`
- `data/`
- `data/managers/`

---

## Step 2: The Data Access Layer (DAL) - Start with the Leaderboard
Let's abstract away the CSV file for the leaderboard, just like the example.

1. Create a new file: `data/managers/leaderboard.py`.
2. Inside, create the `LeaderboardManager` class. Copy the code from the example given earlier.
3. **Test it:** Before connecting it to Discord, write a small test script at the bottom of the file to see if it works:
   ```python
   # data/managers/leaderboard.py
   if __name__ == "__main__":
       mgr = LeaderboardManager("../../classement.csv") # Adjust path if needed
       mgr.add_pr(12345, "TestUser", "#ffffff", 10)
       print(mgr.get_top_players())
   ```
   Run this file directly (`python data/managers/leaderboard.py`) and check if the CSV updates.

---

## Step 3: Update `classement.py` to Use the Manager
Now, let's plug your new manager into the existing Discord cog.

1. Open your `main.py`. Initialize the `LeaderboardManager` *before* loading the cog:
   ```python
   from data.managers.leaderboard import LeaderboardManager

   # ...
   async def setup_hook(self):
       self.leaderboard_mgr = LeaderboardManager("classement.csv")
       await self.load_extension("classement")
       # ...
   ```
2. Open `classement.py`. Update the `__init__` method to accept the bot instance (which now has `self.bot.leaderboard_mgr`).
3. Find where you open `classement.csv` in the `pr` command. Delete the `with open(...)` lines and replace them with:
   ```python
   self.bot.leaderboard_mgr.add_pr(user.id, pseudo, couleur, nombre)
   ```
4. **Run the bot** and test the `pr` command in Discord. If it works, celebrate! You've successfully separated your data logic.

---

## Step 4: Extract the Dice Logic (Services)
The `des.py` file has a lot of complex regex and math logic mixed with Discord commands.

1. Create a new file: `services/dice_parser.py`.
2. Move all the purely mathematical functions out of `des.py` and into this new file. Functions like `nettoyage`, `analyse_token_regex`, `analyse_commande`, etc., belong here.
3. You can wrap them in a class (e.g., `class DiceService:`) or leave them as standalone functions.
4. Back in `des.py`, import your new service:
   ```python
   from services.dice_parser import analyse_commande
   ```
5. Update your commands to call these imported functions.
6. **Run the bot** and test rolling dice.

---

## Step 5: Move Cogs to the `cogs/` Folder
Now that things are getting cleaner, let's organize the Discord files.

1. Move `classement.py`, `des.py`, `reactionrole.py`, and `utilitaires.py` into the `cogs/` folder.
2. Update `main.py` to look in the new folder. Change `await self.load_extension("classement")` to `await self.load_extension("cogs.classement")`.
3. **Run the bot** to make sure it still finds and loads all commands.

---

## Step 6: Create the Custom Bot Class (Core)
Currently, your bot setup is directly in `main.py`. Let's move it to `core/bot.py`.

1. Create `core/bot.py`.
2. Move the `class ExampleBot(commands.Bot):` definition from `main.py` into `core/bot.py`. Rename it to something better, like `Hedebot`.
3. In `main.py`, you will now just import and run it:
   ```python
   from core.bot import Hedebot

   TOKEN = open("TOKEN.txt").read().strip()
   bot = Hedebot()
   bot.run(TOKEN)
   ```

---

## Step 7: Repeat for Other Data (JSONs)
Apply what you learned in Step 2 to the rest of the bot's data:
- Create `data/managers/streaks.py` to handle reading/writing `streaks.json`.
- Create `data/managers/bets.py` to handle reading/writing `paris.json`.
- Create `data/managers/selfrole.py` to handle reading/writing `selfrole.json`.

Update the respective cogs to use these new managers instead of opening files directly.

---

## Step 8: Refine and Objectify (Advanced)
Once everything is working with managers, you can start making the code even more "Object-Oriented."
- Instead of the `LeaderboardManager` returning lists like `["TestUser", "#ffffff", "10", "12345"]`, make it return custom Objects.
- Create a `data/models.py` file:
  ```python
  class Player:
      def __init__(self, name, color, score, discord_id):
          self.name = name
          self.color = color
          self.score = int(score)
          self.discord_id = int(discord_id)
  ```
- Change the manager to return a list of `Player` objects. Then, in `classement.py`, you can access data easily: `player.name` instead of `ligne[0]`.

## Final Tips
- **Commit often:** If you use Git, make a commit after every step. If something breaks, you can easily go back.
- **Print statements are your friend:** If data isn't moving between files correctly, use `print()` to see what the variables look like.
- **Don't rush:** Do one file, or even one function, at a time. Make sure it works before moving to the next.