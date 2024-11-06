from typing import BinaryIO
import rfc3161ng
import re

DIMENSIONE_BUFFER = 65536 

def costruisci_calcola_hash(primoAlgoritmo, secondoAlgoritmo = None):
    def calcola_hash(oggetto: BinaryIO) -> list[str]:

        hashFinale = []

        for algoritmo in [primoAlgoritmo, secondoAlgoritmo]:
            if not algoritmo:
                continue
            hasher = algoritmo()
            oggetto.seek(0)
            while True:
                datiFile = oggetto.read(DIMENSIONE_BUFFER)
                if not datiFile:
                    break
                hasher.update(datiFile)
            hashFinale.append(f"{hasher.name}: {hasher.hexdigest()}")

        return hashFinale
    
    return calcola_hash

def costruisci_controllo_hash(*args):
    raise NotImplementedError
    def controlla_hash(oggetto: BinaryIO, controlloIntegrita: str) -> bool:

        listaHash = re.split(r"\n|: ", controlloIntegrita)

        for algoritmo, hash in zip(args, listaHash[1::2]):
            hasher = algoritmo()
            hasher.update(oggetto)

            if hasher.hexdigest() != hash:
                return False
            
        return True
    
    return controlla_hash

def costruisci_funzione_rfc3161(indirizzoServer, certificato):
    def calcola_timestamp(oggetto: str) -> str:

        serverTimestamp = rfc3161ng.RemoteTimestamper(indirizzoServer, certificate=certificato)
        timestamp = serverTimestamp.timestamp(data=oggetto)

        return rfc3161ng.get_timestamp(timestamp)

    return calcola_timestamp