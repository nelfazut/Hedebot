from discord import Role
import time
def get_user_color(member_roles):
    """
    Determines the hexadecimal color string based on the user's Discord roles.
    This logic was extracted from the original pr command in classement.py.
    
    Args:
        member_roles: A list of discord.Role objects (e.g., user.roles)
        
    Returns:
        str: A hexadecimal color code.
    """
    # Convert role names to lowercase strings for easy checking
    roles = [role.name.lower() for role in member_roles]
    
    if "roster 1" in roles:
        return "#0077d3"
    elif "soldat.e" in roles:
        return "#ff8ff6"
    elif "collaborateur.ice coalisé.e" in roles:
        return "#d60e0e"
    elif "collaborateur.ice ordonné.e" in roles:
        return "#1cb81f"
    else:
        # Default color
        return "#ffb000"

def decouper_liste(liste, n):
        result = []
        for i in range(0, len(liste), n):
            result.append(liste[i:i+n])
        return result   

def get_current_day():
    return int((time.time()+7200)/86400)
