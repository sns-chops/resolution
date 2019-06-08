# to run, add parent directory of PyChop to PYTHONPATH
# then $ python {thisfile}
#
# Main app: http://localhost:8050/
# Download: http://localhost:8050/download?chopper_select=ARCS-100-1.5-AST&chopper_freq=600&Ei=100


import dash, flask, io
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets = ['https://codepen.io/chriddyp/pen/gzRdpr.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "DGS resolution"

# no official support from dash for mathjax
# the following only works for static html 
# mathjax = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'
# app.scripts.append_script({ 'external_url' : mathjax })

import arcs, sequoia, cncs, hyspec
tab_style=dict(margin='0em 2em')
instruments = 'arcs sequoia cncs hyspec'.split()
tabs = []
for instr in instruments:
    interface = eval(instr).build_interface(app)
    tab = dcc.Tab(label=instr.upper(), value=instr, children=html.Div([interface], style=tab_style))
    tabs.append(tab)

app.layout = html.Div([
    dcc.Tabs(tabs, vertical=True)
])

for instr in instruments:
    mod = eval(instr)
    mod.build_callbacks(app)

def main():
    import sys
    if len(sys.argv)>1 and sys.argv[1] == 'debug':
        app.run_server(debug=True)
    else:
        from waitress import serve
        serve(app.server, host='0.0.0.0', port=8050)
    
if __name__ == '__main__': main()

