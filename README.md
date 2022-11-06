# Anki Deck for English Vocabulary

This is a Python package which generates a deck for the English words in `list.txt`.

## Installation

Install the requirements from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

1. [Register a free account with Merriam-Webster,](https://dictionaryapi.com/)
    and choose a key for Merriam-Webster's Collegiate® Dictionary with Audio.

2. Create a file `config.yaml` that contains this key:

    `config.yaml`:
```yaml
dictionary: <KEY>
```

3. Run `python retrieve.py` to populate the cache with definitions for the words
    in `list.txt`.

4. Run `python parse.py` to generate an Anki deck.

5. Open `english.apkg` in Anki.
