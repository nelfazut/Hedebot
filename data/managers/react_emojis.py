import json
class ReactionroleManager:
    def __init__(self, path="data/reactionrole.json"):
        self.path = path
    
    def _read_data(self):
        with open(self.path, "r") as f:
            return json.load(f)
    
    def _write_data(self, data):
        with open(self.path, "w") as f:
            json.dump(data, f)
    
    def get_message_info(self, message_id : int):
        data = self._read_data()
        try:
            return data[str(message_id)]
        except KeyError:
            return None

    def add_reaction(self, message_id: int, emojis: list, roles : list ):
        idstr = str(message_id)
        self_roles = self._read_data()
        try:
            self_roles[idstr]
        except KeyError:
            self_roles[idstr] = {}
            self_roles[idstr]["emojis"] = emojis
            self_roles[idstr]["roles"] = roles
        else: 
            self_roles[idstr]["emojis"] += emojis
            self_roles[idstr]["roles"] += roles

        self._write_data(self_roles)