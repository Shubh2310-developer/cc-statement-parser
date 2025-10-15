# Long Document tutorial

The following tutorial is made to demonstrate an example of what the setup for generating a long pdf document using prep
files may look like.

It does so by parsing documents from the Internet Classics Archive. http://classics.mit.edu.

## Running

    cd long_document
    python -m venv .
    . bin/activate
    pip install -r requirements.txt

An example way you may run the command is as below:

    python generate_long_document.py odyssey.mb.txt

Should the filename be missing it will default to using the art of war document in the `documents/` directory.

## What are the components?

- `documents/` the text files we parse. Following the exact same structure. Art of war needed minor adjustments to match.
- `fonts/` the fonts used in the templates file.
- `generate_long_document.py` used to parse the Internet Classics Archive text files.
- `longdocument.prep` the template in which the parsed in data is loaded into. Represents the pdf structure.

## What does this demonstrate?

How simple it is to set up a basic .py file to work with .prep templates. The small `main()` method is all that's needed
to actually work with the actual prep file. We also have the `load_document()` method which gives us a data structure
to pass into the namespace and call and use from within our template file

