from tinycards import Tinycards
from tinycards.model import Deck
import sqlite3
from data import tinycards_speech_langs

def generate_deck(id_of_first_word, target_lang, words_to_be_excluded):
    tinycards = Tinycards("frequencyl", "Uktuzugo_55")
    cards_to_be_added = []

    db = sqlite3.connect("databases/words.db")
    cursor = db.cursor()
    origin_table = cursor.execute("SELECT * FROM words").fetchall()
    translation_table = cursor.execute(f"SELECT * FROM {target_lang}").fetchall()

    for i in range(id_of_first_word - 1, 6318):
        if origin_table[i][1] not in words_to_be_excluded:
            cards_to_be_added.append((origin_table[i][1], translation_table[i][2]))

    deck_no = 1
    
    speech_lang_list = ["en", ""]
    if target_lang in tinycards_speech_langs:
        speech_lang_list[1] = tinycards_speech_langs[f"{target_lang}"]

    links = {}
    while len(cards_to_be_added) > 150:
        deck_name = f"Deck no: {deck_no}"
        deck = Deck(deck_name, private=True, shareable=True, tts_languages=speech_lang_list)
        created_deck = tinycards.create_deck(deck)
        for i in range(150):
            created_deck.add_card(cards_to_be_added[i])
        del cards_to_be_added[:150]
        tinycards.update_deck(created_deck)
        links[deck_no] = created_deck.shareable_link
        deck_no += 1
    
        deck_name = f"Deck no: {deck_no}"
    deck = Deck(deck_name, private=True, shareable=True, tts_languages=speech_lang_list)
    created_deck = tinycards.create_deck(deck)
    for i in range(len(cards_to_be_added)):
        created_deck.add_card(cards_to_be_added[i])
    tinycards.update_deck(created_deck)
    links[deck_no] = created_deck.shareable_link

    return links
