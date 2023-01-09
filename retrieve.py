import asyncio
import json
import shelve
import time

import aiohttp
import numpy as np
import yaml


class RateLimiter:
    """Limit the rate for an API.

    Args:
        rate (float): Rate.
    """

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


# Load the config. This contains API keys.
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Setup the dictionary API.
api_url = (
    f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/"
    f"{{word}}?key={config['dictionary']}"
)
api_rate = RateLimiter(rate=10)

with shelve.open("responses.shelve") as db:
    if "responses" not in db:
        db["responses"] = {}
    responses = dict(db["responses"])

    async def query(session, word):
        if word in responses:
            return
        async with api_rate:
            print("Requesting:", word)
            async with session.get(api_url.format(word=word)) as response:
                responses[word] = json.loads(await response.text())
            print("Received:", word)

    async def query_many(words):
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*[query(session, word) for word in words])

    with open("list.txt", "r") as f:
        words = []

        for word in f.read().splitlines():
            word = word.lower()

            # Delete possible definition.
            word = word.split(" - ", 1)[0].strip()

            # Delete possible prefix "to ".
            if word.startswith("to "):
                word = word[3:].strip()

            words.append(word)

        # Store the response for every word.
        words = sorted(np.unique(words))
        asyncio.run(query_many(words))
        db["responses"] = responses
        db["words"] = words
