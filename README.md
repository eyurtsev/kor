[![Unit Tests](https://github.com/eyurtsev/kor/actions/workflows/test.yml/badge.svg?branch=main&event=push)](https://github.com/eyurtsev/kor/actions/workflows/test.yml)
[![Test Docs](https://github.com/eyurtsev/kor/actions/workflows/doc_test.yaml/badge.svg?branch=main&event=push)](https://github.com/eyurtsev/kor/actions/workflows/doc_test.yaml)
[![Release Notes](https://img.shields.io/github/release/eyurtsev/kor)](https://github.com/eyurtsev/kor/releases)
[![Downloads](https://static.pepy.tech/badge/kor/month)](https://pepy.tech/project/kor)
[![Open Issues](https://img.shields.io/github/issues-raw/eyurtsev/kor)](https://github.com/eyurtsev/kor/issues)
[![](https://dcbadge.vercel.app/api/server/6adMQxSpJS?compact=true&style=flat)](https://discord.com/channels/1038097195422978059/1170024642245832774)


# Kor

This is a half-baked prototype that "helps" you extract structured data from text using LLMs 🧩.

Specify the schema of what should be extracted and provide some examples.

Kor will generate a prompt, send it to the specified LLM and parse out the
output.

You might even get results back.

So yes – it’s just another wrapper on top of LLMs with its own flavor of abstractions. 😸

See [documentation](https://eyurtsev.github.io/kor/).

Integrated with the [LangChain framework 😽💗 🦜🔗](https://python.langchain.com/en/latest/index.html).

## Kor vs. LangChain

There are 3 different approaches for extracting information using LLMs: 

1. [prompt based/parsing](https://python.langchain.com/docs/use_cases/extraction/how_to/parse)
2. [function/tool calling](https://python.langchain.com/docs/use_cases/extraction/quickstart)
3. JSON mode

Please see the LangChain [extraction use case docs](https://python.langchain.com/docs/use_cases/extraction/) for an overview.

Kor has a pretty good implementation of the **parsing** approach. The approach works with all good-enough LLMs regardless
of whether they support function/tool calling or JSON modes.

Extraction quality is principally driven by providing good reference examples and good schema documentation.

Please see guidelines [here](https://python.langchain.com/docs/use_cases/extraction/guidelines) and [here](https://eyurtsev.github.io/kor/guidelines.html).

## Version 1.0.0 Release

* `kor` compatible with both pydantic v2 and v1.
* pydantic v2 had significant breaking changes w/ respect to v1, `kor` major
  version bump was used as a precaution.


Main things to watch out for:

1. Use a `default` value for any Optional fields if using pydantic v2 for validation.

```python
class MusicRequest(BaseModel):
    song: Optional[List[str]] = Field(
        default=None,
        description="The song(s) that the user would like to be played."
    )
```

2. Kor schema is typed checked using pydantic. Pydantic v2 is stricter, and may
   catch issues that were hiding in existing user code that was using the `kor`
   library.

3. Serialization has not yet been implemented with pydantic v2.


## Kor style schema

```python
from langchain.chat_models import ChatOpenAI
from kor import create_extraction_chain, Object, Text

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    max_tokens=2000,
    model_kwargs = {
        'frequency_penalty':0,
        'presence_penalty':0,
        'top_p':1.0
    }
)

schema = Object(
    id="player",
    description=(
        "User is controlling a music player to select songs, pause or start them or play"
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
chain.invoke("play songs by paul simon and led zeppelin and the doors")['data']
```

```python
{'player': {'artist': ['paul simon', 'led zeppelin', 'the doors']}}
```

## Pydantic style schema

* See documentation here [pydantic](https://eyurtsev.github.io/kor/validation.html).

```python 
class Action(enum.Enum):
    play = "play"
    stop = "stop"
    previous = "previous"
    next_ = "next"


class MusicRequest(BaseModel):
    song: Optional[List[str]] = Field(
        default=None,
        description="The song(s) that the user would like to be played."
    )
    album: Optional[List[str]] = Field(
        default=None,
        description="The album(s) that the user would like to be played."
    )
    artist: Optional[List[str]] = Field(
        default=None,
        description="The artist(s) whose music the user would like to hear.",
        examples=[("Songs by paul simon", "paul simon")],
    )
    action: Optional[Action] = Field(
        default=None,
        description="The action that should be taken; one of `play`, `stop`, `next`, `previous`",
        examples=[
            ("Please stop the music", "stop"),
            ("play something", "play"),
            ("play a song", "play"),
            ("next song", "next"),
        ],
    )
    
schema, validator = from_pydantic(MusicRequest)   
chain = create_extraction_chain(
    llm, schema, encoder_or_encoder_class="json", validator=validator
)
chain.invoke("stop the music now")["validated_data"]
```

```python
MusicRequest(song=None, album=None, artist=None, action=<Action.stop: 'stop'>)
```



## Compatibility

`Kor` is tested against python 3.8, 3.9, 3.10, 3.11.

## Installation

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

## Limitations

Kor has no limitations. (Just kidding.)

Take a look at the section above and at the compatibility section.

## Got Ideas?

Open an issue, and let's discuss!

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
