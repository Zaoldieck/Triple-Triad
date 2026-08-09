# questo e' il caricatore che legge cards.json e trasforma ogni voce in un oggetto Card.

import json

from game.card import Card


# carica le carte presenti in un file JSON
def load_cards(file_path):

    # apro il file e converto il JSON in dati Python
    with open(file_path, "r", encoding="utf-8") as file:
        cards_data = json.load(file)

    # lista che conterrà gli oggetti Card creati
    cards = []

    # trasformo ogni carta del JSON in un oggetto Card
    for card_data in cards_data:

        card = Card(
            card_id=card_data["card_id"],
            name=card_data["name"],
            image_path=card_data["image_path"],
            top=card_data["top"],
            right=card_data["right"],
            bottom=card_data["bottom"],
            left=card_data["left"],
            rarity=card_data["rarity"],
            element=card_data["element"],
            card_sets=card_data["card_sets"]
        )

        # aggiungo la carta appena creata alla lista
        cards.append(card)

    # restituisco tutte le carte caricate
    return cards