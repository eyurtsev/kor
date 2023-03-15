**⚠ WARNING: Prototype with unstable API. 🚧**  

[![test](https://github.com/eyurtsev/kor/actions/workflows/test.yml/badge.svg?branch=main&event=push)](https://github.com/eyurtsev/kor/actions/workflows/test.yml)

# Kor

This is a half-baked prototype that "helps" you extract structured data from text using LLMs 🧩.

Specify the schema of what should be extracted and provide some examples.

Kor will generate a prompt, send it to the specified LLM and parse out the
output. You might even get results back.


```python

from kor.extraction import Extractor
from kor.nodes import Object, Text
from langchain import ChatOpenAI

llm = ChatOpenAI(model_name="gpt-3.5-turbo", 
    temperature = 0,
    max_tokens = 2000,
    frequency_penalty = 0,
    presence_penalty = 0,
    top_p = 1.0,
)

model = Extractor(llm)

schema = Object(
    id="player",
    description=(
        "User is controling a music player to select songs, pause or start them or play"
        " music by a particular artist."
    ),
    attributes=[
        Text(id="song", description="User wants to play this song", examples=[]),
        Text(id="album", description="User wants to play this album", examples=[]),
        Text(
            id="artist",
            description="Music by the given artist",
            examples=[("Songs by paul simon", "paul simon")],
        ),
        Text(
            id="action",
            description="Action to take one of: `play`, `stop`, `next`, `previous`.",
            examples=[
                ("Please stop the music", "stop"),
                ("play something", "play"),
                ("next song", "next"),
            ],
        ),
    ],
)

model("can you play all the songs from paul simon and led zepplin", schema)
```

```python
{'player': [{'artist': ['paul simon', 'led zepplin']}]}
```

See [documentation](https://eyurtsev.github.io/kor/).

## Compatibility

`Kor` is tested against python 3.8, 3.9, 3.10, 3.11.

## Installaton 

```sh
pip install kor
```

## 💡 Ideas

Ideas of some things that could be done with Kor.

* Extract data from text: Define what information should be extracted from a segment
* Convert an HTML form into a Kor form and allow the user to fill it out using natural language. (Convert HTML forms -> API? Or not.)
* Add some skills to an AI assistant

## 🚧 Prototype

This a prototype and the API is not expected to be stable as it hasn't been
tested against real world examples.

##  ✨ Where does Kor excel?  🌟 

* Making mistakes! Plenty of them. Quality varies with the underlying language model, the quality of the prompt, and the number of bugs in the adapter code.
* Slow! It uses large prompts with examples, and works best with the larger slower LLMs.
* Crashing for long enough pieces of text! Context length window could become
  limiting when working with large forms or long text inputs.
* Incorrectly grouping results (see documentation section on objects).

## Limtations

This package has no limitations; however, look at the section directly above as
well as at compatibility.

## Potential Changes

* Adding validators
* Built-in components to quickly assemble schema with examples
* Add routing layer to select appropriate extraction schema for a use case when
  many schema exist

## 🎶 Why the name?

Fast to type and sufficiently unique.

## Contributing

If you have any ideas or feature requests, please open an issue and share!

See [CONTRIBUTING.md](https://github.com/eyurtsev/kor/blob/main/CONTRIBUTING.md) for more information.

## Other packages

Probabilistically speaking this package is unlikely to work for your use case.

So here are some great alternatives:

* [Promptify](https://github.com/promptslab/Promptify)
* [MiniChain](https://srush.github.io/MiniChain/examples/stats/)
