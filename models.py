import json
class Player :
    def __init__(self, name) :
        self.name = name
        self.vote = None

    def __str__(self) :
        return f"Name: {self.name} Vote: {self.vote}"
    def vote9(self, card) :
        self.vote = card


class Feature :
    def __init__(self, name,description) :
        self.name = name
        self.description = description
        self.difficulte = None
    def __str__(self) :
        return f"Name: {self.name} description: {self.description}"
    
class PlanningPoker :
    def __init__(self,mode) :
        self.players = []
        self.backlog = []
        self.mode = mode
    def __str__(self) :
        return f"Players: {self.players} Features: {self.mode}"
    def add_player(self, player) :
        self.players.append(player)
    def add_feature(self, feature) :
        self.backlog.append(feature)

    def vote(self, player, feature, card) :
        player.vote = card
        pass
    def validate_unanimity(votes) :
        return len(set(votes)) == 1
    def validate_average(votes) :
        return sum(votes) / len(votes)
    def validate_majority(votes) :
        return max(set(votes), key = votes.count)
    


    def load_backlog(file_path) :
        with open(file_path,'r') as f :
            data = json.load(f)
    def save_backlog(data,file_path) :
        with open(file_path,'w') as f :
            json.dump(data,f)


