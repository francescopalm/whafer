from pathlib import Path
from shutil import copy2
import csv
import hashlib
import db
import subprocess
from integrita import costruisci_calcola_hash
from interfacce import Sorgente, Gruppo, Contatto, Messaggio

class Progetto:
    def __init__(self, path: str, sorgenti: list = None, encrypted: list = None):
        self.percorso = Path(path)

        if not (self.percorso / "whafer.project").exists():
            with open(self.percorso / "whafer.project", 'w+') as nf:
                pass

        if not (self.percorso / "sorgenti").exists():
            (self.percorso / "sorgenti").mkdir()

        if not (self.percorso / "encrypted").exists():
            (self.percorso / "encrypted").mkdir()

        if not (self.percorso / "media").exists():
            (self.percorso / "media").mkdir()

        if not (self.percorso / "reports").exists():
            (self.percorso / "reports").mkdir()

        if sorgenti is not None:
            for artefatto in sorgenti:
                copy2(artefatto, str(self.percorso / "sorgenti"))

        if encrypted is not None:
            for file in encrypted:
                copy2(file, str(self.percorso / "encrypted"))

        # Decripta msgstore se necessario
        if not (self.percorso / "sorgenti" / "msgstore.db").exists():
            percorsoChiave = self.percorso / "encrypted" / "key"
            percorsoMsgstore = list((self.percorso / "encrypted").glob("**/msgstore.db.crypt*"))[0]
            subprocess.run(["wadecrypt", 
                            str(percorsoChiave),
                            str(percorsoMsgstore),
                            str(self.percorso / "sorgenti" / "msgstore.db")])
            
        # Decripta wa se necessario
        if not (self.percorso / "sorgenti" / "wa.db").exists():
            if list((self.percorso / "encrypted").glob("**/wa.db.crypt*")):
                percorsoChiave = self.percorso / "encrypted" / "key"
                percorsoWa = list((self.percorso / "encrypted").glob("**/wa.db.crypt*"))[0]
                subprocess.run(["wadecrypt", 
                                str(percorsoChiave),
                                str(percorsoWa),
                                str(self.percorso / "sorgenti" / "wa.db")])

        self.sorgentefile = db.SorgenteDB(self.percorso / "sorgenti" / "msgstore.db")

        # Esegui gli hash
        funzione_hash = costruisci_calcola_hash(hashlib.sha256, hashlib.md5)
        if not (self.percorso / "integrità.csv").exists():
            (self.percorso / "integrità.csv").touch()

            with open(self.percorso / "integrità.csv", mode="w", newline='') as integrita:
                writer = csv.writer(integrita, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for artefatto in (self.percorso / "sorgenti").glob('**/*'):
                    with open(artefatto, mode="rb") as file:
                        artefattiHash = funzione_hash(file)
                        writer.writerow([str(artefatto)] + artefattiHash)

                for encrypted in (self.percorso / "encrypted").glob('**/*'):
                    with open(encrypted, mode="rb") as file:
                        encryptedHash = funzione_hash(file)
                        writer.writerow([str(encrypted)] + encryptedHash)

    @property
    def sorgente(self)->Sorgente:
        return self.sorgentefile