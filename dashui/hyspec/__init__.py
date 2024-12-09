import os, sys
here = os.path.abspath(os.path.dirname(__file__))

from dash import dcc
import dash.html as html

from . import elastic # inelastic, 

def build_interface(app):
    el_div = elastic.build_interface(app)
    el_div.style = dict(border="1px solid lightgray", padding='1em')
    return html.Div([
        html.H1(children='HYSPEC resolution'),
        html.Details([
            html.Summary('Help'),
            html.Div([
                dcc.Markdown('''
##### Data
This page displays resolution data from experimental measurements and analytical models.

* The experimental data was obtained by measuring the vanadium standard sample. 
* The modeled data was obtained from a PyChop \[1\] model.
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
                    html.A("PyChop", href="https://docs.mantidproject.org/nightly/interfaces/PyChop.html", target="_blank"),
                ]),
            ])
        ]),
        dcc.Tabs(children=[
            # dcc.Tab(label='Inelastic', children=[inel_div]),
            dcc.Tab(label='Elastic', children=[el_div]),
            ])
    ])

def build_callbacks(app):
    elastic.build_callbacks(app)
    # inelastic.build_callbacks(app)
    return
