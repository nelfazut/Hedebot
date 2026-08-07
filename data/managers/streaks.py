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
        
        user_data = data.get(user_str, [0, 0, 0, 0])
        if len(user_data) == 2:
            user_data.append(0)
        if len(user_data) == 3:
            user_data.append(0)
        
        last_day, streak, best_streak, freezes = user_data
        
        if last_day == current_day:
            return False, False 
        
        # Calcul de la nouvelle streak avec le système de gels
        if last_day == 0:
            new_streak_value = 1
        else:
            missed_days = (current_day - 1) - last_day
            if missed_days > 0:
                if streak > 0 and freezes >= missed_days:
                    freezes -= missed_days
                    new_streak_value = streak + 1  # La streak est sauvée !
                else:
                    new_streak_value = 1  # Streak perdue
            else:
                new_streak_value = streak + 1

        # Vérification si on gagne un gel (au 50ème jour, puis tous les 20 jours)
        freeze_gained = False
        if new_streak_value >= 50 and (new_streak_value - 50) % 20 == 0:
            freezes += 1
            freeze_gained = True

        best_streak = max(best_streak, new_streak_value)
        data[user_str] = [current_day, new_streak_value, best_streak, freezes]
        self._write_streak_data(data)
        
        return True, freeze_gained
    
    def get_user_streak(self, user_id: int) -> int:
        """Lit la streak actuelle en prenant en compte les gels."""
        data = self._get_streak_data()
        user_data = data.get(str(user_id), [0, 0, 0, 0])
        if len(user_data) == 3: user_data.append(0)
        last_day, streak, best_streak, freezes = user_data
        
        if last_day == 0:
            return 0
            
        current_day = get_current_day()
        missed_days = (current_day - 1) - last_day
        
        # Si on a raté des jours, on vérifie si on a assez de gels pour couvrir la période
        if missed_days > 0:
            if freezes >= missed_days:
                return streak
            else:
                return 0
        return streak
        
    def get_user_freezes(self, user_id: int) -> int:
        """Renvoie le nombre de gels disponibles."""
        data = self._get_streak_data()
        user_data = data.get(str(user_id), [0, 0, 0, 0])
        if len(user_data) == 3: user_data.append(0)
        return user_data[3]

    def best_streak(self):
        """renvoie l'id utilisateur associée a la meilleur streak ainsi que sa streak"""
        data = self._get_streak_data()
        if not data:
            return None, 0
        # Correction du bug ici (utilisateurs.items() -> data.items())
        id_max, streak_data = max(data.items(), key=lambda item: item[1][2])
        return int(id_max), streak_data[2]
        
    def get_user_best_streak(self, user : int):
        data = self._get_streak_data()
        user_data = data.get(str(user), [0, 0, 0, 0])
        return user_data[2]

    def get_users_to_remind(self, current_hour: int) -> list[int]:
        """Détermine quels utilisateurs doivent être pingés à cette heure."""
        data = self._get_streak_data()
        current_day = get_current_day()
        to_ping = []

        for user_id_str, user_data in data.items():
            if len(user_data) == 3: user_data.append(0)
            last_day, streak, best_streak, freezes = user_data

            if last_day == 0 or last_day == current_day:
                continue # A déjà joué aujourd'hui ou n'a jamais joué

            missed_days = (current_day - 1) - last_day
            active_streak = streak
            
            # Vérifier si la streak est techniquement active
            if missed_days > 0:
                if freezes >= missed_days:
                    active_streak = streak
                else:
                    active_streak = 0
            
            if active_streak >= 30:
                # 30j = 23h | 45j = 22h | 60j = 21h | 75j = 20h | 90j = 19h | 105j = 18h
                shifts = (active_streak - 30) // 15
                shift_hours = min(5, shifts) # Max 5h de décalage (donc 18h)
                target_hour = 23 - shift_hours
                
                if current_hour == target_hour:
                    to_ping.append(int(user_id_str))

        return to_ping