from dataclasses import dataclass

@dataclass
class Pari:
    id: int
    lanceur_id: int
    adversaire_id: int
    objet: str
    montant: int