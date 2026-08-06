import json
from utils.helpers import get_current_day

class StreakMgr:
    def __init__(self, path="data/streaks.json"):
        self.path = path
    
    def _get_streak_data(self) -> dict:
        """Renvoie le fichier streaks entier"""
        with open(self.path, "r", encoding="utf8") as f:
            data = json.load(f)
        return data

    def _write_streak_data(self, data):
        """Ecrit dans le fichier streaks"""
        with open(self.path, "w", encoding="utf8") as f:
            json.dump(data, f, indent=4)

    def trigger_streak(self, user_id: int) -> bool:
        """Met à jour la streak et renvoie True si elle vient d'augmenter."""
        data = self._get_streak_data()
        user_str, current_day = str(user_id), get_current_day()
        
        last_day, streak = data.get(user_str, [0, 0])
        
        # Si c'est aujourd'hui, on coupe court et on renvoie False
        if last_day == current_day:
            return False 
            
        data[user_str] = [current_day, streak + 1 if last_day == current_day - 1 else 1]
        self._write_streak_data(data)
        
        # La streak a été modifiée avec succès, on renvoie True
        return True
    
    def get_user_streak(self, user_id: int) -> int:
        """Lit la streak actuelle (pour la commande !streak) sans tricher."""
        data = self._get_streak_data()
        last_day, streak = data.get(str(user_id), [0, 0])
        
        # Si le joueur n'a pas joué hier ou aujourd'hui, sa streak est à 0 visuellement
        return streak if last_day >= get_current_day() - 1 else 0
