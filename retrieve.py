import asyncio
import requests
import time
import json
import genanki
import shelve
import aiohttp


class RateLimiter:
    def __init__(self, rate):
        self.rate = rate
        self.last_request = None

    async def __aenter__(self):
        if self.last_request is not None:
            while time.time() <= self.last_request + 1 / self.rate:
                await asyncio.sleep(1 / self.rate / 10)
        self.last_request = time.time()

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        pass




api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
api_rate = RateLimiter(rate=5)

responses = {}


async def query(session, word):
    async with api_rate:
        print("Requesting", word)
        async with session.get(api_url.format(word=word)) as response:
            responses[word] = json.loads(await response.text())
        print("Received", word)


async def query_many(words):
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[query(session, word) for word in words])

        


with open("list.txt", "r") as f:
    words = f.read().splitlines()

word_meanings = []

meanings = asyncio.run(query_many(words))
print(responses.keys())




exit()

for word in words:
    with api_rate:
        response = requests.get(api_url.format(word=word))
        word_def = json.loads(response.text)
        out = ""
        for meaning in word_def[0]["meanings"]:
            pos = meaning["partOfSpeech"]
            for d in meaning["definitions"]:
                out += f"[{pos}] {d['definition']} "
        word_meanings.append(out)
        print(word, out)

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

deck = genanki.Deck(1917659204, "English Vocabulary")

for word, meaning in zip(words, word_meanings):
    note = genanki.Note(model=anki_model, fields=[word, meaning])
    deck.add_note(note)

package = genanki.Package(deck)
package.write_to_file("english.apkg")
