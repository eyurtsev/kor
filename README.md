**⚠ WARNING: Prototype with unstable API. 🚧**  

# Kor

Kor is a prototype to see if it's easy to introduce a few building blocks 🧩 to make it faster to extract structured information with an LLM. 

At the moment, Kor supports a single input form and does one pass interaction.

## 💡 What could one do?

* Use with a virtual assistant to help specify to the assistant precisely what information must be collected from the user. 
* Create a form that specifies which information needs to be extracted from a segment of text. Main limitation: length of context window if the form is long. This may require a first filtering pass on the text if the source text is long to identify potentially relevant segments.
* Read an HTML page online, and convert a form input on it into a Kor form, allowing a user to fill out an online form using natural language.
* Add an automaton that has multiple states, each state with its own form and an ability to execute forms, and transition between states based on user input. If the number of states grows to be large, one must apply a pre-f [HERE]

## 🦺 Limitations 

Extraction is expected to contain frequent errors. 
Quality depends on quality of underlying model and to an extent the quality of the prompt.

## 🎶 Why the name?

It's fast to type and looks unique enough

