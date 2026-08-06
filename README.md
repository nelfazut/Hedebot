# Hedebot

# Installation
- clone the repo
- install the dependancies `pip install -r requirements.txt`
- create a config.json file in the repo directory with these informations
```json
{
    "GUILD_ID": <id>,
    "RANKING_CHANNEL": <id>,
    "EXCLUDED_IDS": [<ids>],
    "DEFAULT_COLOR": "#ffb000",
    "UI_CHANNEL_ID": <id>,
    "STREAK_CHANNEL_ID": <id>,
    "STREAK_DAY_PR": [[30,5], [50,15], [100,50], [200,115], [365,220], [500,320], [666, -10000], [667, 10000],[1000,1100], [2000,2300]],
    "BOT_PREFIX": "h!",
    "ARRIVAL_MESSAGE": "<message>",
    "LOGO_LINK" : "<link of your guild logo>",
    "DEFAULT_CHANNEL" : <id>,
    "DEFAULT_ROLE" : <id>,
    "HELP_CHANNEL" : <id>,
    "TOKEN" : "TOKEN",
    "HONEYPOT_CHANNEL" : <id>
}
```
- download the alien encounters font at https://www.dafont.com/fr/alien-encounters.font, and copy it into the main directory as alienfont.ttf
- Create a file named TOKEN.txt where you put your discord bot token
- run main.py
- special thanks to Otomatyk for the dice part (Otomatyk/diceio)
