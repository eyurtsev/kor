Welcome to Kor's documentation!
===============================

This is a half-baked prototype that "helps" you extract structured data from text using large language models (LLMs) 🧩. 

Specify the schema of what should be extracted and provide some examples. 

Kor will generate a prompt, send it to the specified LLM and parse out the output.
And you might even get results back!

So yes -- it's just another wrapper on top of LLMs with its own flavor of abstractions. 😸


Example
-------

Translate user input into structured JSON to use for an API **request**:

.. code-block:: python

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

.. code-block:: python

  chain = create_extraction_chain(llm, schema, encoder_or_encoder_class='json')
  chain.predict_and_parse(text="play songs by paul simon and led zeppelin and the doors")['data']

.. code-block:: python

  {'player': {'artist': ['paul simon', 'led zeppelin', 'the doors']}}


.. toctree::
   :maxdepth: 2
   :caption: Contents

   tutorial
   objects
   nested_objects
   untyped_objects
   apis
   validation
   document_extraction

.. toctree::
   :caption: Advanced

   type_descriptors
   api
