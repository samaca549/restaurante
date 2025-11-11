# presentation/observable.py

class Observable:
    """
    Una clase simple que permite "observar" un valor.
    Cuando el valor cambia, notifica a todos los suscriptores.
    """
    def __init__(self, value=None):
        self._value = value
        self._subs = []

    def subscribe(self, cb):
        """Añade un 'callback' (función) para ser notificado de cambios."""
        self._subs.append(cb)
        if self._value is not None:
            cb(self._value)  # Notifica inmediatamente si ya hay un valor

    @property
    def value(self):
        """Obtiene el valor actual."""
        return self._value

    @value.setter
    def value(self, v):
        """Establece un nuevo valor y notifica a todos los suscriptores."""
        self._value = v
        # Notificamos a una copia de la lista por si un suscriptor
        # intenta desuscribirse durante la notificación.
        for cb in list(self._subs):
            cb(v)