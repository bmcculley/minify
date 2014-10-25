#!/bin/python
import sys, re

def cssMinify(css, saveFileName):
    # remove comments - this will break a lot of hacks :-P
    css = re.sub( r'\s*/\*\s*\*/', "$$HACK1$$", css ) # preserve IE<6 comment hack
    css = re.sub( r'/\*[\s\S]*?\*/', "", css )
    css = css.replace( "$$HACK1$$", '/**/' ) # preserve IE<6 comment hack

    # url() doesn't need quotes
    css = re.sub( r'url\((["\'])([^)]*)\1\)', r'url(\2)', css )

    # spaces may be safely collapsed as generated content will collapse them anyway
    css = re.sub( r'\s+', ' ', css )

    # shorten collapsable colors: #aabbcc to #abc
    css = re.sub( r'#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)', r'#\1\2\3\4', css )

    # fragment values can loose zeros
    css = re.sub( r':\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;', r':\1;', css )

    returnVal = ""
    for rule in re.findall( r'([^{]+){([^}]*)}', css ):

        # we don't need spaces around operators
        selectors = [re.sub( r'(?<=[\[\(>+=])\s+|\s+(?=[=~^$*|>+\]\)])', r'', selector.strip() ) for selector in rule[0].split( ',' )]

        # order is important, but we still want to discard repetitions
        properties = {}
        porder = []
        for prop in re.findall( '(.*?):(.*?)(;|$)', rule[1] ):
            key = prop[0].strip().lower()
            if key not in porder: porder.append( key )
            properties[ key ] = prop[1].strip()

        # output rule if it contains any declarations
        if properties:
            f = open(saveFileName,'a')
            f.write( "%s{%s}" % ( ','.join( selectors ), ''.join(['%s:%s;' % (key, properties[key]) for key in porder])[:-1] ) )
            f.close()
            #returnVal = returnVal + "%s{%s}" % ( ','.join( selectors ), ''.join(['%s:%s;' % (key, properties[key]) for key in porder])[:-1] )
    #return returnVal

def fileMin(ifile):
    returnVal = ''
    ifSplit = ifile.split('.')
    for n, filePart in enumerate(ifSplit):
        if n == len(ifSplit)-1:
            returnVal = returnVal + "min."
        returnVal = returnVal + filePart
        if n != len(ifSplit)-1:
            returnVal =returnVal + "."
    return returnVal

css = ""
files = []
saveFileName = "style.min.css"
flag = False
sepFlag = False
for n, i in enumerate(sys.argv):
    if n == 0:
        pass
    elif i in ("-h", "--help"):
        print "Add CSS files space separated to be combined and minified. \n \
                    \t-h, --help \n \
                    \t\tDisplay this help message. \n \
                    \t-o, --output \n \
                    \t\tDeclare name of output CSS file. \n \
                    \t-s, --separate \n \
                    \t\tOutput each individual file as min. ex: \n \
                    \t\tstyle.css will become style.min.css"
        break
    elif i in ("-o", "--output"):
        flag = True
    elif i in ("-s", "--separate"):
        sepFlag = True
    elif flag:
        saveFileName = i
        flag = False
    elif sepFlag:
        files.append(i)
    else:
        css = css + open( i, 'r' ).read()

if sepFlag:
    for cssFile in files:
        css = open(cssFile, 'r').read()
        cssFile = fileMin(cssFile)
        cssMinify(css, cssFile)
else:
    cssMinify(css, saveFileName)