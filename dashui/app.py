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

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "ARCS inelastic resolution"

import arcs
app.layout = arcs.build_interface(app)
arcs.build_callbacks(app)

def main():
    import sys
    if len(sys.argv)>1 and sys.argv[1] == 'debug':
        app.run_server(debug=True)
    else:
        from waitress import serve
        serve(app.server, host='0.0.0.0', port=8050)
    
if __name__ == '__main__': main()
