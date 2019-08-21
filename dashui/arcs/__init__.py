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

from . import inelastic, elastic, conv

def build_interface(app):
    inel_div = inelastic.build_interface(app)
    el_div = elastic.build_interface(app)
    conv_div = conv.build_interface(app)
    inel_div.style = el_div.style = conv_div.style = dict(border="1px solid lightgray", padding='1em')
    return html.Div([
        html.H1(children='ARCS resolution'),
        html.Details([
            html.Summary('Help'),
            html.Div([
                dcc.Markdown('''
##### Data
This page displays resolution data from experimental measurements and analytical models.

* The experimental data was obtained by measuring the vanadium standard sample. 
  For more details, see \[1\] below
* The modeled data was obtained from a PyChop \[2\] model.
  The sample was assumed to be a plate of 2mm thickness and 48mm width and height.
                '''),
                dcc.Markdown('''
##### Plots
The plots below are interactive plot.ly plots.

* You can drag a rectangle to zoom in
* There are several icons near the top-right corner on each plot.ly plot as you hover your mouse on top of the plot, including an icon to zoom out
* Hover the mouse over any data point to show more information related to the data point
                '''),
                html.P([
                    "[1]", " ",
                    html.A("the ARCS elastic resolution paper", href="https://doi.org/10.1016/j.physb.2018.11.027", target="_blank"),
                    ]),
                html.P([
                    "[2]", " ",
                    html.A("PyChop", href="https://docs.mantidproject.org/nightly/interfaces/PyChop.html", target="_blank"),
                    ]),
            ])
        ]),
        dcc.Tabs(id="tabs", children=[
            dcc.Tab(label='Inelastic', children=[inel_div]),
            dcc.Tab(label='Elastic', children=[el_div]),
            dcc.Tab(label='Convolution', children=[conv_div]),
            ])
        ])

def build_callbacks(app):
    elastic.build_callbacks(app)
    inelastic.build_callbacks(app)
    conv.build_callbacks(app)
    return
