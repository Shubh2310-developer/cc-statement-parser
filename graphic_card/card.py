import os, sys, copy

from reportlab.lib import colors
from reportlab.graphics.shapes import *


from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont

# font will be found in reportlab/fonts bundled. To be called just 'Vera' in your attributes below
registerFont(TTFont("myvera", "Vera.ttf"))



def calling_card():
    drawing = Drawing(400, 200)
    r1 = Rect(0,0,400,200,10,10)
    r1.fillColor = colors.navy
    drawing.add(r1)

    r2 = Rect(10,10,380,180,10,10)
    r2.fillColor = colors.blue
    drawing.add(r2)

    s = String(200,85,"Andy was here",
        textAnchor='middle',
        fontName='myvera',
        fontSize=24,
        fillColor=colors.white
        )
    drawing.add(s)

    lin = Line(
        75,75,325,75, 
        strokeColor=colors.white, 
        strokeLineCap=1,
        strokeWidth=10
        )
    drawing.add(lin)

    return drawing

if __name__ == '__main__':
    d = calling_card()
    d.save(formats=['pdf', 'png'], outDir=".", fnRoot="card001")
    print("saved card001.pdf/png")