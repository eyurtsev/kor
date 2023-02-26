**⚠ WARNING: Prototype with unstable API. 🚧**  

# Kor

Kor helps developers leverage LLMs for structured data extraction.

Kor introduces an inputs API (to resemble HTML form inputs) as building blocks 🧩.

At the moment, Kor supports a single input form and does one pass interaction. 


## 💡 Ideas

Ideas of some things that could be done with Kor.

* Extract data from text: Define what information should be extracted from a segment.
* Improve an AI assistant by defining what information should be collected from a user? (maybe not useful)
* Convert an HTML form into a Kor form and allow the user to fill it out using natural language. (May allow converting HTML forms into APIs.)

## 🚧 Prototype

A prototype created in less than 20 hours, the API is not expected to be stable
as it hasn't been used against enough real world examples.

## 🦺 Limitations 

* Extraction is not perfect. Quality depends on the language model and the quality of the prompt.
* May be slow if underlying language model is slow (i.e., a few seconds).
* Length context window could become limiting when working with large forms or long text inputs.


## Expected changes

* Improve type information for Object inputs
* Add built-in validators
* Add router that allows one to route a user input between different possible
  forms -- This may be sufficient to re-implement a full virtual assistant with
  skills

## 🎶 Why the name?

Fast to type and sufficiently unique.
