# questo e' il caricatore che legge cards.json e trasforma ogni voce in un oggetto Card.

import json

from pathlib import Path
from game.card import Card


# carica le carte presenti in un file JSON
def load_cards(file_path, active_card_sets):

    # apro il file e converto il JSON in dati Python
    with open(file_path, "r", encoding="utf-8") as file:
        cards_data = json.load(file)

    # lista che conterrà gli oggetti Card creati
    cards = []

    # insieme usato per individuare eventuali ID duplicati
    seen_card_ids = set()

    # trasformo ogni carta del JSON in un oggetto Card
    for card_data in cards_data:

        # recupero l'identificatore della carta
        card_id = card_data["card_id"]

        # controllo che l'ID sia una stringa non vuota
        if (
            not isinstance(card_id, str)
            or not card_id.strip()
        ):
            raise ValueError(
                f"Invalid card_id: {card_id}"
            )

        # recupero il nome della carta
        card_name = card_data["name"]

        # controllo che il nome sia una stringa non vuota
        if (
            not isinstance(card_name, str)
            or not card_name.strip()
        ):
            raise ValueError(
                f"Invalid card name for "
                f"{card_id}: {card_name}"
            )

        # impedisco la presenza di due carte con lo stesso ID
        if card_id in seen_card_ids:
            raise ValueError(
                f"Duplicate card_id found: {card_id}"
            )

        # salvo l'ID tra quelli già incontrati
        seen_card_ids.add(card_id)

        # recupero i set ai quali appartiene la carta
        card_sets = card_data["card_sets"]

        # controllo che card_sets sia una lista non vuota
        if (
            not isinstance(card_sets, list)
            or not card_sets
        ):
            raise ValueError(
                f"Invalid card_sets for {card_id}: "
                f"{card_sets}"
            )

        # controllo che ogni set sia una stringa non vuota
        if not all(
            isinstance(card_set, str)
            and card_set.strip()
            for card_set in card_sets
        ):
            raise ValueError(
                f"Invalid card set for {card_id}: "
                f"{card_sets}"
            )

        # controllo se la carta appartiene ad almeno un set abilitato
        belongs_to_active_set = any(
            card_set in active_card_sets
            for card_set in card_sets
        )

        # ignoro la carta se non appartiene ai set abilitati
        if not belongs_to_active_set:
            continue

        # recupero il percorso dell'illustrazione
        image_path = card_data["image_path"]

        # controllo che il file dell'illustrazione esista
        if not Path(image_path).is_file():
            raise FileNotFoundError(
                f"Card image not found for "
                f"{card_id}: {image_path}"
            )


        
        card = Card(
            card_id=card_id,
            name=card_name,
            image_path=image_path,
            top=card_data["top"],
            right=card_data["right"],
            bottom=card_data["bottom"],
            left=card_data["left"],
            rarity=card_data["rarity"],
            element=card_data["element"],
            card_sets=card_sets
        )

        # aggiungo la carta appena creata alla lista
        cards.append(card)

    # restituisco tutte le carte caricate
    return cards