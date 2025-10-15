# File Structure

## /home/ghost/cc-statement-parser/graphic_card
```
graphic_card/
├── card.py
├── README.txt
└── requirements.txt
```

## /home/ghost/cc-statement-parser/invoice
```
invoice/
├── 00README
├── data/
│   └── invoice.json
├── gen_invoice.py
├── jsondict.py
├── requirements.txt
└── rml/
    ├── invoice.prep
    └── rl_letterhead_201203.pdf
```

## /home/ghost/cc-statement-parser/long_document
```
long_document/
├── documents/
│   ├── artwar.1b.txt
│   ├── fab.mb.txt
│   ├── metaphysics.mb.txt
│   ├── odyssey.mb.txt
│   └── republic.mb.txt
├── fonts/
│   ├── Carlito-Bold.ttf
│   └── Carlito-Regular.ttf
├── generate_long_document.py
├── longdocument.prep
├── README.md
└── requirements.txt
```

## /home/ghost/cc-statement-parser/cc_generator
```
cc_generator/
├── components/
│   ├── __init__.py
│   └── base_component.py
├── data/
│   └── samples/
│       ├── amex_sample.json
│       ├── axis_sample.json
│       ├── hdfc_sample.json
│       ├── icici_sample.json
│       └── sbi_sample.json
├── generators/
│   ├── __init__.py
│   ├── amex_generator.py
│   ├── axis_generator.py
│   ├── base_generator.py
│   ├── hdfc_generator.py
│   ├── icici_generator.py
│   └── sbi_generator.py
├── output/
│   ├── amex/
│   │   └── amex_statement.pdf
│   ├── axis/
│   │   └── axis_statement.pdf
│   ├── hdfc/
│   │   └── hdfc_statement.pdf
│   ├── icici/
│   │   └── icici_statement.pdf
│   └── sbi/
│       └── sbi_statement.pdf
├── utils/
│   ├── __init__.py
│   ├── colors.py
│   ├── formatters.py
│   └── styles.py
├── config.py
├── generate_all.sh
├── main_generator.py
├── QUICKSTART.md
├── README.md
└── requirements.txt
```
