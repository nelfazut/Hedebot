import json
import os
from data.models import Pari

class BetManager:
    def __init__(self, filepath="data/paris.json"):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            self._write_raw({"last_id": 0, "active_bets": []})

    def _read_raw(self) -> dict:
        try:
            with open(self.filepath, "r", encoding="utf8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"last_id": 0, "active_bets": []}

    def _write_raw(self, data: dict):
        with open(self.filepath, "w", encoding="utf8") as f:
            json.dump(data, f, indent=4)
    
    def create_bet(self, lanceur_id: int, adversaire_id: int, objet: str, montant: int) -> Pari:
        data = self._read_raw()
        new_id = data["last_id"] + 1
        
        # On crée un dictionnaire simple pour le stockage JSON
        bet_data = {
            "id": new_id,
            "lanceur_id": lanceur_id,
            "adversaire_id": adversaire_id,
            "objet": objet,
            "montant": montant
        }
        
        data["active_bets"].append(bet_data)
        data["last_id"] = new_id
        self._write_raw(data)
        
        return Pari(**bet_data)

    def remove_bet(self, bet_id: int):
        """Supprime un pari par son ID unique, peu importe qui est impliqué."""
        data = self._read_raw()
        data["active_bets"] = [b for b in data["active_bets"] if b["id"] != bet_id]
        self._write_raw(data)


    def get_user_bets(self, user_id: int) -> list[Pari]:
        """Récupère tous les paris d'un utilisateur"""
        data = self._read_raw()
        
        # On filtre les dictionnaires
        bets_dicts = [b for b in data["active_bets"] 
                    if b["lanceur_id"] == user_id or b["adversaire_id"] == user_id]
        
        # On les transforme en instances de la classe Pari
        return [Pari(**b) for b in bets_dicts]

    def get_bet_by_id(self, bet_id: int) -> Pari:
        """Retrouve un pari spécifique par son ID unique et le renvoie en tant qu'objet Pari."""
        data = self._read_raw()
        
        for pari in data["active_bets"]:
            if pari["id"] == bet_id:
                return Pari(**pari)
        return None