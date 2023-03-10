**⚠ WARNING: Prototype with unstable API. 🚧**  

# Kor

This is a half baked prototype that "helps" you extract structured data from text using
LLMs 🧩.

Just specify the schema of what should be extracted and provide some examples.
Kor will generate a prompt, send it to the specified LLM and parse out the
output. And you might even get some nice results back.

## 💡 Ideas

Ideas of some things that could be done with Kor.

* Extract data from text: Define what information should be extracted from a segment
* Convert an HTML form into a Kor form and allow the user to fill it out using natural language. (Convert HTML forms -> API? Or not.)
* Add some skills to an AI assistant

## 🚧 Prototype

This a prototype and the API is not expected to be stable as it hasn't been
tested against real world examples.

##  ✨ What does Kor excel at?  🌟 ✨

* Making mistakes! Plenty of them. Quality varies with the underlying language model, the quality of the prompt, and the number of bugs in the adapter code.
* Slow! It uses large prompts with examples, and works best with the larger slower LLMs.
* Crashing for long enough pieces of text! Context length window could become
  limiting when working with large forms or long text inputs.


## Potential Changes

* Adding validators
* Built-in components to quickly assemble schema with examples
* Add routing layer to select appropriate extraction schema for a use case when
  many schema exist

## 🎶 Why the name?

Fast to type and sufficiently unique.
