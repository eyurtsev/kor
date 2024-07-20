.. _api:

.. currentmodule:: kor


API
----------

The main **Kor** API is shown here:


.. autosummary::

  create_extraction_chain
  from_pydantic


Schema
======

Kor has its own internal representation of a schema. The schema
is pretty minimal and does not do much except for helping to produce
type descriptions for the prompts.

Instead of using the internal representation it may be more convenient
to use **from_pydantic** to convert a pydantic schema into internal
representation automatically.

.. note::
  It may be that the internal schema will be removed in the future in favor
  of just using pydantic schema.

.. autosummary::

    Object
    Text
    Number
    Bool
    Selection
    Option


Encoders
========

Encoders are used to specify how we want the extracted content to be 
encoded. At the moment, JSONEncoder is the most flexible, the CSVEncoder
may be the most accurate, while the XMLEncoder may be neither.

**create_extraction_chain** accepts an encoder as named argument allowing
a user to provide their own custom way to encode the input.

.. autosummary::

  JSONEncoder
  CSVEncoder 
  XMLEncoder 

Base class: 

.. autosummary::

  encoders.Encoder
  encoders.SchemaBasedEncoder

TypeDescriptors
================

.. autosummary::

  TypeScriptDescriptor
  BulletPointDescriptor


Base class: 

.. autosummary::

  TypeDescriptor


Index
=====

.. automodule:: generated.kor

