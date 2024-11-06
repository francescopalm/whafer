from __future__ import annotations
from typing import Protocol
from dataclasses import dataclass
import sqlite3
from costanti import TIPI_CONTATTI

@dataclass
class Contatto:
    numeroTelefonico: str
    nome: str = ""

@dataclass
class Gruppo:
    numero: str
    nome: str

@dataclass
class Messaggio:
    id: int

class ContattoDBParser:
    def get_contatti(self, msgstore: sqlite3.Connection)->list[Contatto]:
        cursore = msgstore.cursor()
        cursore.execute("SELECT user "
                        "FROM jid "
                        f"WHERE type = {TIPI_CONTATTI.get('Contatto')}")
        numeriTelefonici, = zip(*cursore.fetchall())
        contatti = list(map(Contatto, numeriTelefonici))
        return contatti
    
    def get_contatti_from_gruppo(self, msgstore: sqlite3.Connection, gruppo: Gruppo)->list[Contatto]:
        cursore = msgstore.cursor()
        cursore.execute("SELECT jid.user "
                "FROM jid "
                "JOIN group_participants "
                "ON jid.raw_string = group_participants.jid "
                f"WHERE jid.type = {TIPI_CONTATTI.get('Contatto')} "
                f"AND group_participants.gjid = \"{gruppo.numero+'@g.us'}\"")
        numeriTelefonici, = zip(*cursore.fetchall())
        contatti = list(map(Contatto, numeriTelefonici))
        return contatti
    
class GruppoDBParser:
    def get_gruppi(self, msgstore: sqlite3.Connection)->list[Gruppo]:
        cursore = msgstore.cursor()
        cursore.execute("SELECT jid.user, chat_view.subject "
                        "FROM jid "
                        "JOIN chat_view "
                        "ON jid.raw_string = chat_view.raw_string_jid "
                        f"WHERE jid.type = {TIPI_CONTATTI.get('Gruppo')}")
        numeri, nomi = zip(*cursore.fetchall())        
        gruppi = list(map(Gruppo, numeri, nomi))
        return gruppi
    
    def get_gruppi_from_contatto(self, msgstore: sqlite3.Connection, contatto: Contatto)->list[Gruppo]:
        cursore = msgstore.cursor()
        cursore.execute("SELECT jid.user, chat_view.subject "
                        "FROM jid "
                        "JOIN chat_view "
                        "ON jid.raw_string = chat_view.raw_string_jid "
                        "JOIN group_participants "
                        "ON jid.raw_string = group_participants.gjid "
                        f"WHERE jid.type = {TIPI_CONTATTI.get('Gruppo')} "
                        f"AND group_participants.jid = \"{contatto.numeroTelefonico+'@s.whatsapp.net'}\"")
        numeri, nomi = zip(*cursore.fetchall())        
        gruppi = list(map(Gruppo, numeri, nomi))
        return gruppi
    
class ChatDBParser:
    pass

class Media:
    percorso = str

    def __init__(self, percorso):
        self.percorso = percorso

class Contenuto:
    testo: str
    media: Media

    def __init__(self, testo, media):
        self.testo = testo
        self.media = media

    def get_testo(self):
        return self.testo
    
    def get_media(self):
        return self.media
    
    def add_testo(self, testo):
        self.testo = testo
    
    def add_media(self, media):
        self.media = media
    
class Chat:
    messaggi: list[Messaggio]

    def __init__(self):
        self.messaggi = list()

    def add_messaggio(self, messaggio):
        self.messaggi.append(messaggio)

