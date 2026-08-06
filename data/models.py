from dataclasses import dataclass

@dataclass
class Pari:
    id: int
    lanceur_id: int
    adversaire_id: int
    objet: str
    montant: int
@dataclass
class UserClassement:
    id: int
    nom: str
    color: str
    pr: int