import json
from pathlib import Path


# percorso del file che conterrà la collezione salvata
SAVE_PATH = Path(
    "saves/player_save.zao"
)


# salva su disco la collezione del giocatore
def save_card_collection(card_collection):

    # creo la cartella saves se non esiste ancora
    SAVE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # recupero i dati preparati dalla collezione
    save_data = card_collection.get_save_data()

    # apro il file e scrivo i dati in formato JSON
    with SAVE_PATH.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            save_data,
            file,
            indent=4,
            ensure_ascii=False
        )

# carica dal disco la collezione del giocatore
def load_card_collection(card_collection):

    # se il salvataggio non esiste, mantengo una collezione vuota
    if not SAVE_PATH.exists():
        return False

    # apro il file e leggo i dati JSON contenuti al suo interno
    with SAVE_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:

        save_data = json.load(file)

    # ricostruisco la collezione usando i dati caricati
    card_collection.load_save_data(
        save_data
    )

    # segnalo che il caricamento è avvenuto correttamente
    return True