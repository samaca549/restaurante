class Observable:
    def __init__(self, value=None):
        self._value = value
        self._observers = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.notify()

    def subscribe(self, observer):
        if callable(observer):
            self._observers.append(observer)

    def notify(self):
        for observer in self._observers:
            observer(self._value)
