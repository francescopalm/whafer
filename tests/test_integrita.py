from whafer import integrita
import hashlib
import io

def testa_singolo_hash():
    """ Testa l'uso di `calcola_hash` con un singolo algoritmo """
    algoritmoHash = integrita.costruisci_calcola_hash(hashlib.sha256)
    with io.BytesIO(b"ciao") as dati:
        hash = algoritmoHash(dati)
    assert isinstance(hash, str)

def testa_doppio_hash():
    """ Testa l'uso di `calcola_hash` con due algoritmi """
    algoritmoHash = integrita.costruisci_calcola_hash(hashlib.sha256, hashlib.md5)
    with io.BytesIO(b"ciao") as dati:
        hash = algoritmoHash(dati)
    assert isinstance(hash, str)
