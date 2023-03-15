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

  from langchain import ChatOpenAI
  from kor.extraction import Extractor
  from kor.nodes import Object, Text

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

.. code-block:: python

  model("can you play all the songs from paul simon and led zepplin", schema)

.. code-block:: python

  {'player': [{'artist': ['paul simon', 'led zepplin']}]}


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial
   prompt_examples 
   objects
   apis

