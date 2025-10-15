/home/ghost/cc-statement-parser/graphic_card/card.py

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

/home/ghost/cc-statement-parser/invoice/gen_invoice.py

"""Invoice generator

This shows how to use our preppy templating system and RML2PDF markup.
All of the formatting is inside invoice.prep
"""
import sys, os, datetime, json
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont
from rlextra.rml2pdf import rml2pdf
import jsondict
from rlextra.radxml.html_cleaner import cleanBlocks
from rlextra.radxml.xhtml2rml import xhtml2rml
import preppy


def bb2rml(text):
    return preppy.SafeString(xhtml2rml(cleanBlocks(bbcode.render_html(text)),ulStyle="normal_ul", olStyle="normal_ol"))

def generate_pdf(json_file_name, options):
    data = json.load(open(json_file_name))

    here = os.path.abspath(os.path.dirname('__file__'))
    output = os.path.abspath(options.output)
    if not os.path.isdir(output):
        os.makedirs(output,0o755)

    #wrap it up in something friendlier
    data = jsondict.condJSONSafe(data)

    #make a dictionary to pass into preppy as its namespace.
    #you could pass in any Python objects or variables,
    #as long as the template expressions evaluate
    ns = dict(data=data, bb2rml=bb2rml, format="long" if options.longformat else "short")

    #we usually put some standard things in the preppy namespace
    ns['DATE_GENERATED'] = datetime.date.today()
    ns['showBoundary'] = "1" if options.showBoundary else "0"

    #let it know where it is running; trivial in a script, confusing inside
    #a big web framework, may be used to compute other paths.  In Django
    #this might be relative to your project path,
    ns['RML_DIR'] = os.getcwd()     #os.path.join(settings.PROJECT_DIR, appname, 'rml')

    #we tend to keep fonts in a subdirectory.  If there won't be too many,
    #you could skip this and put them alongside the RML
    FONT_DIR = ns['FONT_DIR'] = os.path.join(ns['RML_DIR'], 'fonts')


    #directory for images, PDF backgrounds, logos etc relating to the PDF
    ns['RSRC_DIR'] = os.path.join(ns['RML_DIR'], 'resources')

    #We tell our template to use Preppy's standard quoting mechanism.
    #This means any XML characters (&, <, >) will be automatically
    #escaped within the prep file.
    template = preppy.getModule('rml/invoice.prep')
    

    #this hack will allow rmltuils functions to 'know' the default quoting mechanism
    #try:
    #   import builtins as __builtin__
    #except:
    #   import __builtin__
    #__builtin__._preppy_stdQuote = preppy.stdQuote
    rmlText = template.getOutput(ns, quoteFunc=preppy.stdQuote)

    file_name_root = os.path.join(output,os.path.splitext(os.path.basename(json_file_name))[0])
    if options.saverml:
        #It's useful in development to save the generated RML.
        #If you generate some illegal RML, pyRXP will complain
        #with the exact line number and you can look to see what
        #went wrong.  Once running, no need to save.  Within Django
        #projects we usually have a settings variable to toggle this
        #on and off.
        rml_file_name = file_name_root + '.rml'
        open(rml_file_name, 'wb').write(rmlText)
    pdf_file_name = file_name_root + '.pdf'

    #convert to PDF on disk.  If you wanted a PDF in memory,
    #you could pass a StringIO to 'outputFileName' and
    #retrieve the PDF data from it afterwards.
    rml2pdf.go(rmlText, outputFileName=pdf_file_name)
    print('saved %s' % pdf_file_name)




if __name__=='__main__':
    from optparse import OptionParser
    usage = "usage: runme.py [--long] myfile.json"
    parser = OptionParser(usage=usage)
    parser.add_option("-l", "--long",
                      action="store_true", dest="longformat", default=False,
                      help="Do long profile (rather than short)")
    parser.add_option("-r","--rml",
                      action="store_true", dest="saverml", default=False,
                      help="save a copy of the generated rml")
    parser.add_option("-s","--showb",
                      action="store_true", dest="showBoundary", default=False,
                      help="tuen on global showBoundary flag")
    parser.add_option("-o", "--output",
                      action="store", dest="output", default='output',
                      help="where to store result")

    options, args = parser.parse_args()

    if len(args) != 1:
        print(parser.usage)
    else:
        filename = args[0]
        generate_pdf(filename, options)

/home/ghost/cc-statement-parser/invoice/jsondict.py

"""Utilities for working with JSON and json-like structures - deeply nested Python dicts and lists

This lets us iterate over child nodes and access elements with a dot-notation.
"""
import sys
isPy3 = sys.version_info[0]==3
if isPy3:
    def __alt_str__(v,enc='utf8'):
        return v if isinstance(v,bytes) else v.encode(enc)
    __strTypes__ = (str,bytes)
else:
    __alt_str__ = unicode
    __strTypes__ = (str,unicode)

class MyLocals(object):
    pass
mylocals = MyLocals()

def setErrorCollect(collect):
    mylocals.error_collect = collect

setErrorCollect(False)

def errorValue(x):
    if isinstance(x,__strTypes__):
         return repr(x) if ' ' in x else x
    return 'None' if x is None else str(x)
def condJSON(v,__name__=''):
    return JSONDict(v,__name__=__name__) if isinstance(v,dict) else JSONList(v,__name__=__name__) if isinstance(v,list) else v

def condJSONSafe(v,__name__=''):
    return JSONDictSafe(v,__name__=__name__) if isinstance(v,dict) else JSONListSafe(v,__name__=__name__) if isinstance(v,list) else v

class JSONListIter(object):
    def __init__(self, lst, conv):
        self.lst = lst
        self.i = -1
        self.conv = conv

    def __iter__(self):
        return self

    def next(self):
        if self.i<len(self.lst)-1:
            self.i += 1         
            return self.conv(self.lst[self.i])
        else:
            raise StopIteration

    if isPy3:
        __next__ = next
        del next

class JSONList(list):
    def __init__(self,v,__name__=''):
        list.__init__(self,v)
        self.__name__ = __name__
    def __getitem__(self,x):
        return condJSON(list.__getitem__(self,x),__name__='%s\t%s'%(self.__name__,errorValue(x)))
    def __iter__(self):
        return JSONListIter(self,condJSON)

class JSONListSafe(JSONList):
    def __getitem__(self,x):
        __name__='%s\t%s'%(self.__name__,errorValue(x))
        try:
            return condJSONSafe(list.__getitem__(self,x),__name__=__name__)
        except:
            if mylocals.error_collect:
                mylocals.error_collect(__name__)
            return JSONStrSafe('')
    def __iter__(self):
        return JSONListIter(self,condJSONSafe)

class JSONStrSafe(str):
    def __getattr__(self, attr):
        return self
    __getitem__ = __getattr__


class JSONDict(dict):
    "Allows dotted access"
    def __new__(cls,*args,**kwds):
        __name__ = kwds.pop('__name__')
        self = dict.__new__(cls,*args,**kwds)
        self.__name__ = __name__
        return self

    def __init__(self,*args,**kwds):
        kwds.pop('__name__','')
        dict.__init__(self,*args,**kwds)

    def __getattr__(self, attr, default=None):
        if attr in self:
            return condJSON(self[attr],__name__='%s\t%s'%(self.__name__,errorValue(attr)))
        elif __alt_str__(attr) in self:
            return condJSON(self[__alt_str__(attr)],__name__='%s\t%s'%(self.__name__,errorValue(attr)))
        elif attr=='__safe__':
            return JSONDictSafe(self,__name__=self.__name__)
        else:
            raise AttributeError("No attribute or key named '%s'" % attr)

    def sorted_items(self,accept=None, reject=lambda i: i[0]=='__name__'):
        if accept or reject:
            if not accept:
                f = lambda i: not reject(i)
            elif not reject:
                f = accept
            else: #both
                f = lambda i: accept(i) and not reject(i)
            return sorted(((k,condJSON(v,__name__==k)) for k,v in self.iteritems() if f((k,v))))
        else:
            return sorted(((k,condJSON(v,__name__==k)) for k,v in self.iteritems()))

    def sorted_keys(self):
        return sorted(self.keys())

class JSONDictSafe(JSONDict):
    "Allows dotted access"
    def __getattr__(self, attr, default=None):
        if attr in self:
            return condJSONSafe(self[attr],__name__='%s\t%s'%(self.__name__,errorValue(attr)))
        elif __alt_str__(attr) in self:
            return condJSONSafe(self[__alt_str__(attr)],__name__='%s\t%s'%(self.__name__,errorValue(attr)))
        elif attr=='__safe__':
            return self
        else:
            return JSONStrSafe('')

    def __getitem__(self,x):
        __name__='%s\t%s'%(self.__name__,errorValue(x))
        try:
            return condJSONSafe(dict.__getitem__(self,x),__name__=__name__)
        except KeyError:
            if mylocals.error_collect:
                mylocals.error_collect(__name__)
            return JSONStrSafe('')

    def sorted_items(self,accept=None, reject=lambda i: i[0]=='__name__'):
        if accept or reject:
            if not accept:
                f = lambda i: not reject(i)
            elif not reject:
                f = accept
            else: #both
                f = lambda i: accept(i) and not reject(i)
            return sorted(((k,condJSONSafe(v,__name__==k)) for k,v in self.iteritems() if f((k,v))))
        else:
            return sorted(((k,condJSONSafe(v,__name__==k)) for k,v in self.iteritems()))


/home/ghost/cc-statement-parser/invoice/data/invoice.json

{
    "id": "Hgdl165-n",
    "customer_name": "Liu Young Electronics",
    "address": "14 Kings Street, Yang Region",
    "country_name": "Hong Kong",
    "manager": "Samo Haung",
    "issue_date": "21 December 2017",
    "terms": "30 days",
    "vat_number": "58641949644",
    "purchase_id": "RPLUS 10k pages",
    "subtotal": "\u00a32600.00",
    "vat_total": "\u00a3520.00",
    "total_price": "\u00a33120.00",
    "important_text": "This invoice is due within 30 days",
    "items": ["one","two","three"],
    "last_name": "Liu",
    "orders": [
        
        {
            "description": "RPTLAB PLUS",
            "price": "\u00a31300.00",
            "quantity": 1,
            "net": "\u00a31300.00",
            "vat": "20%",
            "gross": "\u00a31560.00"

        },
        {
            "description": "Initial Consultation",
            "price": "\u00a3500.00",
            "quantity": 1,
            "net": "\u00a3500.00",
            "vat": "20%",
            "gross": "\u00a3600.00"

        },
        {
            
            "description": "Live Server set up",
            "price": "\u00a3800.00",
            "quantity": 1,
            "net": "\u00a3800.00",
            "vat": "20%",
            "gross": "\u00a3960.00"

        }
    ]
    
}


Act as a proffesional backend develper and code all files in the /home/ghost/cc-statement-parser/backend which contains file and subfolders  which contains files read readme for  in depth information i have /home/ghost/cc-statement-parser/AmexCCSample.pdf , /home/ghost/cc-statement-parser/AXISCCSAMPLE.pdf , /home/ghost/cc-statement-parser/HDFCCCSAMPLE.pdf , /home/ghost/cc-statement-parser/ICICICCSAMPLE.pdf according to this files  it should extract  these details from all bank cc statement : transaction info, card variant, card
last 4 digits, billing cycle, payment due date, total balance) with name and little info and also see that 