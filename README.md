**⚠ WARNING: Prototype with unstable API. 🚧**  

# Kor

Kor helps developers leverage LLMs for structured data extraction.

Kor introduces an inputs API (to resemble HTML form inputs) as building blocks 🧩.

At the moment, Kor supports a single input form and does one pass interaction. 


## 💡 What could one do?

* Build a virtual assistant: define what information needs to be collected from a user. 
* Extract data from text: Define what information should be extracted from a segment.
* Convert an HTML form into a Kor form 
* Read an HTML page online, and convert a form input on it into a Kor form, allowing a user to fill out an online form using natural language.
* Add an automaton that has multiple states, each state with its own form and an ability to execute forms, and transition between states based on user input. If the number of states grows to be large,  a filtering step will be required first followed by dynamically constructing an appropriate prompt.

## 🚧 Prototype

A prototype created in less than 20 hours, the API is not expected to be stable
as it hasn't been used against enough real world examples.

## 🦺 Limitations 

* Extraction is not perfect. Quality depends on the language model and the quality of the prompt.
* May be slow if underlying language model is slow (i.e., a few seconds).
* Length context window could become limiting when working with large forms or long text inputs.


## Expected changes

* Improve type information for Object inputs.
* 


## 🎶 Why the name?

Fast to type and sufficiently unique
