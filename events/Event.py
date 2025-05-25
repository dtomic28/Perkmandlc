from abc import ABC, abstractmethod

class Event():
    def __init__(self, name: str):
        self.name = name
        self.positions = []

    @abstractmethod
    def start_event(self, game):
        pass

    def __str__(self):
        return f"Event(name={self.name}, description={self.description}, date={self.date})"

    def __repr__(self):
        return self.__str__()