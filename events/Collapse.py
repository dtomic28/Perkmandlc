from events.Event import Event

class Collapse(Event):
    def __init__(self):
        super().__init__("Collapse")
        self.size = 1

    def start_event(self, game):
        pass