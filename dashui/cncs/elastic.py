import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask, io
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

import numpy as np
from . import model as cncsmodel, exp


chopper_modes = [
    'High Resolution',
    'Intermediate',
    'High Intensity',
]

# interface
def build_interface(app):
    # select chopper mode
    chopper_mode = dcc.Dropdown(
        id='cncs_chopper_mode',
        value='High Resolution',
        options = [dict(label=str(_), value=_) for _ in chopper_modes],
    )
    return html.Div(children=[
        html.Div([
            dcc.Graph(
                id='cncs-flux_vs_fwhm',
            ),
        ], style=dict(width="50em")),
    ])


def sorted_xy_byx(x,y):
    s = np.argsort(x)
    return np.array(x)[s], np.array(y)[s]

def getFWHM_vs_Ei(chopper_mode):
    x,y = sorted_xy_byx(expdata_highres.Ei_list, expdata_highres.FWHM)
    ax[0].loglog(x,y, '+-', label='HighRes')
    instrument.setChopper('High Resolution')
    y_pychop = [instrument.getResFlux(Etrans=0, Ei_in=_, frequency=180.)[0][0] for _ in x]


def build_callbacks(app):
    return
    @app.callback(
        [dd.Output(component_id='cncs-flux_vs_fwhm', component_property='figure'),
        ],
        [dd.Input('cncs_chopper_mode', 'value'),
        ],
    )
    def update_figure(chopper):
        data = [
            getFlux_vs_FWHMdata(exp.alldata, Ei, 'High resolution', 0),
            getFlux_vs_FWHMdata(exp.alldata, Ei, 'High flux', 1),
        ]
        return {
            'data': data,
            'layout': dict(
                title = 'Flux vs resolution',
                xaxis=dict(
                    title='FWHM (meV)',
                    showspikes=True,
                ),
                yaxis=dict(
                    title='Flux (counts/s/cm^2/MW)',
                    showspikes=True,
                ),
            ),
        },
    return
