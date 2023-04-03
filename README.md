**⚠ WARNING: Prototype with unstable API. 🚧**  

[![Unit Tests](https://github.com/eyurtsev/kor/actions/workflows/test.yml/badge.svg?branch=main&event=push)](https://github.com/eyurtsev/kor/actions/workflows/test.yml)
[![Test Docs](https://github.com/eyurtsev/kor/actions/workflows/doc_test.yaml/badge.svg?branch=main&event=push)](https://github.com/eyurtsev/kor/actions/workflows/doc_test.yaml)

# Kor


This is a half-baked prototype that "helps" you extract structured data from text using LLMs 🧩.

Specify the schema of what should be extracted and provide some examples.

Kor will generate a prompt, send it to the specified LLM and parse out the
output. 

You might even get results back.

See [documentation](https://eyurtsev.github.io/kor/).

## Version >=0.4.0

* Integrated with langchain framework.
* The code below uses Kor style schema, but you can also use [pydantic](https://eyurtsev.github.io/kor/validation.html).


```python

  from langchain.chat_models import ChatOpenAI
  from kor import create_extraction_chain, Object, Text, Number

  llm = ChatOpenAI(
      model_name="gpt-3.5-turbo",
      temperature=0,
      max_tokens=2000,
      frequency_penalty=0,
      presence_penalty=0,
      top_p=1.0,
  )

  schema = Object(
    id="player",
    description=(
        "User is controling a music player to select songs, pause or start them or play"
        " music by a particular artist."
    ),
    attributes=[
        Text(
            id="song",
            description="User wants to play this song",
            examples=[],
            many=True,
        ),
        Text(
            id="album",
            description="User wants to play this album",
            examples=[],
            many=True,
        ),
        Text(
            id="artist",
            description="Music by the given artist",
            examples=[("Songs by paul simon", "paul simon")],
            many=True,
        ),
        Text(
            id="action",
            description="Action to take one of: `play`, `stop`, `next`, `previous`.",
            examples=[
                ("Please stop the music", "stop"),
                ("play something", "play"),
                ("play a song", "play"),
                ("next song", "next"),
            ],
        ),
    ],
    many=False,
)

  chain = create_extraction_chain(llm, schema, encoder_or_encoder_class='json')
  chain.predict_and_parse(text="play songs by paul simon and led zeppelin and the doors")['data']
```

```python
  {'player': {'artist': ['paul simon', 'led zeppelin', 'the doors']}}
```

## Compatibility

`Kor` is tested against python 3.8, 3.9, 3.10, 3.11.

## Installaton 

```sh
pip install kor
```

## 💡 Ideas

Ideas of some things that could be done with Kor.

* Extract data from text that matches an extraction schema.
* Power an AI assistant with skills by precisely understanding a user request.
* Provide natural language access to an existing API.

## 🚧 Prototype

Prototype! So the API is not expected to be stable!

##  ✨ What does Kor excel at?  🌟 

* Making mistakes! Plenty of them!
* Slow! It uses large prompts with examples, and works best with the larger slower LLMs.
* Crashing for long enough pieces of text! Context length window could become
  limiting when working with large forms or long text inputs.

The expectation is that as LLMs improve some of these issues will be mitigated.

## Limtations

No limitations whatsoever. Do take a look at the section directly above as well
as at the section about compatibility.

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
