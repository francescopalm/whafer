from __future__ import annotations
from typing import Protocol
from datetime import datetime

class Sorgente(Protocol):
    @property
    def contatti(self)->list[Contatto]:
        pass

    @property
    def gruppi(self)->list[Gruppo]:
        pass

    @property
    def gruppi_raw(self)->list:
        pass

    @property
    def contatti_raw(self)->list:
        pass

    @property
    def messaggi_raw(self)->list:
        pass

class Contatto(Protocol):
    _id: int
    numeroTelefonico: str
    nome: str

    @property
    def gruppi(self)->list[Gruppo]:
        pass

    @property
    def messaggi(self)->list[Messaggio]:
        pass

class Gruppo(Protocol):
    _id: int
    numeroTelefonico: str
    nome: str
    dataCreazione: datetime

    @property
    def membri(self)->list[Contatto]:
        pass

    @property
    def amministratori(self)->list[Contatto]:
        pass

    @property
    def creatore(self)->Contatto:
        pass

    @property
    def messaggi(self)->list[Messaggio]:
        pass

class Messaggio(Protocol):
    _id: int
    contenuto: str
    dataInvio: datetime
    dataRicezione: datetime

    @property
    def mittente(self)->Contatto:
        pass

    @property
    def destinatariEffettivi(self)->list[tuple[Contatto, datetime]]:
        pass

    @property
    def lettori(self)->list[tuple[Contatto, datetime]]:
        pass

    @property
    def lettoriMedia(self)->list[tuple[Contatto, datetime]]:
        pass