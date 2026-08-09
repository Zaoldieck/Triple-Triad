# quantità massima possedibile per una singola carta
MAX_CARD_QUANTITY = 99


# gestisce quantità e scoperta delle carte del giocatore
class CardCollection:

    def __init__(self):

        # associa ogni card_id alla quantità posseduta
        self.card_quantities = {}

        # contiene gli ID delle carte possedute almeno una volta
        self.discovered_card_ids = set()

    # controlla se una carta è disponibile in quantità infinita
    def is_unlimited(self, card):

        # tutte le carte di rarità 1 sono sempre disponibili
        return card.rarity == 1

    # controlla se una carta è stata scoperta
    def is_discovered(self, card):

        # le carte di rarità 1 sono scoperte automaticamente
        if self.is_unlimited(card):
            return True

        # le altre carte sono scoperte dopo il primo ottenimento
        return card.card_id in self.discovered_card_ids

    # restituisce la quantità posseduta di una carta
    def get_quantity(self, card):

        # None rappresenta la quantità infinita
        if self.is_unlimited(card):
            return None

        # una carta mai ottenuta oppure persa completamente restituisce 0
        return self.card_quantities.get(
            card.card_id,
            0
        )

    # aggiunge una o più copie di una carta alla collezione
    def add_card(self, card, amount=1):

        # accetto soltanto quantità positive
        if amount <= 0:
            raise ValueError(
                f"Card amount must be positive: {amount}"
            )

        # le carte infinite non hanno bisogno di copie aggiuntive
        if self.is_unlimited(card):
            return 0

        # recupero la quantità attualmente posseduta
        current_quantity = self.get_quantity(card)

        # impedisco alla quantità di superare il limite massimo
        new_quantity = min(
            current_quantity + amount,
            MAX_CARD_QUANTITY
        )

        # calcolo quante copie sono state effettivamente aggiunte
        added_quantity = new_quantity - current_quantity

        # salvo la nuova quantità
        self.card_quantities[card.card_id] = new_quantity

        # la carta rimane scoperta dopo il primo ottenimento
        if new_quantity > 0:
            self.discovered_card_ids.add(card.card_id)

        # restituisco il numero di copie realmente aggiunte
        return added_quantity

    # rimuove una o più copie di una carta dalla collezione
    def remove_card(self, card, amount=1):

        # accetto soltanto quantità positive
        if amount <= 0:
            raise ValueError(
                f"Card amount must be positive: {amount}"
            )

        # le carte di rarità 1 sono infinite e non possono essere perse
        if self.is_unlimited(card):
            return 0

        # recupero la quantità attualmente posseduta
        current_quantity = self.get_quantity(card)

        # non posso rimuovere più copie di quelle possedute
        removed_quantity = min(
            current_quantity,
            amount
        )

        # calcolo e salvo la quantità rimanente
        self.card_quantities[card.card_id] = (
            current_quantity - removed_quantity
        )

        # restituisco il numero di copie realmente rimosse
        return removed_quantity

    # prepara i dati della collezione per il salvataggio
    def get_save_data(self):

        return {
            # salvo le quantità possedute delle carte
            "card_quantities": self.card_quantities,

            # converto il set in una lista perché JSON non supporta set()
            "discovered_card_ids": sorted(
                self.discovered_card_ids
            )
        }

    # ricostruisce la collezione usando i dati di un salvataggio
    def load_save_data(self, save_data):

        # recupero le quantità, oppure un dizionario vuoto se mancano
        self.card_quantities = dict(
            save_data.get(
                "card_quantities",
                {}
            )
        )

        # recupero le carte scoperte e riconverto la lista in un set
        self.discovered_card_ids = set(
            save_data.get(
                "discovered_card_ids",
                []
            )
        )