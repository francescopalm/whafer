from __future__ import annotations
from datetime import datetime
from whafer.costanti import TIPI_CONTATTI, TIPI_PARTECIPANTI
from whafer.interfacce import Contatto, Gruppo, Messaggio, Chat
import sqlite3

class SorgenteDB():
    msgstore: sqlite3.Connection
    wa: sqlite3.Connection|None

    def __init__(self, msgstore: sqlite3.Connection|str, wa: sqlite3.Connection|str|None = None):
        try:
            self.msgstore = sqlite3.connect(msgstore)
        except TypeError:
            self.msgstore = msgstore

        try:
            self.wa = sqlite3.connect(wa)
        except TypeError:
            self.wa = wa

    """
    @property
    def contatti(self)->list[Contatto]:
        #TODO nome dei contatti
        cursore = self.msgstore.cursor()
        cursore.execute("SELECT _id, user "
                        "FROM jid "
                        f"WHERE type = {TIPI_CONTATTI.get('Contatto')}")
        _id, numeriTelefonici = zip(*cursore.fetchall())
        nomi = numeriTelefonici
        contatti = list(map(ContattoDB, _id, numeriTelefonici, nomi))
        return contatti
    """
    
    @property
    def contatti(self)->list[Contatto]:
        if(self.wa):
            cursore = self.wa.cursor()
            cursore.execute("SELECT _id, number, display_name "
                            "FROM wa_contacts "
                            f"WHERE phone_type = 2")
            _id, numeriTelefonici, nomiVisualizzati = zip(*cursore.fetchall())
        else:
            cursore = self.msgstore.cursor()
            cursore.execute("SELECT _id, user "
                        "FROM jid "
                        f"WHERE type = {TIPI_CONTATTI.get('Contatto')}")
            _id, numeriTelefonici = zip(*cursore.fetchall())
            nomiVisualizzati = numeriTelefonici

        contatti = list(map(ContattoDB, _id, numeriTelefonici, nomiVisualizzati))
        return contatti
    
    @property
    def gruppi(self)->list[Gruppo]:
        cursore = self.msgstore.cursor()
        cursore.execute("SELECT jid._id, jid.user, chat.subject, chat.created_timestamp "
                        "FROM jid "
                        "JOIN chat "
                        "ON jid._id = chat.jid_row_id "
                        f"WHERE jid.type = {TIPI_CONTATTI.get('Gruppo')}")
        _id, numeri, nomi, timestamp= zip(*cursore.fetchall())
        timestamp = [datetime.fromtimestamp(ts/1000) if ts is not None else None for ts in timestamp]
        gruppi = list(map(GruppoDB, _id, numeri, nomi, timestamp))
        for gruppo in gruppi:
            gruppo.msgstore = self.msgstore
        return gruppi
    
    @property
    def gruppi_raw(self)->list:
        cursore = self.msgstore.cursor()
        cursore.execute("SELECT * "
                        "FROM jid "
                        "JOIN chat "
                        "ON jid._id = chat.jid_row_id "
                        f"WHERE jid.type = {TIPI_CONTATTI['Gruppo']}")
        risultati = cursore.fetchall()
        return risultati
    
    @property
    def contatti_raw(self)->list:
        cursore = self.msgstore.cursor()
        cursore.execute("SELECT * "
                        "FROM jid "
                        "JOIN chat "
                        "ON jid._id = chat.jid_row_id "
                        f"WHERE jid.type = {TIPI_CONTATTI['Contatto']}")
        risultati = cursore.fetchall()
        return risultati
    
    @property
    def messaggi_raw(self)->list:
        cursore = self.msgstore.cursor()

        risultati = cursore.fetchall()
        return risultati
    
    @property
    def chat(self)->list[Chat]:
        cursore = self.msgstore.cursor()
        cursore.execute("SELECT chat._id, chat.subject, jid.user "
                        "FROM chat, jid "
                        "WHERE chat.hidden = 0 AND chat.jid_row_id = jid._id")
        _id, soggetto, user = zip(*cursore.fetchall())        
        chat = list(map(ChatDB, _id, soggetto, user))
        for single_chat in chat:
            if single_chat.soggetto == None:
                single_chat.soggetto = single_chat.user
            single_chat.msgstore = self.msgstore
        return chat

class ContattoDB():
    _id: int
    numeroTelefonico: str
    nome: str

    def __init__(self, _id: int, numeroTelefonico: str, nome: str):
        self._id = _id
        self.numeroTelefonico = numeroTelefonico
        self.nome = nome

    @property
    def gruppi(self)->list[Gruppo]:
        pass

    @property
    def messaggi(self)->list[Messaggio]:
        pass

class GruppoDB():
    _id: int
    numeroTelefonico: str
    nome: str
    dataCreazione: datetime
    msgstore: sqlite3.Connection

    def __init__(self, _id: int, numeroTelefonico: str, nome: str, dataCreazione: datetime):
        self._id = _id
        self.numeroTelefonico = numeroTelefonico
        self.nome = nome
        self.dataCreazione = dataCreazione

    @property
    def partecipanti(self)->list[Contatto]:
        cursore = self.msgstore.cursor()
        cursore.execute("SELECT groups._id, groups.user "
                        "FROM group_participant_user "
                        "JOIN jid groups "
                        "ON group_participant_user.user_jid_row_id = groups._id "
                        f"WHERE group_participant_user.rank >= {TIPI_PARTECIPANTI.get('Partecipante')}")
        risultato = cursore.fetchall()
        if risultato:
            _id, numeriTelefonici = zip(*risultato)
            nomi = numeriTelefonici
            partecipanti = list(map(ContattoDB, _id, numeriTelefonici, nomi))
        else:
            partecipanti = []
        return partecipanti

    @property
    def amministratori(self)->list[Contatto]:
        cursore = self.msgstore.cursor()
        cursore.execute("SELECT groups._id, groups.user "
                        "FROM group_participant_user "
                        "JOIN jid groups "
                        "ON group_participant_user.user_jid_row_id = groups._id "
                        f"WHERE group_participant_user.rank > {TIPI_PARTECIPANTI.get('Partecipante')} ")
        risultato = cursore.fetchall()
        if risultato:
            _id, numeriTelefonici = zip(*risultato)
            nomi = numeriTelefonici
            amministratori = list(map(ContattoDB, _id, numeriTelefonici, nomi))
        else:
            amministratori = []
        return amministratori
    
    @property
    def creatore(self)->Contatto:
        cursore = self.msgstore.cursor()
        cursore.execute("SELECT groups._id, groups.user "
                        "FROM group_participant_user "
                        "JOIN jid groups "
                        "ON group_participant_user.user_jid_row_id = groups._id "
                        f"WHERE group_participant_user.rank = {TIPI_PARTECIPANTI.get('Creatore')}")
        risultato = cursore.fetchone()
        _id, numeroTelefonico = risultato if risultato is not None else (None, "Non trovato")
        nome = numeroTelefonico
        creatore = ContattoDB(_id, numeroTelefonico, nome)
        return creatore

    @property
    def messaggi(self)->list[Messaggio]:
        cursore = self.msgstore.cursor()
        cursore.execute("SELECT message._id, message.text_data, message.timestamp, message.received_timestamp, message.receipt_server_timestamp, message.recipient_count, message.status, jid.user, message.from_me "
                        "FROM message "
                        "JOIN chat "
                        "ON message.chat_row_id = chat._id "
                        "LEFT JOIN jid "
                        "ON chat.jid_row_id = jid._id "
                        f"WHERE jid._id = {self._id} AND message_type = 0 ")
        _id, contenuti, dateInvio, dateRicezione, dateRicezioneServer, groupMessage, status, sender, from_me = zip(*cursore.fetchall())
        dateInvio = [datetime.fromtimestamp(ts/1000) if ts is not None else None for ts in dateInvio]
        dateRicezione = [datetime.fromtimestamp(ts/1000) if ts is not None else None for ts in dateRicezione]
        dateRicezioneServer = [datetime.fromtimestamp(ts/1000) if ts is not None and ts > 0 else None for ts in dateRicezioneServer]
        messaggi = list(map(MessaggioDB, _id, contenuti, dateInvio, dateRicezione, dateRicezioneServer, groupMessage, status, sender, from_me))
        return messaggi

class MessaggioDB():
    _id: int
    contenuto: str
    dataInvio: datetime
    dataRicezione: datetime
    dataRicezioneServer: datetime
    groupMessage: bool
    status: int
    sender: str
    from_me: bool
    msgstore: sqlite3.Connection

    def __init__(self, _id: int, contenuto: str, dataInvio: datetime, dataRicezione: datetime, dataRicezioneServer: datetime, groupMessage: bool, status: int, sender: str, from_me: bool):
        self._id = _id
        self.contenuto = contenuto
        self.dataInvio = dataInvio
        self.dataRicezione = dataRicezione
        self.dataRicezioneServer = dataRicezioneServer
        self.groupMessage = groupMessage
        self.status = status
        self.sender = sender
        self.from_me = from_me

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
    

class ChatDB():
    _id: int
    soggetto: str
    user: str
    msgstore: sqlite3.Connection

    def __init__(self, _id: int, soggetto: str, user: str):
        self._id = _id
        self.soggetto = soggetto
        self.user = user

    @property
    def messaggi(self)->list[Messaggio]:
        cursore = self.msgstore.cursor()
        cursore.execute("SELECT message._id, message.text_data, message.timestamp, message.received_timestamp, message.receipt_server_timestamp, message.recipient_count, message.status, jid.user, message.from_me "
                        "FROM message "
                        "JOIN chat "
                        "ON message.chat_row_id = chat._id "
                        "LEFT JOIN jid "
                        "ON message.sender_jid_row_id = jid._id "
                        f"WHERE chat._id = {self._id} AND message_type = 0 ")
        _id, contenuti, dateInvio, dateRicezione, dateRicezioneServer, groupMessage, status, sender, from_me = zip(*cursore.fetchall())
        dateInvio = [datetime.fromtimestamp(ts/1000) if ts is not None else None for ts in dateInvio]
        dateRicezione = [datetime.fromtimestamp(ts/1000) if ts is not None else None for ts in dateRicezione]
        dateRicezioneServer = [datetime.fromtimestamp(ts/1000) if ts is not None and ts > 0 else None for ts in dateRicezioneServer]
        messaggi = list(map(MessaggioDB, _id, contenuti, dateInvio, dateRicezione, dateRicezioneServer, groupMessage, status, sender, from_me))
        for messaggio in messaggi:
            if(messaggio.groupMessage != 0):
                messaggio.groupMessage = True
            else:
                messaggio.groupMessage = False
        return messaggi
