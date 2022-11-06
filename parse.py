import shelve
from collections import defaultdict

import genanki

# Load the responses for all words.
with shelve.open("responses.shelve", "r") as db:
    db = dict(db)

# Define some custom definitions for words that the API did not provide a definition
# for.
custom_responses = defaultdict(lambda: [])
custom_responses["archnemesis"] = [{"fl": "noun", "shortdef": ["archrival"]}]

# Produce an HTML-formatted meaning for every word.
meanings = []
for word in db["words"]:
    response = db["responses"][word]
    out = ""
    for meaning in response + custom_responses[word]:
        # The key "fl" corresponds to the part of speech. If there is no part of speech,
        # skip it.
        if "fl" in meaning:
            pos = meaning["fl"]
            if out:
                out += " <br><br> "
            # Generate a list if there are multiple definitions.
            if len(meaning["shortdef"]) == 1:
                definition = meaning["shortdef"][0]
            else:
                definition = "<br>".join(
                    f"{i + 1}. " + d for i, d in enumerate(meaning["shortdef"])
                )
            out += f"<b>{pos}</b> <br> {definition}"
    # If `out` is still empty, skip the word. Provide a custom definition and try again.
    if not out:
        print("Skipping", word)
        continue
    meanings.append((word, out))

anki_model = genanki.Model(
    1874940493,
    "Question and Answer",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Question}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
        },
    ],
)

# Generate the deck.
deck = genanki.Deck(1917659204, "English Vocabulary")
for word, meaning in meanings:
    note = genanki.Note(model=anki_model, fields=[word, meaning], guid=word)
    deck.add_note(note)
package = genanki.Package(deck)
package.write_to_file("english.apkg")
