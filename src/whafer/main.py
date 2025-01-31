from itertools import islice
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import PIL
import pandas
import sqlite3
import subprocess
import xml.etree.ElementTree as ET
import os
import shutil
import numpy as np
from reportlab.lib.pagesizes import landscape, A4, A1
from reportlab.platypus import SimpleDocTemplate, Table as ReportLabTable, TableStyle
from reportlab.lib import colors
from pathlib import Path
from datetime import datetime
from time import sleep, strftime, localtime
from pandastable import Table, dialogs
from importlib.resources import files
from whafer.interfacce import Sorgente, Contatto, Gruppo, Messaggio, Chat
from whafer.progetti import Progetto
from whafer.costanti import STATO_MESSAGGIO

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
genericUserImg = PIL.Image.open(files("whafer.assets").joinpath("generic-user-icon.png"))

class TagFrame(ctk.CTkFrame):
    def __init__(self, parent, intestazione: str, descrizione: str, testoPulsante: str, comando: callable):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        #try:
            #self.immagine = ctk.CTkImage(immagine, size=(30,30))
        #except self.immagine == None:
            #self.immagine = ctk.CTkImage(size=(30,30))

        self.intestazione = ctk.CTkLabel(self, text=intestazione, font=ctk.CTkFont(size=20, weight="bold"), anchor="w", compound="left")
        self.descrizione = ctk.CTkLabel(self, text=descrizione, font=ctk.CTkFont(size=16), anchor="w", wraplength=600)
        self.pulsante = ctk.CTkButton(self, text=testoPulsante, command=comando)

        self.intestazione.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.descrizione.grid(row=1, column=0, sticky="w", padx=10, pady=(0,10))
        self.pulsante.grid(row=0, column=1, sticky="ns", padx=10, pady=(25, 0))

class SenderMessageFrame(ctk.CTkFrame):
    def __init__(self, parent, testo: str, dataInvio: datetime, dataRicezioneServer: datetime, stato: int|None):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,4), weight=1)

        self.testo = ctk.CTkLabel(self, text=testo, font=ctk.CTkFont(size=15, weight="bold"), anchor="e", compound="left")
        self.dataInvio = ctk.CTkLabel(self, text="Invio: "+dataInvio.strftime('%d-%m-%Y %H:%M:%S'), font=ctk.CTkFont(size=12), anchor="e", wraplength=600)
        self.dataRicezioneServer = ctk.CTkLabel(self, text="Ricezione Server: "+dataRicezioneServer.strftime('%d-%m-%Y %H:%M:%S'), font=ctk.CTkFont(size=12), anchor="e", wraplength=600)
        self.inviato = STATO_MESSAGGIO.get("Inviato")
        self.consegnato = STATO_MESSAGGIO.get("Consegnato")
        self.letto = STATO_MESSAGGIO.get("Letto")
        match(stato):
            case self.inviato:
                self.stato = ctk.CTkLabel(self, text="Stato: Inviato", font=ctk.CTkFont(size=12), anchor="e", compound="left")
            case self.consegnato:
                self.stato = ctk.CTkLabel(self, text="Stato: Consegnato", font=ctk.CTkFont(size=12), anchor="e", compound="left")
            case self.letto:
                self.stato = ctk.CTkLabel(self, text="Stato: Letto", font=ctk.CTkFont(size=12), anchor="e", compound="left")
                      

        self.testo.grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.dataInvio.grid(row=1, column=0, sticky="e", padx=10)
        self.dataRicezioneServer.grid(row=2, column=0, sticky="e", padx=10)
        self.stato.grid(row=3, column=0, sticky="e", padx=10, pady=(0,10))


class ReceiverMessageFrame(ctk.CTkFrame):
    def __init__(self, parent, testo: str, dataRicezione: datetime):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,2), weight=1)

        self.testo = ctk.CTkLabel(self, text=testo, font=ctk.CTkFont(size=15, weight="bold"), anchor="w", compound="left")
        self.dataRicezione = ctk.CTkLabel(self, text="Ricezione: "+dataRicezione.strftime('%d-%m-%Y %H:%M:%S'), font=ctk.CTkFont(size=12), anchor="w", wraplength=600)

        self.testo.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.dataRicezione.grid(row=2, column=0, sticky="w", padx=10, pady=(0,10))

class ReceiverGroupMessageFrame(ctk.CTkFrame):
    def __init__(self, parent, testo: str, dataRicezione: datetime, sender:str):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,3), weight=1)

        self.testo = ctk.CTkLabel(self, text=testo, font=ctk.CTkFont(size=15, weight="bold"), anchor="w", compound="left")
        self.dataRicezione = ctk.CTkLabel(self, text="Ricezione: "+dataRicezione.strftime('%d-%m-%Y %H:%M:%S'), font=ctk.CTkFont(size=12), anchor="w", wraplength=600)
        self.sender = ctk.CTkLabel(self, text="Inviato da: +"+sender, font=ctk.CTkFont(size=12), anchor="w", wraplength=600)

        self.testo.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.dataRicezione.grid(row=1, column=0, sticky="w", padx=10)
        self.sender.grid(row=2, column=0, sticky="w", padx=10, pady=(0,10))


class BaseView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True, padx=10, pady=10)


class BenvenutoView(BaseView):
    def __init__(self, parent):
        super().__init__(parent)

        self.intestazione = ctk.CTkLabel(self, text="Benvenuto su WhaFeR", font=ctk.CTkFont(size=40, weight="bold"))
        self.descrizione = ctk.CTkLabel(self, text="Usa i pulsanti sulla barra di navigazione laterale per esplorarne le funzionalità")

        self.intestazione.pack(expand=True, anchor="s")
        self.descrizione.pack(expand=True, anchor="n")


class RiepilogoView(BaseView):
    def __init__(self, parent, progetto: Progetto):
        super().__init__(parent)

        self.intestazione = ctk.CTkLabel(self, text="Riepilogo", font=ctk.CTkFont(size=25, weight="bold"))
        self.intestazione.pack(anchor="w", padx=20, pady=20)

        self.progetto = progetto

        if any(file.endswith(".xml") for file in os.listdir(str(self.progetto.percorso / "sorgenti/" ))):
            tree = ET.parse(str(self.progetto.percorso / "sorgenti" / "com.whatsapp_preferences_light.xml"))
            root = tree.getroot()
            for elem in root.iter():  # Itera attraverso tutti gli elementi nel file XML
                if elem.attrib.get('name') == 'registration_jid':  # Verifica l'attributo 'name'
                    self.telefono = ctk.CTkLabel(self, text="Numero di telefono: +"+elem.text, font=ctk.CTkFont(size=14))
                    self.telefono.pack(anchor="w", padx=20)
                if elem.attrib.get('name') == 'perf_device_id':
                    self.deviceID = ctk.CTkLabel(self, text="Device ID: "+elem.text, font=ctk.CTkFont(size=14))
                    self.deviceID.pack(anchor="w", padx=20)
                if elem.attrib.get('name') == 'my_current_status':
                    self.stato = ctk.CTkLabel(self, text="Stato corrente: "+elem.text, font=ctk.CTkFont(size=14))
                    self.stato.pack(anchor="w", padx=20)
                if elem.attrib.get('name') == 'last_login_time':
                    self.ultimoAccesso = ctk.CTkLabel(self, text="Ultimo accesso: "+strftime('%d-%m-%Y %H:%M:%S', localtime(int(elem.get("value"))))+" (Ora locale)", font=ctk.CTkFont(size=14))
                    self.ultimoAccesso.pack(anchor="w", padx=20)
                if elem.attrib.get('name') == 'registration_success_time_ms':
                    self.dataRegistrazione = ctk.CTkLabel(self, text="Data registrazione: "+strftime('%d-%m-%Y %H:%M:%S', localtime(int(elem.get("value"))/1000))+" (Ora locale)", font=ctk.CTkFont(size=14))
                    self.dataRegistrazione.pack(anchor="w", padx=20)
                if elem.attrib.get('name') == 'privacy_online':
                    if (int(elem.get("value"))):
                        self.mostraStatoOnline = ctk.CTkLabel(self, text="Mostra stato Online: No", font=ctk.CTkFont(size=14))
                    else:
                        self.mostraStatoOnline = ctk.CTkLabel(self, text="Mostra stato Online: Si", font=ctk.CTkFont(size=14))
                    self.mostraStatoOnline.pack(anchor="w", padx=20)

            tree = ET.parse(str(self.progetto.percorso / "sorgenti" / "startup_prefs.xml"))
            root = tree.getroot()
            for elem in root.iter():
                if elem.attrib.get('name') == 'push_name':
                    self.username = ctk.CTkLabel(self, text="Username utente: "+elem.text, font=ctk.CTkFont(size=14))
                    self.username.pack(anchor="w", padx=20)
                
                if elem.attrib.get('name') == 'version':
                    self.version = ctk.CTkLabel(self, text="Versione WhatsApp: "+elem.text, font=ctk.CTkFont(size=14))
                    self.version.pack(anchor="w", padx=20)
                    
                if elem.attrib.get('name') == 'profile_photo_full_id':
                    if (int(elem.get("value"))<0):
                        self.fotoProfilo = ctk.CTkLabel(self, text="Immagine del profilo: Non settata", font=ctk.CTkFont(size=14))
                    else:
                        self.fotoProfilo = ctk.CTkLabel(self, text="Immagine del profilo: Presente", font=ctk.CTkFont(size=14))                
                    self.fotoProfilo.pack(anchor="w", padx=20)

        else:
            self.errorLabel = ctk.CTkLabel(self, text="Non sono stati caricati artefatti .xml", font=ctk.CTkFont(size=14))
            self.errorLabel.pack(anchor="w", padx=20, pady=(0,20))

        self.artefattiLabel = ctk.CTkLabel(self, text="Artefatti caricati:", font=ctk.CTkFont(size=14, weight="bold"))
        self.artefattiLabel.pack(anchor="w", padx=20, pady=(30,0))

        cartellaArtefatti = Path(self.progetto.percorso / "sorgenti" )
        elencoArtefatti = ""
        for file in cartellaArtefatti.iterdir():
            if file.is_file() and file.suffix not in(".db-shm", ".db-wal"):
                elencoArtefatti += file.stem+file.suffix+"\n"

        self.elencoArtefatti = ctk.CTkLabel(self, text=elencoArtefatti, font=ctk.CTkFont(size=14, slant="italic"), justify="left")
        self.elencoArtefatti.pack(anchor="w", padx=20)



class GruppiView(BaseView):

    def __init__(self, parent, gruppi: list[Gruppo], contatti: list[Contatto]):
        super().__init__(parent)

        self.gruppi = gruppi
        self.gruppiFiltrati = gruppi
        self.contatti = contatti
        #self.gruppoCorrente = 0
        #self.numGruppi = 5

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.intestazione = ctk.CTkLabel(self, text="Elenco gruppi", font=ctk.CTkFont(size=25, weight="bold"))

        if (len(gruppi) > 0):
            opzioniOrdina = ["Data creazione", "Nome"]
            self.ordinamentoCorrente = ctk.StringVar(self, value=opzioniOrdina[0])
            self.versoOrdinamento = ctk.BooleanVar(self, value=False)

            self.ordinaPer = ctk.CTkFrame(self)
            self.ordinaPer.intestazione = ctk.CTkLabel(self.ordinaPer, text="Ordina per")
            self.ordinaPer.scelta = ctk.CTkOptionMenu(self.ordinaPer, values=opzioniOrdina, variable=self.ordinamentoCorrente, command=self.ordina_gruppi)
            self.ordinaPer.verso = ctk.CTkCheckBox(self.ordinaPer, variable=self.versoOrdinamento, onvalue=True, offvalue=False, text="Decrescente?", command=self.ordina_gruppi)

            self.filtro = ctk.StringVar(self)

            self.filtraPer = ctk.CTkFrame(self)
            self.filtraPer.intestazione = ctk.CTkLabel(self.filtraPer, text="Filtra per")
            self.filtraPer.testo = ctk.CTkEntry(self.filtraPer, placeholder_text="Filtra per nome", textvariable=self.filtro)
            self.filtraPer.pulsante = ctk.CTkButton(self.filtraPer, text="Cerca", command=self.filtra_gruppi)

            self.frameGruppi = ctk.CTkScrollableFrame(self)
            
            self.ordina_gruppi()
            self.mostra_gruppi()

            #self.framePulsanti = ctk.CTkFrame(self)
            #self.frameGruppi.pagIndietro = ctk.CTkButton(self.framePulsanti, text="Pagina precedente", command=self.mostra_pagina_precedente).pack(side="left", anchor="sw", padx=10, pady=10)
            #self.frameGruppi.pagAvanti = ctk.CTkButton(self.framePulsanti, text="Pagina successiva", command=self.mostra_pagina_successiva).pack(side="right", anchor="se", padx=10, pady=10)

            self.ordinaPer.verso.pack(side="right", padx=5, pady=5)
            self.ordinaPer.scelta.pack(side="right", padx=5, pady=5)
            self.ordinaPer.intestazione.pack(side="right", fill="both", padx=5, pady=5)
            
            self.filtraPer.intestazione.pack(side="left", padx=5, pady=5)
            self.filtraPer.testo.pack(side="left", padx=5, pady=5)
            self.filtraPer.pulsante.pack(side="left", padx=5, pady=5)

            self.intestazione.grid(row=0, column=0, columnspan=3, padx=(20,0), pady=(20,0), sticky="w")
            self.ordinaPer.grid(row=1, column=1, padx=10, pady=(10,0), sticky="nsew")
            self.filtraPer.grid(row=1, column=2, padx=10, pady=(10,0), sticky="nsew")
            self.frameGruppi.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
            #self.framePulsanti.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        else:
            self.emptyLabel = ctk.CTkLabel(self, text="Non è presente alcun gruppo WhatsApp", font=ctk.CTkFont(size=14))


    def mostra_vista_gruppo(self, gruppo: Gruppo, contatti: list[Contatto]):
        self.destroy()
        self.master.vista = GruppoView(self.master, gruppo, contatti)
 
    def mostra_gruppi(self):
        for widget in self.frameGruppi.winfo_children():
            widget.destroy()
        for gruppo in self.gruppi:
            gruppoFrame = TagFrame(self.frameGruppi, 
                                               gruppo.nome,
                                               f"Creato in data: {str(gruppo.dataCreazione.strftime('%d-%m-%Y %H:%M:%S'))}",
                                               "Vai al gruppo",
                                               lambda gruppo=gruppo: self.mostra_vista_gruppo(gruppo, self.contatti))
            gruppoFrame.pack(fill="x", padx=10, pady=(10,0))
            ttk.Separator(self.frameGruppi, orient='horizontal').pack(fill="x", padx=10, pady=(10,0))

    def mostra_pagina_successiva(self):
        if self.gruppoCorrente + self.numGruppi <= len(self.gruppiFiltrati):
            self.gruppoCorrente += self.numGruppi
        self.mostra_gruppi()
        
    def mostra_pagina_precedente(self):
        if self.gruppoCorrente - self.numGruppi >= 0:
            self.gruppoCorrente -= self.numGruppi
        self.mostra_gruppi()

    def ordina_gruppi(self, *args):
        opzioni = {
            "Data creazione": lambda gruppo: (gruppo.dataCreazione is None, gruppo.dataCreazione) ,
            "Nome": lambda gruppo: (gruppo.nome is None, gruppo.nome)
        }
        self.gruppiFiltrati.sort(key=opzioni.get(self.ordinamentoCorrente.get()), reverse=self.versoOrdinamento.get())
        self.mostra_gruppi()

    def filtra_gruppi(self):
        gruppiTemp = [gruppo for gruppo in self.gruppi if gruppo.nome is not None]
        self.gruppiFiltrati = [gruppo for gruppo in gruppiTemp if self.filtro.get() in gruppo.nome ]
        self.gruppoCorrente = 0
        self.ordina_gruppi()
        self.mostra_gruppi()

class GruppoView(BaseView):
    def __init__(self, parent, gruppo: Gruppo, contatti: list[Contatto]|None):
        super().__init__(parent)

        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.gruppo = gruppo
        self.contatti = contatti

        gruppoImg = ctk.CTkImage(genericUserImg, size=(100,100))
        self.gruppoImg = ctk.CTkLabel(self, text="", image=gruppoImg, compound="right")
        self.intestazione = ctk.CTkLabel(self, text=gruppo.nome+" ", font=ctk.CTkFont(size=25, weight="bold"))

        self.dataCreazione = ctk.CTkLabel(self, text=f"Creato in data: {str(gruppo.dataCreazione.strftime('%d-%m-%Y %H:%M:%S'))}", justify="left")
        self.creatore = ctk.CTkLabel(self, text=f"Creato da: +{gruppo.creatore.nome}", justify="left")

        self.intestazioneMembri = ctk.CTkLabel(self, text="Membri", font=ctk.CTkFont(size=25, weight="bold"), justify="left")
        self.intestazioneMessaggi = ctk.CTkLabel(self, text="Anteprima Messaggi", font=ctk.CTkFont(size=25, weight="bold"), justify="left")

        self.frameMembri = ctk.CTkScrollableFrame(self)
        self.frameMessaggi = ctk.CTkScrollableFrame(self)

        self.intestazione.grid(row=0, column=0, columnspan=2, sticky="nw", padx=20, pady=(20,0))
        self.gruppoImg.grid(row=0, column=1, columnspan=2, sticky="e", padx=20, pady=(20,0))
        self.dataCreazione.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(10,0))
        self.creatore.grid(row=0, column=0, columnspan=2, sticky="sw", padx=20, pady=(0,20))
        self.intestazioneMembri.grid(row= 3, column=0, padx=10, pady=(20, 0))
        self.intestazioneMessaggi.grid(row= 3, column=1, padx=10, pady=(20, 0))
        self.frameMembri.grid(row= 4, column=0, sticky="nsew", padx=10, pady=10)
        self.frameMessaggi.grid(row= 4, column=1, sticky="nsew", padx=10, pady=10)

        self.mostra_membri()
        self.mostra_messaggi()

    def mostra_membri(self):
        for widget in self.frameMembri.winfo_children():
            widget.destroy()
        self.frameMembri.intestazioneAmministratori = ctk.CTkLabel(self.frameMembri, text="Amministratori", font=ctk.CTkFont(size=20, weight="bold"))
        self.frameMembri.intestazioneAmministratori.pack(fill="x", padx=10, pady=(10,0))
        amministratori = self.gruppo.amministratori
        if amministratori:
            for amministratore in self.gruppo.amministratori:
                if(amministratore.numeroTelefonico == ""):
                    amministratore.numeroTelefonico = "Me stesso"
                else:
                    amministratore.numeroTelefonico = "+"+amministratore.numeroTelefonico
                for contatto in self.contatti:
                    if(amministratore.numeroTelefonico == "+39"+contatto.numeroTelefonico):
                        username = contatto.nome
                        break
                    else:
                        username = "Username N/D"
                membroFrame = TagFrame(self.frameMembri, 
                                                username,
                                                amministratore.numeroTelefonico,
                                                "Vai al contatto",
                                                None)
                membroFrame.pack(fill="x", padx=10, pady=(10,0))
                ttk.Separator(self.frameMembri, orient='horizontal').pack(fill="x", padx=10, pady=(10,0))
        else:
            membroFrame = ctk.CTkLabel(self.frameMembri, text="Non trovati")
            membroFrame.pack(fill="x", padx=10, pady=(10,0))
        self.frameMembri.intestazionePartecipanti = ctk.CTkLabel(self.frameMembri, text="Membri", font=ctk.CTkFont(size=20, weight="bold"))
        self.frameMembri.intestazionePartecipanti.pack(fill="x", padx=10, pady=(10,0))
        partecipanti = self.gruppo.partecipanti
        if partecipanti:
            for partecipante in self.gruppo.partecipanti:
                if(partecipante.numeroTelefonico == ""):
                    partecipante.numeroTelefonico = "Me stesso"
                else:
                    partecipante.numeroTelefonico = "+"+partecipante.numeroTelefonico
                for contatto in self.contatti:
                    if(partecipante.numeroTelefonico == "+39"+contatto.numeroTelefonico):
                        username = contatto.nome
                        break
                    else:
                        username = "Username N/D"
                membroFrame = TagFrame(self.frameMembri, 
                                                username,
                                                partecipante.numeroTelefonico,
                                                "Vai al contatto",
                                                None)
                membroFrame.pack(fill="x", padx=10, pady=(10,0))
                ttk.Separator(self.frameMembri, orient='horizontal').pack(fill="x", padx=10, pady=(10,0))
        else:
            membroFrame = ctk.CTkLabel(self.frameMembri, text="Non trovati")
            membroFrame.pack(fill="x", padx=10, pady=(10,0))

    def mostra_messaggi(self):
        for widget in self.frameMessaggi.winfo_children():
            widget.destroy()
        messaggi = self.gruppo.messaggi
        #TODO Implementare possibilità di visualizzare dettagli relativi ad un messaggio visualizzato in anteprima
        if messaggi:
            for messaggio in messaggi[0:10]:
                messaggioFrame = TagFrame(self.frameMessaggi, 
                                                "Messaggio:",
                                                messaggio.contenuto,
                                                "Vai al messaggio",
                                                None)
                messaggioFrame.pack(fill="x", padx=10, pady=(10,0))
                ttk.Separator(self.frameMessaggi, orient='horizontal').pack(fill="x", padx=10, pady=(10,0))
        else:
            messaggioFrame = ctk.CTkLabel(self.frameMessaggi, )

class ConversazioniView(BaseView):

    def __init__(self, parent, chat: list[Chat], contatti: list[Contatto]):
        super().__init__(parent)

        self.chat = chat

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.frameConversazioni = ctk.CTkScrollableFrame(self)
        self.intestazione = ctk.CTkLabel(self, text="Elenco conversazioni", font=ctk.CTkFont(size=25, weight="bold"))
        self.intestazione.grid(row=0, column=0, columnspan=3, padx=(20,0), pady=(20,0), sticky="w")
        self.frameConversazioni.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        
        
        for chat_s in self.chat:
            for contatto in contatti:
                if chat_s.soggetto == "39"+contatto.numeroTelefonico:
                    chat_s.soggetto = contatto.nome

        self.mostra_conversazioni()

        

    def mostra_conversazioni(self):
        for widget in self.frameConversazioni.winfo_children():
            widget.destroy()
        for chat in self.chat:
            chatFrame = TagFrame(self.frameConversazioni, 
                                               chat.soggetto,
                                               "User: "+chat.user,
                                               "Vai alla conversazione",
                                               lambda chat=chat: self.mostra_vista_conversazione(chat))
            chatFrame.pack(fill="x", padx=10, pady=(10,0))
            ttk.Separator(self.frameConversazioni, orient='horizontal').pack(fill="x", padx=10, pady=(10,0))

    def mostra_vista_conversazione(self, chat: Chat):
        self.destroy()
        self.master.vista = ConversazioneView(self.master, chat)

class ConversazioneView(BaseView):
    def __init__(self, parent, chat: Chat):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        messaggi = chat.messaggi
        self.intestazione = ctk.CTkLabel(self, text="Dettagli conversazione: "+chat.soggetto, font=ctk.CTkFont(size=25, weight="bold"))
        self.frameConversazione = ctk.CTkScrollableFrame(self)
        self.intestazione.grid(row=0, column=0, columnspan=3, padx=(20,0), pady=(20,0), sticky="w")
        self.frameConversazione.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        if messaggi:
            for messaggio in messaggi:
                if(messaggio.from_me):
                    messaggioFrame = SenderMessageFrame(self.frameConversazione, 
                                                    messaggio.contenuto,
                                                    messaggio.dataInvio,
                                                    messaggio.dataRicezioneServer,
                                                    messaggio.status
                                                    )
                else:
                    if(messaggio.groupMessage):
                        messaggioFrame = ReceiverGroupMessageFrame(self.frameConversazione, 
                                                        messaggio.contenuto,
                                                        messaggio.dataRicezione,
                                                        messaggio.sender
                                                        )
                    else:
                        messaggioFrame = ReceiverMessageFrame(self.frameConversazione, 
                                                        messaggio.contenuto,
                                                        messaggio.dataRicezione
                                                        )
                messaggioFrame.pack(fill="x", padx=10, pady=(10,0))
                ttk.Separator(self.frameConversazione, orient='horizontal').pack(fill="x", padx=10, pady=(10,0))
        else:
            pass



class ContattiView(BaseView):

    def __init__(self, parent, contatti: list[Contatto]):
        super().__init__(parent)

        self.contatti = contatti
        self.contattiFiltrati = contatti
        self.contattoCorrente = 0
        self.numContatti = 5

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.intestazione = ctk.CTkLabel(self, text="Elenco contatti", font=ctk.CTkFont(size=25, weight="bold"))

        opzioniOrdina = ["Numero telefonico", "Nome"]
        self.ordinamentoCorrente = ctk.StringVar(self, value=opzioniOrdina[0])
        self.versoOrdinamento = ctk.BooleanVar(self, value=False)

        self.ordinaPer = ctk.CTkFrame(self)
        self.ordinaPer.intestazione = ctk.CTkLabel(self.ordinaPer, text="Ordina per")
        self.ordinaPer.scelta = ctk.CTkOptionMenu(self.ordinaPer, values=opzioniOrdina, variable=self.ordinamentoCorrente, command=self.ordina_contatti)
        self.ordinaPer.verso = ctk.CTkCheckBox(self.ordinaPer, variable=self.versoOrdinamento, onvalue=True, offvalue=False, text="Decrescente?", command=self.ordina_contatti)

        self.filtro = ctk.StringVar(self)

        self.filtraPer = ctk.CTkFrame(self)
        self.filtraPer.intestazione = ctk.CTkLabel(self.filtraPer, text="Filtra per")
        self.filtraPer.testo = ctk.CTkEntry(self.filtraPer, placeholder_text="Filtra per nome", textvariable=self.filtro)
        self.filtraPer.pulsante = ctk.CTkButton(self.filtraPer, text="Cerca", command=self.filtra_contatti)

        self.frameContatti = ctk.CTkScrollableFrame(self)
        
        self.ordina_contatti()
        self.mostra_contatti()

        self.framePulsanti = ctk.CTkFrame(self)
        self.frameContatti.countContatti = ctk.CTkLabel(self.framePulsanti, text="Contatti visualizzati: "+str(self.contattoCorrente+1)+"-"+str(self.numContatti)+"/"+str(len(self.contattiFiltrati)), font=ctk.CTkFont(size=14))
        self.frameContatti.countContatti.pack(side="left", anchor="sw", padx=10, pady=10)
        self.frameContatti.pagAvanti = ctk.CTkButton(self.framePulsanti, text="Pagina successiva", command=self.mostra_pagina_successiva).pack(side="right", anchor="se", padx=10, pady=10)
        self.frameContatti.pagIndietro = ctk.CTkButton(self.framePulsanti, text="Pagina precedente", command=self.mostra_pagina_precedente).pack(side="right", anchor="se", padx=10, pady=10)
        
        self.ordinaPer.verso.pack(side="right", padx=5, pady=5)
        self.ordinaPer.scelta.pack(side="right", padx=5, pady=5)
        self.ordinaPer.intestazione.pack(side="right", fill="both", padx=5, pady=5)
        
        self.filtraPer.intestazione.pack(side="right", padx=5, pady=5)
        self.filtraPer.testo.pack(side="right", padx=5, pady=5)
        self.filtraPer.pulsante.pack(side="right", padx=5, pady=5)

        self.intestazione.grid(row=0, column=0, columnspan=3, padx=(20,0), pady=(20,0), sticky="w")
        self.ordinaPer.grid(row=1, column=1, padx=10, pady=(10,0), sticky="nsew")
        self.filtraPer.grid(row=1, column=2, padx=10, pady=(10,0), sticky="nsew")
        self.frameContatti.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.framePulsanti.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")


    def mostra_vista_contatto(self, contatto: Contatto):
        self.destroy()
        self.master.vista = ContattoView(self.master, contatto)
 
    def mostra_contatti(self):
        for widget in self.frameContatti.winfo_children():
            widget.destroy()
        genericUserImg = PIL.Image.open(files("whafer.assets").joinpath("generic-user-icon.png"))
        for contatto in islice(self.contattiFiltrati, self.contattoCorrente, self.contattoCorrente+self.numContatti):
            self.frameContatti.contatto = TagFrame(self.frameContatti, 
                                               contatto.nome,
                                               f"Numero telefonico: {contatto.numeroTelefonico}",
                                               "Vai al contatto",
                                               lambda contatto=contatto: self.mostra_vista_contatto(contatto))
            self.frameContatti.contatto.pack(fill="x", padx=10, pady=(10,0))
            ttk.Separator(self.frameContatti, orient='horizontal').pack(fill="x", padx=10, pady=(10,0))

    def mostra_pagina_successiva(self):
        if self.contattoCorrente + self.numContatti <= len(self.contattiFiltrati):
            self.contattoCorrente += self.numContatti
            self.mostra_contatti()
            if(self.contattoCorrente+1 >= len(self.contattiFiltrati)):
                self.frameContatti.countContatti.configure(text="Contatti visualizzati: "+str(self.contattoCorrente+1)+"/"+str(len(self.contattiFiltrati)))
            else:
                self.frameContatti.countContatti.configure(text="Contatti visualizzati: "+str(self.contattoCorrente+1)+"-"+str(self.contattoCorrente+self.numContatti)+"/"+str(len(self.contattiFiltrati)))

                
        
    def mostra_pagina_precedente(self):
        if self.contattoCorrente - self.numContatti >= 0:
            self.contattoCorrente -= self.numContatti
            self.mostra_contatti()
            self.frameContatti.countContatti.configure(text="Contatti visualizzati: "+str(self.contattoCorrente+1)+"-"+str(self.contattoCorrente+self.numContatti)+"/"+str(len(self.contattiFiltrati)))


    def ordina_contatti(self, *args):
        opzioni = {
            "Numero telefonico": lambda contatto: (contatto.numeroTelefonico is None, contatto.numeroTelefonico) ,
            "Nome": lambda contatto: (contatto.nome is None, contatto.nome)
        }
        self.contattiFiltrati.sort(key=opzioni.get(self.ordinamentoCorrente.get()), reverse=self.versoOrdinamento.get())
        self.mostra_contatti()
        pass

    def filtra_contatti(self):
        contattiTemp = [contatto for contatto in self.contatti if contatto.nome is not None]
        self.contattiFiltrati = [contatto for contatto in contattiTemp if self.filtro.get() in contatto.nome ]
        self.contattoCorrente = 0
        self.ordina_contatti()
        self.mostra_contatti()
        pass

class ContattoView(BaseView):
    def __init__(self, parent, contatto: Contatto):
        super().__init__(parent)

        gruppoImg = ctk.CTkImage(genericUserImg, size=(100,100))
        self.intestazione = ctk.CTkLabel(self, text="Dettagli contatto: "+contatto.nome, font=ctk.CTkFont(size=25, weight="bold"))

        self.numeroTelefonico = ctk.CTkLabel(self, text=f"Numero telefonico: +{str(contatto.numeroTelefonico)}", justify="left")
        self.immagineProfilo = ctk.CTkLabel(self, text="Immagine profilo:\n", image=gruppoImg, compound="bottom", justify="left")
        self.intestazione.pack(anchor="w", padx=20, pady=20)
        self.numeroTelefonico.pack(anchor="w", padx=20)
        #TODO Implementare visualizzazione immagine profilo contatto
        self.immagineProfilo.pack(anchor="w", padx=20)

class ContenutiView(BaseView):
    def __init__(self, parent, progetto: Progetto):
        super().__init__(parent)
        self.frameOggetti = ctk.CTkFrame(self, fg_color="transparent")
        self.frameOggetti.pack(fill="both", expand=True)

        self.progetto = progetto
        self.db = sqlite3.connect(str(self.progetto.percorso / "sorgenti" / "msgstore.db"))

        self.contatti = pandas.read_sql_query("SELECT * FROM jid LEFT JOIN chat_view ON chat_view.jid_row_id = jid._id WHERE jid.type = 0", self.db)
        self.gruppi = pandas.read_sql_query("SELECT * FROM jid JOIN chat ON chat.jid_row_id = jid._id WHERE jid.type = 1", self.db)
        self.messaggi = pandas.read_sql_query("SELECT * FROM message", self.db)
        self.sqlite_sequence = pandas.read_sql_query("SELECT * FROM sqlite_sequence", self.db)

        
        # Tabella contatti (jid = 0)
        self.intestazioneContatti = ctk.CTkLabel(self.frameOggetti, text="Contatti", font=ctk.CTkFont(size=25, weight="bold"), justify="left")
        self.intestazioneContatti.pack(anchor="w", padx=20, pady=(20,5))
        self.contattiLabel = ctk.CTkLabel(self.frameOggetti, text="Questa tabella contiene i risultati ottenuti da una join delle tabelle 'jid' e 'chat_view'.\nFai riferimento alla documentazione di WhaFeR per i dettagli.", font=ctk.CTkFont(size=14), justify="left")
        self.contattiLabel.pack(anchor="w", padx=20)
        self.gruppoPulsantiContatti = ctk.CTkFrame(self.frameOggetti, fg_color="transparent")
        self.pulsanteContattiEsporta = ctk.CTkButton(self.gruppoPulsantiContatti, text="Esporta Tabella Contatti (CSV)", command=self.reporta_contatti_csv).pack(side="right", anchor="se")
        self.pulsanteContattiEsporta = ctk.CTkButton(self.gruppoPulsantiContatti, text="Esporta Tabella Contatti (PDF)", command=self.reporta_contatti).pack(side="right", anchor="se", padx=10)
        self.pulsanteContattiAnalisi = ctk.CTkButton(self.gruppoPulsantiContatti, text="Analisi Tabella Contatti", command=lambda: self.analisi_tabella(self.contatti)).pack(side="left", anchor="se")
        self.gruppoPulsantiContatti.pack(anchor="w", padx=20, pady=(10,0))

        # Tabella gruppi (jid = 1)
        self.intestazioneGruppi = ctk.CTkLabel(self.frameOggetti, text="Gruppi", font=ctk.CTkFont(size=25, weight="bold"), justify="left")
        self.intestazioneGruppi.pack(anchor="w", padx=20, pady=(20,5))
        self.gruppiLabel = ctk.CTkLabel(self.frameOggetti, text="Questa tabella contiene i risultati ottenuti da una join delle tabelle 'jid' e 'chat', selezionando solo le righe riferite ai gruppi (type=1).\nFai riferimento alla documentazione di WhaFeR per i dettagli.", font=ctk.CTkFont(size=14), justify="left")
        self.gruppiLabel.pack(anchor="w", padx=20)
        self.gruppoPulsantiGruppi = ctk.CTkFrame(self.frameOggetti, fg_color="transparent")
        self.pulsanteGruppiEsporta = ctk.CTkButton(self.gruppoPulsantiGruppi, text="Esporta Tabella Gruppi (CSV)", command=self.reporta_gruppi_csv).pack(side="right", anchor="se")
        self.pulsanteGruppiEsporta = ctk.CTkButton(self.gruppoPulsantiGruppi, text="Esporta Tabella Gruppi (PDF)", command=self.reporta_gruppi).pack(side="right", anchor="se", padx=10)
        self.pulsanteGruppiAnalisi = ctk.CTkButton(self.gruppoPulsantiGruppi, text="Analisi Tabella Gruppi", command=lambda: self.analisi_tabella(self.gruppi)).pack(side="left", anchor="se")
        self.gruppoPulsantiGruppi.pack(anchor="w", padx=20, pady=(10,0))

        # Tabella messaggi (message)
        self.intestazioneMessaggi = ctk.CTkLabel(self.frameOggetti, text="Messaggi", font=ctk.CTkFont(size=25, weight="bold"), justify="left")
        self.intestazioneMessaggi.pack(anchor="w", padx=20, pady=(20,5))
        self.messaggiLabel = ctk.CTkLabel(self.frameOggetti, text="Questa tabella contiene i risultati ottenuti da una query sulla tabella 'message'.\nFai riferimento alla documentazione di WhaFeR per i dettagli.", font=ctk.CTkFont(size=14), justify="left")
        self.messaggiLabel.pack(anchor="w", padx=20)
        self.gruppoPulsantiMessaggi = ctk.CTkFrame(self.frameOggetti, fg_color="transparent")
        self.pulsanteMessaggiEsporta = ctk.CTkButton(self.gruppoPulsantiMessaggi, text="Esporta Tabella message (CSV)", command=self.reporta_messaggi_csv).pack(side="right", anchor="se")
        self.pulsanteMessaggiEsporta = ctk.CTkButton(self.gruppoPulsantiMessaggi, text="Esporta Tabella message (PDF)", command=self.reporta_messaggi).pack(side="right", anchor="se", padx=10)
        self.pulsanteMessaggiAnalisi = ctk.CTkButton(self.gruppoPulsantiMessaggi, text="Analisi Tabella message", command=lambda: self.analisi_tabella(self.messaggi)).pack(side="left", anchor="se")
        self.gruppoPulsantiMessaggi.pack(anchor="w", padx=20, pady=(10,0))


        # Tabella sqlite_sequence
        self.intestazioneSqlite = ctk.CTkLabel(self.frameOggetti, text="sqlite_sequence", font=ctk.CTkFont(size=25, weight="bold"), justify="left")
        self.intestazioneSqlite.pack(anchor="w", padx=20, pady=(20,5))
        self.sqliteLabel = ctk.CTkLabel(self.frameOggetti, text="Questa tabella contiene i risultati ottenuti da una query sulla tabella 'sqlite_sequence'.\nFai riferimento alla documentazione di WhaFeR per i dettagli.", font=ctk.CTkFont(size=14), justify="left")
        self.sqliteLabel.pack(anchor="w", padx=20)
        self.gruppoPulsantiSqlite = ctk.CTkFrame(self.frameOggetti, fg_color="transparent")
        self.pulsanteSqliteEsporta = ctk.CTkButton(self.gruppoPulsantiSqlite, text="Esporta Tabella sqlite_sequence (CSV)", command=self.reporta_sqlite_sequence_csv).pack(side="right", anchor="se")
        self.pulsanteSqliteEsporta = ctk.CTkButton(self.gruppoPulsantiSqlite, text="Esporta Tabella sqlite_sequence (PDF)", command=self.reporta_sqlite_sequence).pack(side="right", anchor="se", padx=10)
        self.pulsanteSqliteAnalisi = ctk.CTkButton(self.gruppoPulsantiSqlite, text="Analisi Tabella sqlite_sequence", command=lambda: self.analisi_tabella(self.sqlite_sequence)).pack(side="left", anchor="se")
        self.gruppoPulsantiSqlite.pack(anchor="w", padx=20, pady=(10,0))

    def filtra_contatti(self):
        pass

    def filtra_gruppi(self):
        pass

    def filtra_messaggi(self):
        pass

    def reporta_contatti(self):
        percorso = Path(self.progetto.percorso / "reports" / f"contatti_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.pdf")
        self.genera_report(percorso, self.contatti)

    def reporta_contatti_csv(self):
        percorso = Path(self.progetto.percorso / "reports" / f"contatti_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv")
        self.genera_report_csv(percorso, self.contatti)

    def reporta_gruppi(self):
        percorso = Path(self.progetto.percorso / "reports" / f"gruppi_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.pdf")
        self.genera_report(percorso, self.gruppi)

    def reporta_gruppi_csv(self):
        percorso = Path(self.progetto.percorso / "reports" / f"gruppi_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv")
        self.genera_report_csv(percorso, self.gruppi)

    def reporta_messaggi(self): 
        percorso = Path(self.progetto.percorso / "reports" / f"messaggi_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.pdf")
        self.genera_report(percorso, self.messaggi)

    def reporta_messaggi_csv(self):
        percorso = Path(self.progetto.percorso / "reports" / f"messaggi_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv")
        self.genera_report_csv(percorso, self.messaggi)

    def reporta_sqlite_sequence(self):
        percorso = (self.progetto.percorso / "reports" / f"sqlite_sequence_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.pdf")
        self.genera_report(percorso, self.sqlite_sequence)

    def reporta_sqlite_sequence_csv(self):
        percorso = (self.progetto.percorso / "reports" / f"sqlite_sequence_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv")
        self.genera_report_csv(percorso, self.sqlite_sequence)

    def apri_popup_successo(self, percorso):
        self.successPopup = ctk.CTkToplevel()
        self.successPopup.geometry("600x150")
        self.successPopup.title("Esportazione effettuata")
        self.successLabel = ctk.CTkLabel(self.successPopup, text="Esportazione effettuata con successo in:\n"+str(percorso), font=ctk.CTkFont(size=14)).pack(pady=20)
        chiudi_btn = ctk.CTkButton(self.successPopup, text="CHIUDI", command=self.successPopup.destroy)
        chiudi_btn.pack(pady=10, padx=10)
        self.successPopup.attributes("-topmost",True)

    def analisi_tabella(self, tabella):
        self.popup = ctk.CTkToplevel()
        self.popup.geometry("900x400")
        self.popup.title("Dettaglio tabella")
        self.popup.attributes("-topmost",True)
        self.frameContatti = ctk.CTkFrame(self.popup)
        self.tabella = Table(self.frameContatti, dataframe=tabella)
        self.frameContatti.pack(expand=True, fill="both", padx=10, pady=10)
        self.tabella.show()
        self.tabella.redraw()


    def genera_report(self, percorso, dataframe):

        if (int(len(dataframe.columns)) > 45):
            custom_pagesize = (7000,3000)
        elif (int(len(dataframe.columns)) > 10):
            custom_pagesize = landscape(A1)
        elif (int(len(dataframe.columns)) > 5):
            custom_pagesize = landscape(A4)
        else:
            custom_pagesize = A4

        # Crea il documento PDF
        pdf = SimpleDocTemplate(str(percorso), pagesize=custom_pagesize, leftMargin=10, rightMargin=10)
        elements = []

        # Converte il DataFrame in una lista di liste
        data = [dataframe.columns.to_list()] + dataframe.values.tolist()

        # Crea una tabella
        table = ReportLabTable(data)

        # Applica uno stile alla tabella
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Sfondo grigio per l'intestazione
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Testo bianco per l'intestazione
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Allinea il testo al centro
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Font grassetto per l'intestazione
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding per l'intestazione
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Sfondo beige per le celle
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Aggiunge una griglia
        ])
        table.setStyle(style)

        # Aggiungi la tabella agli elementi del PDF
        elements.append(table)

        # Costruisce il PDF
        pdf.build(elements)
        print(f"Report PDF generato con successo")
        self.apri_popup_successo(str(percorso))


    def genera_report_csv(self, percorso, dataframe):
        with open(percorso, mode="wb") as file:
            dataframe.to_csv(file, index=False, sep=";")
            self.apri_popup_successo(percorso)


class MediaView(BaseView):
    def __init__(self, parent, progetto : Progetto):
        super().__init__(parent)

        self.progetto = progetto

        self.intestazione = ctk.CTkLabel(self, text="File Media", font=ctk.CTkFont(size=25, weight="bold"))
        self.intestazione.pack(anchor="w", padx=20, pady=20)

        self.descrizione = ctk.CTkLabel(self, justify="left", text="Questa funzionalità permette di estrarre e analizzare i file media WhatsApp presenti nel dispositivo.\n\n" \
                                        "1. Assicurati che nelle impostazioni dello smartphone sia attivo il Debug USB.\n(Per farlo, approfondisci sulla documentazione di WhaFeR)\n" \
                                        "2. Sblocca lo smartphone e collegalo attraverso USB al PC\n" \
                                        "3. Se richiesto, conferma sullo smartphone il debug USB\n" \
                                        "4. Clicca su 'Estrai file media' in questa finestra\n" \
                                        "5. Attendere il completamento dell'operazione\n\n" \
                                        "In caso di errori, fare riferimento alla documentazione di WhaFeR.\n" \
                                        "Talvolta può essere risolutivo scollegare e ricollegare nuovamente il cavo USB al pc, assicurandosi\ndi compiere questa operazione con smartphone sbloccato." \
                                            , font=ctk.CTkFont(size=14))
        self.descrizione.pack(anchor="w", padx=20)

        self.gruppoPulsantiMedia = ctk.CTkFrame(self, fg_color="transparent")
        self.estraiMedia = ctk.CTkButton(self.gruppoPulsantiMedia, text="Estrai file media", command=self.estrai_media).pack(side="left")
        self.apriMedia = ctk.CTkButton(self.gruppoPulsantiMedia, text="Apri cartella media estratti", command=self.apri_media)
        self.apriMedia.pack(side="right", padx=10)
        self.gruppoPulsantiMedia.pack(anchor="w", padx=20, pady=20)
        self.errorLabel = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.errorLabel.pack(anchor="w", padx=20, pady=30)

        if len(os.listdir(str(self.progetto.percorso / "media"))) == 0:
            self.apriMedia.configure(state="disabled", fg_color="darkgrey")

        

    def estrai_media(self):
        try:
            proc1 = subprocess.Popen('adb shell', stdin = subprocess.PIPE, stdout=subprocess.PIPE, stderr=None)
            out, err = proc1.communicate(b'getprop ro.build.version.sdk\nexit') # Controllo API level Android
            proc1.terminate()
            print(int(out.decode("utf-8")))
            if(int(out.decode("utf-8")) <= 30):
                proc1 = subprocess.Popen('adb pull -a /sdcard/WhatsApp/Media/. '+str(self.progetto.percorso / "media"))
                proc1.wait()
            else:
                proc1 = subprocess.Popen('adb pull -a /sdcard/Android/media/com.whatsapp/WhatsApp/Media/. '+str(self.progetto.percorso / "media"))
                proc1.wait()
            proc1.terminate()
            self.apriMedia.configure(state="normal", fg_color="#1F6AA5")
            
            # Popup di successo
            self.successPopup = ctk.CTkToplevel()
            self.successPopup.geometry("600x150")
            self.successPopup.title("Estrazione effettuata")
            self.successLabel = ctk.CTkLabel(self.successPopup, text="Estrazione effettuata con successo in:\n"+str(self.progetto.percorso / "media"), font=ctk.CTkFont(size=14)).pack(pady=20)
            chiudi_btn = ctk.CTkButton(self.successPopup, text="CHIUDI", command=self.successPopup.destroy)
            chiudi_btn.pack(pady=10, padx=10)
            self.successPopup.attributes("-topmost",True)

        except Exception as e:
            print("Si è verificato un errore:", str(e))
            self.errorLabel.configure(text="Errore. Controlla la console per il log.")



    def apri_media(self):
        path = str(self.progetto.percorso / "media")
        path = os.path.realpath(path)
        os.startfile(path)




class Applicazione(ctk.CTkFrame):
    def __init__(self, parent, progetto: Progetto):
        super().__init__(parent)
        self.pack(expand=True, fill="both")

        self.progetto = progetto

        self.navbar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.navbar.pack(side="left", fill="both", ipadx=10)

        self.intestazione = ctk.CTkLabel(self.navbar, text="WhaFeR", font=ctk.CTkFont(size=20, weight="bold"), width=200, pady=30)
        self.pulsanteRiepilogo = ctk.CTkButton(self.navbar, text="Riepilogo", command=self.mostra_vista_riepilogo, anchor="w", fg_color="transparent", corner_radius=0, border_spacing=20)
        self.pulsanteGruppo = ctk.CTkButton(self.navbar, text="Gruppi", command=self.mostra_vista_gruppi, anchor="w", fg_color="transparent", corner_radius=0, border_spacing=20)
        self.pulsanteConversazioni = ctk.CTkButton(self.navbar, text="Conversazioni", command=self.mostra_vista_conversazioni, anchor="w", fg_color="transparent", corner_radius=0, border_spacing=20)        
        self.pulsanteContatto = ctk.CTkButton(self.navbar, text="Contatti", command=self.mostra_vista_contatti, anchor="w", fg_color="transparent", corner_radius=0, border_spacing=20)
        self.pulsanteMedia = ctk.CTkButton(self.navbar, text="Media", command=self.mostra_vista_media, anchor="w", fg_color="transparent", corner_radius=0, border_spacing=20)
        self.pulsanteContenuti = ctk.CTkButton(self.navbar, text="Analisi tabelle DB", command=self.mostra_vista_contenuti, anchor="w", fg_color="transparent", corner_radius=0, border_spacing=20)
        self.pulsanteImpostazioni = ctk.CTkButton(self.navbar, state="disabled", text="Impostazioni", anchor="w", fg_color="transparent", corner_radius=0, border_spacing=20)

        self.vista = BenvenutoView(self)

        self.intestazione.pack(fill="x", pady=5)
        self.pulsanteRiepilogo.pack(fill="x")
        self.pulsanteGruppo.pack(fill="x")
        self.pulsanteConversazioni.pack(fill="x")
        self.pulsanteContatto.pack(fill="x")
        self.pulsanteMedia.pack(fill="x")
        self.pulsanteContenuti.pack(fill="x")
        self.pulsanteImpostazioni.pack(fill="x")

    def mostra_vista_riepilogo(self):
        self.pulsanteRiepilogo.configure(fg_color="#1F6AA5", hover=False)
        self.pulsanteGruppo.configure(fg_color="transparent", hover=True)
        self.pulsanteContatto.configure(fg_color="transparent", hover=True)
        self.pulsanteConversazioni.configure(fg_color="transparent", hover=True)
        self.pulsanteContenuti.configure(fg_color="transparent", hover=True)
        self.pulsanteMedia.configure(fg_color="transparent", hover=True)
        self.vista.destroy()
        self.vista = RiepilogoView(self, self.progetto)
    
    def mostra_vista_gruppi(self):
        self.pulsanteGruppo.configure(fg_color="#1F6AA5", hover=False)
        self.pulsanteRiepilogo.configure(fg_color="transparent", hover=True)
        self.pulsanteContatto.configure(fg_color="transparent", hover=True)
        self.pulsanteConversazioni.configure(fg_color="transparent", hover=True)
        self.pulsanteContenuti.configure(fg_color="transparent", hover=True)
        self.pulsanteMedia.configure(fg_color="transparent", hover=True)
        self.vista.destroy()
        self.vista = GruppiView(self, self.progetto.sorgente.gruppi, self.progetto.sorgente.contatti)

    def mostra_vista_conversazioni(self):
        self.pulsanteConversazioni.configure(fg_color="#1F6AA5", hover=False)
        self.pulsanteGruppo.configure(fg_color="transparent", hover=True)
        self.pulsanteRiepilogo.configure(fg_color="transparent", hover=True)
        self.pulsanteContatto.configure(fg_color="transparent", hover=True)
        self.pulsanteContenuti.configure(fg_color="transparent", hover=True)
        self.pulsanteMedia.configure(fg_color="transparent", hover=True)
        self.vista.destroy()
        self.vista = ConversazioniView(self, self.progetto.sorgente.chat ,self.progetto.sorgente.contatti)

    def mostra_vista_contatti(self):
        self.pulsanteContatto.configure(fg_color="#1F6AA5", hover=False)
        self.pulsanteRiepilogo.configure(fg_color="transparent", hover=True)
        self.pulsanteGruppo.configure(fg_color="transparent", hover=True)
        self.pulsanteConversazioni.configure(fg_color="transparent", hover=True)
        self.pulsanteContenuti.configure(fg_color="transparent", hover=True)
        self.pulsanteMedia.configure(fg_color="transparent", hover=True)
        self.vista.destroy()
        self.vista = ContattiView(self, self.progetto.sorgente.contatti)
    
    def mostra_vista_contenuti(self):
        self.pulsanteContenuti.configure(fg_color="#1F6AA5", hover=False)
        self.pulsanteRiepilogo.configure(fg_color="transparent", hover=True)
        self.pulsanteContatto.configure(fg_color="transparent", hover=True)
        self.pulsanteGruppo.configure(fg_color="transparent", hover=True)
        self.pulsanteConversazioni.configure(fg_color="transparent", hover=True)
        self.pulsanteMedia.configure(fg_color="transparent", hover=True)
        self.vista.destroy()
        self.vista = ContenutiView(self, self.progetto)

    def mostra_vista_media(self):
        self.pulsanteMedia.configure(fg_color="#1F6AA5", hover=False)
        self.pulsanteContenuti.configure(fg_color="transparent", hover=True)
        self.pulsanteRiepilogo.configure(fg_color="transparent", hover=True)
        self.pulsanteContatto.configure(fg_color="transparent", hover=True)
        self.pulsanteGruppo.configure(fg_color="transparent", hover=True)
        self.pulsanteConversazioni.configure(fg_color="transparent", hover=True)
        self.vista.destroy()
        self.vista = MediaView(self, self.progetto)


class Introduzione(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        #whaimage = ctk.CTkImage(PIL.Image.open(files("whafer.assets").joinpath("whatsapp.png")), size=(30, 30))
        gdriveimage = ctk.CTkImage(PIL.Image.open(files("whafer.assets").joinpath("GoogleDrive.png")), size=(30, 30))
        androidimage = ctk.CTkImage(PIL.Image.open(files("whafer.assets").joinpath("android.png")), size=(30, 30))
        localimage = ctk.CTkImage(PIL.Image.open(files("whafer.assets").joinpath("search.png")), size=(30, 30))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.title_label = ctk.CTkLabel(self.sidebar_frame, text="WhaFeR", font=ctk.CTkFont(size=20, weight="bold"), compound="right", padx=10)
        self.title_label.grid(row=0, column=0, padx=5, pady=(30,5))
        self.desc_label = ctk.CTkLabel(self.sidebar_frame, text="WhatsApp Forensic Reporter", font=ctk.CTkFont(size=14), compound="right", padx=10)
        self.desc_label.grid(row=1, column=0, padx=5)


        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Tema:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"],
                                                             command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="Ridimensionamento:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["100%", "110%", "120%", "80%", "90%"],
                                                     command=self.change_scaling_event)

        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        
        self.frame_azioni = ctk.CTkFrame(self)
        self.frame_azioni.grid(row=0, column=1, padx=150, pady=150)
        self.frame_azioni.grid_columnconfigure((0, 2), weight=1)
        self.frame_azioni.grid_rowconfigure((0, 2), weight=1)
        self.frame_azioni.configure(fg_color="transparent")

        # Sezione estrai

        self.estrazioneIntestazione = ctk.CTkLabel(self.frame_azioni, text="Estrai i dati da...",font=ctk.CTkFont(size=25))
        self.estrazioneIntestazione.grid(row=0, column=0, sticky="s", padx=10)

        self.estrazioneFrameBottoni = ctk.CTkFrame(self.frame_azioni)
        self.estrazioneFrameBottoni.grid(row=1, column=0, sticky="ns", padx=10, pady=10, ipadx=100)

        # bottone per caricare il progetto da Google Drive
        self.pulsanteGoogleDrive = ctk.CTkButton(self.estrazioneFrameBottoni, state="disabled", text_color_disabled="#636363", text="Google Drive", image=gdriveimage, compound="left", font=ctk.CTkFont(size=15), anchor="w", fg_color="darkgrey", border_spacing=15)
        self.pulsanteGoogleDrive.pack(fill="x", pady=10)

        # bottone per caricare il progetto da un telefono android
        self.pulsanteAndroid = ctk.CTkButton(self.estrazioneFrameBottoni, text="Android", image=androidimage, compound="left", font=ctk.CTkFont(size=15), command=self.estrai_android, anchor="w", border_spacing=15)
        self.pulsanteAndroid.pack(fill="x", pady=(0,10))
        self.popup_exists = False

        # bottone per caricare il progetto dal local storage
        self.pulsanteLocal = ctk.CTkButton(self.estrazioneFrameBottoni, text="Percorso locale", image=localimage, compound="left", font=ctk.CTkFont(size=15), command=self.estrai_locale_popup, anchor="w", border_spacing=15)
        self.pulsanteLocal.pack(fill="x", pady=(0,10))

        self.separatore = ttk.Separator(self.frame_azioni, orient="vertical")
        self.separatore.grid(row=0, column=1, rowspan=3, sticky="ns", padx=5, pady=30)

        self.progettoIntestazione = ctk.CTkLabel(self.frame_azioni, text="Apri un progetto",font=ctk.CTkFont(size=25))
        self.progettoIntestazione.grid(row=0, column=2, sticky="s", padx=10)

        self.progettoPulsante = ctk.CTkButton(self.frame_azioni, text="Seleziona un progetto", command=self.apri_progetto)
        self.progettoPulsante.grid(row=1, column=2, sticky="nsew", padx=10, pady=20)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
    
    def apri_progetto(self):
        percorsoProgetto = tk.filedialog.askdirectory(title="Seleziona un progetto precedentemente creato")
        if(percorsoProgetto):
            if (Path(percorsoProgetto+"/whafer.project")).exists():
                progetto = Progetto(percorsoProgetto)
                self.master.main = Applicazione(self.master, progetto)
                self.destroy()
            else:
                self.successPopup = ctk.CTkToplevel()
                self.successPopup.geometry("600x150")
                self.successPopup.title("Errore")
                self.successLabel = ctk.CTkLabel(self.successPopup, text="Non è presente alcun progetto WhaFeR nella cartella selezionata", font=ctk.CTkFont(size=14)).pack(pady=20)
                chiudi_btn = ctk.CTkButton(self.successPopup, text="CHIUDI", command=self.successPopup.destroy)
                chiudi_btn.pack(pady=10, padx=10)
                self.successPopup.attributes("-topmost",True)


    def estrai_locale_popup(self):
        self.infoPopup = ctk.CTkToplevel()
        self.infoPopup.geometry("700x400")
        self.infoPopup.title("Seleziona artefatti")
        self.infoLabel = ctk.CTkLabel(self.infoPopup, justify="left", text="Questa funzionalità consente di selezionare manualmente gli artefatti da sottoporre ad analisi.\n" \
                                                            "Assicurarsi di selezionare (almeno) i file:\n\n" \
                                                            "-msgstore.db\n-wa.db\n\n" \
                                                            "Se si è in possesso delle controparti cifrate (es: .crypt14 o .crypt15) è necessario\nallegare anche la chiave di cifratura (rinominandola 'key' se non lo è già),\naltresì non sarà possibile proseguire.\n"\
                                                            "Per estrarla dallo smartphone, fare riferimento alla documentazione di WhaFeR.\n\n" \
                                                            "Opzionalmente è possibile approfondire l'analisi allegando i file .xml come:\n\n" \
                                                            "-com.whatsapp_preferences_light.xml\n-startup_prefs.xml", font=ctk.CTkFont(size=14)).pack(pady=20)
        frame_pulsanti = ctk.CTkFrame(self.infoPopup, fg_color="transparent")
        frame_pulsanti.pack(pady=20)  # Centra il frame verticalmente nella finestra
        chiudi_btn = ctk.CTkButton(frame_pulsanti, text="ANNULLA", command=self.infoPopup.destroy, fg_color="#d14249", hover_color="#c6131b")
        chiudi_btn.pack(side="left", padx=10)
        seleziona_btn = ctk.CTkButton(frame_pulsanti, text="CONTINUA", command=self.estrai_locale)
        seleziona_btn.pack(side="left", padx=10)
        self.infoPopup.attributes("-topmost",True)


    def estrai_locale(self):
        self.infoPopup.destroy()
        artefatti = tk.filedialog.askopenfilenames(title="Seleziona gli artefatti da importare", multiple=True)
        if(artefatti):
            percorsoProgetto = tk.filedialog.askdirectory(title="Seleziona una cartella vuota in cui creare il progetto")
            if(percorsoProgetto):
                sorgenti = [artefatto for artefatto in artefatti if artefatto.endswith(".db") or artefatto.endswith(".xml")]
                encrypted = [artefatto for artefatto in artefatti if ".crypt" in artefatto or artefatto.endswith("key")]
                progetto = Progetto(percorsoProgetto, sorgenti=sorgenti, encrypted=encrypted)
                self.master.main = Applicazione(self.master, progetto)
                self.destroy()

    def estrai_android(self):

        if (self.popup_exists is not True):
            # Impedisce di aprire finestre duplicate
            self.popup_exists = True 

            # Crea una finestra di popup
            self.popup = ctk.CTkToplevel()
            self.popup.geometry("650x475")
            self.popup.title("Estrazione artefatti Android")
            label_popup = ctk.CTkLabel(self.popup, justify="left", text="Questa funzionalità consente di automatizzare l'estrazione di tutti gli\nartefatti necessari all'analisi forense da uno smartphone Android.\n" \
                                        "Per la sua corretta esecuzione è necessario, tuttavia, che sullo smartphone \noggetto di analisi siano stati ottenuti " \
                                        "preventivamente i\npermessi di ROOT, altresì non sarà possibile proseguire.\n\n" \
                                        "1. Assicurati che nelle impostazioni dello smartphone sia attivo il Debug USB.\n(Per farlo, approfondisci sulla documentazione di WhaFeR)\n" \
                                        "2. Sblocca lo smartphone e collegalo attraverso USB al PC\n" \
                                        "3. Se richiesto, conferma sullo smartphone il debug USB\n" \
                                        "4. Clicca su 'CONFERMA' in questa finestra\n" \
                                        "5. Se richiesto, concedere i permessi di root a 'com.android.shell'\n" \
                                        "6. Attendere il completamento dell'operazione\n\n" \
                                        "In caso di errori, fare riferimento alla documentazione di WhaFeR.\n" \
                                        "Talvolta può essere risolutivo scollegare e ricollegare\nnuovamente il cavo USB al pc, assicurandosi di \ncompiere questa operazione con smartphone sbloccato.")
            label_popup.pack(pady=20)
            frame_pulsanti = ctk.CTkFrame(self.popup, fg_color="transparent")
            frame_pulsanti.pack(pady=20)  # Centra il frame verticalmente nella finestra
            chiudi_btn = ctk.CTkButton(frame_pulsanti, text="ANNULLA", command=self.chiudi_popup, fg_color="#d14249", hover_color="#c6131b")
            chiudi_btn.pack(side="left", padx=10)
            continua_btn = ctk.CTkButton(frame_pulsanti, text="CONTINUA", command=self.esegui_comando_adb)
            continua_btn.pack(side="left", padx=10)
            self.error_label = ctk.CTkLabel(self.popup, text="", font=ctk.CTkFont(weight="bold"))
            self.error_label.pack(pady=10)
            self.popup.attributes("-topmost",True)
            self.popup.protocol("WM_DELETE_WINDOW", self.chiudi_popup) # Intercetta l'evento di chiusura della finestra con il metodo "protocol" ed esegue "chiudi_popup"

        
    def chiudi_popup(self):
        self.popup.destroy()
        self.popup_exists = False

    def esegui_comando_adb(self):
        try:
            # Esegui il comando ADB
            proc1 = subprocess.Popen('adb shell su', stdin = subprocess.PIPE)
            proc1.communicate(b'mkdir /sdcard/whafer_extractedfiles\ncp /data/data/com.whatsapp/files/key /sdcard/whafer_extractedfiles/\ncp /data/data/com.whatsapp/databases/msgstore.db /sdcard/whafer_extractedfiles/\ncp /data/data/com.whatsapp/databases/wa.db /sdcard/whafer_extractedfiles/\ncp /data/data/com.whatsapp/shared_prefs/com.whatsapp_preferences_light.xml /sdcard/whafer_extractedfiles/\ncp /data/data/com.whatsapp/shared_prefs/startup_prefs.xml /sdcard/whafer_extractedfiles/\nexit\n')
            proc2 = subprocess.Popen('adb pull /sdcard/whafer_extractedfiles/')
            proc2.wait()
            proc1.terminate()
            proc2.terminate()            
     
            # Controlla se ci sono errori
            if proc1.returncode != 0:
                self.error_label.configure(text="Errore. Controlla la console per il log.")
                print("Errore: ", proc1.stderr)
                
            elif proc2.returncode != 0:
                self.error_label.configure(text="Errore. Controlla la console per il log.")
                print("Errore: ", proc2.stderr)
                
            else:
                print("Completato")
                self.popup.destroy()
                percorsoProgetto = tk.filedialog.askdirectory(title="Seleziona una cartella vuota in cui creare il progetto")
                sorgenti = ['whafer_extractedfiles/msgstore.db', 'whafer_extractedfiles/wa.db', 'whafer_extractedfiles/com.whatsapp_preferences_light.xml', 'whafer_extractedfiles/startup_prefs.xml']
                progetto = Progetto(percorsoProgetto, sorgenti=sorgenti)
                self.master.main = Applicazione(self.master, progetto)

                # Rimozione dei file temporanei estratti dallo smartphone
                projectFolder = os.path.dirname(os.path.abspath(__file__))
                shutil.rmtree(projectFolder+"/whafer_extractedfiles")

                self.destroy()
                
        except Exception as e:
            print("Si è verificato un errore:", str(e))

    
class ControlloDipendenze(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="Controllo dipendenze: FALLITO\n Assicurati che adb sia installato e inserito \n correttamente nelle variabili d'ambiente.", font=ctk.CTkFont(size=14)).pack(pady=20)
        close = ctk.CTkButton(self, text="CHIUDI", command=self.quit, fg_color="red", hover_color="darkred").pack(pady=5)

def main():
    app = ctk.CTk()
    ctk.set_appearance_mode("System")
    app.title("WhaFeR - WhatsApp Forensic Reporter")

    # Controllo delle dipendenze
    try:
        check = subprocess.Popen('adb --version', stdin = subprocess.PIPE, stdout=subprocess.PIPE, stderr=None)
        app.geometry(f"{1100}x{580}")
        app.main = Introduzione(app).pack(fill="both", expand=True)
    except:
        print("Errore: adb non trovato. Assicurati che sia installato e inserito nelle'variabili d'ambiente.")
        app.geometry(f"{500}x{150}")
        app.main = ControlloDipendenze(app).pack(fill="both", expand=True)
    
    app.mainloop()
    

if __name__ == "__main__":
    main()
