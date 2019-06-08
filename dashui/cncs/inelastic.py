import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

import numpy as np
from . import model as cncsmodel, exp

# chopper freqs
chopper_freqs = range(120, 601, 120)
chopper_freq_opts = [dict(label=str(f), value=f) for f in chopper_freqs]

# select Ei
Ei_widget_elements = [
    html.Label('Incident energy (meV)'),
    dcc.Input(id='cncs_Ei_input', type='number', value=20.),
]

# select FC
FC_widget_elements = [
    html.Label('Chopper mode'),
    dcc.Dropdown(
        id='cncs_chopper_select',
        options = [
            dict(label='High resolution', value='High Resolution'),
            dict(label='Intermediate', value='Intermediate'),
            dict(label='High Flux', value='High Flux'),
        ],
        value = 'High Resolution',
    ),
]

def build_interface(app):
    return html.Div(children=[

        # input fields
        html.Table([
            html.Tr([
                html.Td(Ei_widget_elements),
                html.Td(FC_widget_elements, style=dict(width="14em")),
            ])
        ]),

        # calculate button
        html.Div([html.Button('Calculate', id='cncs-calculate-button')], style=dict(padding='1em')),
        # status
        html.Div(id='cncs-status', children='', style=dict(padding='1em', color='red')),

        # summary
        html.Details([
            html.Summary('Summary'),
            dcc.Markdown('', id='cncs-summary'),
        ]),

        # plot
        html.Div([
            dcc.Graph(
                id='cncs-res_vs_E',
            ),
        ], style=dict(width="40em", margin='.3em')),

        # download button
        html.A(html.Button('Download'), id='cncs-download-link'),

    ])


def build_callbacks(app):
    @app.callback(
        [dd.Output(component_id='cncs-res_vs_E', component_property='figure'),
         dd.Output(component_id='cncs-status', component_property='children'),
         dd.Output('cncs-download-link', 'href'),
         dd.Output('cncs-summary', 'children'),
        ],
        [dd.Input('cncs-calculate-button', 'n_clicks'),
         ],
        [
         dd.State(component_id='cncs_chopper_select', component_property='value'),
         dd.State(component_id='cncs_Ei_input', component_property='value'),
        ]
        )
    def update_output_div(n_clicks, chopper_select, Ei):
        print(n_clicks, chopper_select, Ei)
        try:
            E, res = get_data(chopper_select, Ei)
        except Exception as e:
            raise
            status = str(e)
            curve = {}
            downloadlink = ''
            summary = ''
        else:
            curve = {
                'data': [
                    {'x': E, 'y': res, 'type': 'point', 'name': 'resolution'},
                ],
                'layout': {
                    'title': 'Energy dependence of resolution (PyChop)',
                    'xaxis':{
                        'title':'E (meV)'
                    },
                    'yaxis':{
                        'title':'FWHM (meV)'
                    }
                }
            }
            if (res!=res).any():
                status = "No transmission"
                downloadlink = ''
                summary = ''
            else:
                status = ''
                downloadlink = '/download/cncs?chopper_select=%s&Ei=%s' % (
                    chopper_select, Ei)
                elastic_res,flux = cncsmodel.elastic_res_flux(chopper=chopper_select, Ei=Ei)
                # data = exp.data[chopper_select]
                # indexes = (np.where(np.isclose(data.vdata.Energy, Ei)))[0]
                #if len(indexes):
                #    index = indexes[0]
                #    # print(data.FWHM[index])
                #    flux = '%g (PyChop); %g (Experiment)' % (flux, data.intensity[index])
                #else:
                #    flux = '%g (PyChop)' % flux
                summary = summary_format_str.format(
                    el_res=elastic_res, el_res_percentage=elastic_res/Ei*100., Ei=Ei) #, flux=flux)
        return curve, status, downloadlink, summary

    @app.server.route('/download/cncs')
    def cncs_download_csv():
        d = {}
        keys = ['chopper_select', 'Ei']
        for k in keys:
            value = flask.request.args.get(k)
            try: value = float(value)
            except: pass
            d[k] = value
        E, res = get_data(**d)
        filename = "cncs_res_{chopper_select}_Ei_{Ei}.csv".format(**d)
        from ..widget_utils import send_file
        return send_file(np.array([E,res]).T, filename)

    return

summary_format_str = '''
* Incident energy: {Ei} meV
* Elastic resolution: {el_res:.3f} meV
* Elastic resolution percentage: {el_res_percentage:.2f}%
'''
# * Flux: {flux} counts/s/cm^2/MW

def get_data(chopper_select, Ei):
    E = np.linspace(-Ei*.2, Ei*.95, 100)
    res = cncsmodel.res_vs_E(E, chopper=chopper_select, Ei=Ei)
    return E, res
