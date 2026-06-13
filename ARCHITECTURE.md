# Hedebot Architecture Overhaul

This document outlines a modernized, object-oriented, and logically structured architecture for the Hedebot Discord Bot. The goal is to make the codebase readable, modular, easily upgradable, and maintainable.

## 1. Directory Structure

A clean separation of concerns is crucial. The following directory structure is proposed:

```
hedebot/
├── core/                   # Core functionality, configuration, and base classes
│   ├── __init__.py
│   ├── bot.py              # Custom Bot class extending commands.Bot
│   ├── config.py           # Configuration management (loading TOKEN, paths)
│   └── exceptions.py       # Custom exception definitions
├── cogs/                   # Discord Cog extensions (Commands and Events)
│   ├── __init__.py
│   ├── classement.py       # Leaderboard and PR management commands
│   ├── des.py              # Dice rolling commands
│   ├── reactionrole.py     # Reaction role management
│   └── utilitaires.py      # Utility commands (purge, remind, etc.)
├── services/               # Business logic, decoupled from Discord
│   ├── __init__.py
│   ├── dice_parser.py      # Dice parsing and calculation logic (from des.py/module1.py)
│   └── image_gen.py        # Image generation logic (from creation_image.py)
├── data/                   # Data access layer (DAL) and models
│   ├── __init__.py
│   ├── database.py         # Abstraction for database/file access
│   ├── models.py           # Data classes for User, Bet, Streak, etc.
│   └── managers/           # Specific logic for handling specific data types
│       ├── __init__.py
│       ├── leaderboard.py  # Handles operations on the classement data
│       ├── bets.py         # Handles operations on bets (paris)
│       └── streaks.py      # Handles operations on daily streaks
├── utils/                  # Helper functions and utilities
│   ├── __init__.py
│   └── helpers.py          # General helper functions (e.g., text cleaning)
├── tests/                  # Unit and integration tests
│   ├── __init__.py
│   ├── test_dice.py
│   └── test_leaderboard.py
├── assets/                 # Static assets
│   └── alienfont.ttf
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
└── README.md               # Project documentation
```

## 2. Key Architectural Principles

### 2.1 Separation of Concerns (MVC-like)
- **Controllers (Cogs):** The files in `cogs/` should *only* handle Discord interactions (receiving commands, parsing arguments, sending messages/embeds). They should not contain complex business logic or direct data access.
- **Services (Business Logic):** The `services/` directory contains the core logic of the bot. For example, `dice_parser.py` will take a string (e.g., "2d6+1") and return the result. It knows nothing about Discord contexts.
- **Data Access (Models & DAL):** The `data/` directory handles all file I/O (CSV, JSON) or future database interactions (e.g., SQLite, PostgreSQL). This makes it trivial to upgrade from file-based storage to a real database later.

### 2.2 Object-Oriented Design
- **Custom Bot Class:** The `core/bot.py` will define a `Hedebot` class inheriting from `commands.Bot`. This class will manage its own setup, error handling, and dependency injection (e.g., passing the database connection to cogs).
- **Data Models:** Instead of passing around lists of lists from CSVs, use Python `dataclasses` or standard classes.
  - Example: A `Player` class with attributes `id`, `name`, `color`, `score`.
  - The `LeaderboardManager` will return lists of `Player` objects, which the cog will then use to format the output.
- **Dice Roller Classes:** Create classes for different types of dice logic (e.g., `DiceExpression`, `DiceResult`) to encapsulate the complex parsing currently in `des.py`.

### 2.3 Dependency Injection
Instead of Cogs opening files directly, they should receive a reference to the data managers upon initialization.
```python
class ClassementCog(commands.Cog):
    def __init__(self, bot, leaderboard_manager):
        self.bot = bot
        self.leaderboard_manager = leaderboard_manager
```

## 3. Refactoring Plan

1. **Create the Data Access Layer:** Start by building the `data/` directory. Create classes that read/write to `classement.csv`, `paris.json`, etc. Write tests for these.
2. **Extract Business Logic:** Move the dice rolling logic from `des.py` and `module1.py` into a clean `services/dice_parser.py` module. Write tests for the parser.
3. **Refactor Cogs:** Rewrite the cogs to use the new Services and Data Access Layer. Remove all `open(...)` calls from the cogs.
4. **Error Handling:** Implement a global error handler in the main `bot.py` or a dedicated cog to gracefully handle command errors and logging.
5. **Configuration:** Move hardcoded IDs (e.g., channel IDs, role IDs) into a configuration file or environment variables.

## 4. Example: The "pr" Command (Before vs After)

**Before (Current):**
The command opens the CSV, manually searches for the user, checks roles, modifies a list, sorts it, writes back to the CSV, then calls another function that opens JSONs and generates images.

**After (Proposed):**
```python
# cogs/classement.py
@app_commands.command(name="pr")
@app_commands.checks.has_role("Soldat.e")
async def pr_command(self, interaction: discord.Interaction, user: discord.Member, amount: int):
    # Determine color based on user roles
    color = get_user_color(user.roles)

    # 1. Update data via the DAL
    self.leaderboard_manager.add_pr(user.id, user.display_name, color, amount)

    # 2. Get the updated leaderboard
    top_players = self.leaderboard_manager.get_top_players()

    # 3. Generate the image via the Image Service
    image_file = await self.image_service.generate_leaderboard_image(top_players)

    # 4. Send the result
    await interaction.response.send_message("Leaderboard updated!", file=image_file)
```

## 5. Benefits of this Architecture

- **Testability:** You can test the dice parser or the leaderboard logic without needing a running Discord bot or mocking Discord objects.
- **Maintainability:** Bugs are easier to find. If the database format changes, you only update the `data/` directory; the Cogs remain untouched.
- **Upgradability:** Moving from JSON/CSV files to a SQL database (like PostgreSQL) requires only rewriting the Data Access Layer (`data/database.py` and managers), without touching the command logic in the Cogs.
- **Readability:** Cogs are small, concise, and focused solely on what the user sees and interacts with.
