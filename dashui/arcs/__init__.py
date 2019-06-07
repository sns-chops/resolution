# to run, add parent directory of PyChop to PYTHONPATH
# then $ python {thisfile}
#
# Main app: http://localhost:8050/
# Download: http://localhost:8050/download?chopper_select=ARCS-100-1.5-AST&chopper_freq=600&Ei=100

import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask, io
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

from . import inelastic, elastic

def build_interface(app):
    inel_div = inelastic.build_interface(app)
    el_div = elastic.build_interface(app)
    return html.Div([
        dcc.Tabs(id="tabs", children=[
            dcc.Tab(label='Elastic', children=[el_div]),
            dcc.Tab(label='Inelastic', children=[inel_div]),
            ])
        ])

def build_callbacks(app):
    elastic.build_callbacks(app)
    inelastic.build_callbacks(app)
    return
