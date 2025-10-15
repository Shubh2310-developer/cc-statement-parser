Introduction
----------------

This shows use of reportlab/graphics to make a very simple "image card", which might be used on a web page.

Diagra™ renders graphs, piecharts, scatter plots and more, associates them with data sources, and controls every visual element. Ideal for financial applications, it is widely used by fund managers to automate factsheet production.

Read more information here https://docs.reportlab.com/diagra/

Instructions
---------------
Before starting, you need to register for a Reportlab Account  here https://www.reportlab.com/accounts/register/

(You will be prompted for a username and password when installing requirements below.)

Installation
---------------
python -m venv  .
. bin/activate
pip install -r requirements.txt


Note that The above installation only allows PDF outputs

Optional Installation for png, jpg, gif outputs
----------------------------------------------------------
With 'pip install rlextra[RL_RENDERPM]


Running
---------------
After installing the requirements as mentioned above simply run:
python card.py

