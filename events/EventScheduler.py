import random

class EventScheduler:
    def __init__(self, event_cooldown=120):
        self.possible_events = []
        self.current_events = []
        self.timer = 0
        self.event_cooldown = event_cooldown

    def add_event(self, event):
        self.possible_events.append(event)

    def check_events(self, game):
        self.timer += 1
        if game.difficulty == "Easy" and len(self.current_events) < 1 and self.timer > self.event_cooldown:
            self.start_new_event(game)
        elif game.difficulty == "Medium" and len(self.current_events) < 2 and self.timer > self.event_cooldown:
            self.start_new_event(game)
        elif game.difficulty == "Hard" and len(self.current_events) < 3 and self.timer > self.event_cooldown:
            self.start_new_event(game)

    def start_new_event(self, game):
        self.timer = 0
        if self.possible_events:
            event = random.choice(self.possible_events)
            event.start_event(game)
            self.current_events.append(event)
