import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

import numpy as np
from . import model as sequoiamodel, exp
import widget_utils as wu

# chopper freqs
chopper_freqs = range(60, 601, 60)
chopper_freq_opts = [dict(label=str(f), value=f) for f in chopper_freqs]

# select Ei
Ei_widget_elements = [
    html.Label('Incident energy (meV)'),
    dcc.Input(id='sequoia_Ei_input', type='number', value=80.),
]

# select FC
FC_widget_elements = [
    html.Label('Fermi Chopper'),
    dcc.Dropdown(
        id='sequoia_chopper_select',
        options = [
            dict(label='High Resolutionn', value='High-Resolution'),
            dict(label='High Flux', value='High-Flux'),
        ],
        value = 'High-Resolution',
    ),
    #
    html.Label('Fermi chopper frequency'),
    dcc.Dropdown(id='sequoia_chopper_freq', value=600, options=chopper_freq_opts),
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
        html.Div([html.Button('Calculate', id='sequoia-calculate-button')], style=dict(padding='1em')),
        # status
        html.Div(id='sequoia-status', children='', style=dict(padding='1em', color='red')),

        # summary
        html.Details([
            html.Summary('Summary'),
            dcc.Markdown('', id='sequoia-summary'),
        ]),

        # formula
        html.Details([
            html.Summary("Polynomial fit for the energy-transfer (x) dependence of resolution (FWHM)"),
            html.Div(id='sequoia-pychop-polyfit-python-formula'),
            html.Div(id='sequoia-pychop-polyfit-matlab-formula'),
        ]),

        # plot
        html.Div([
            dcc.Graph(
                id='sequoia-res_vs_E',
            ),
        ], style=dict(width="40em", margin='.3em')),

        # download button
        html.A(html.Button('Download'), id='sequoia-download-link'),

    ])


def build_callbacks(app):
    @app.callback(
        [dd.Output(component_id='sequoia-res_vs_E', component_property='figure'),
         dd.Output(component_id='sequoia-status', component_property='children'),
         dd.Output('sequoia-download-link', 'href'),
         dd.Output('sequoia-summary', 'children'),
         dd.Output('sequoia-pychop-polyfit-python-formula', 'children'),
         dd.Output('sequoia-pychop-polyfit-matlab-formula', 'children'),
        ],
        [dd.Input('sequoia-calculate-button', 'n_clicks'),
         ],
        [
         dd.State(component_id='sequoia_chopper_select', component_property='value'),
         dd.State(component_id='sequoia_chopper_freq', component_property='value'),
         dd.State(component_id='sequoia_Ei_input', component_property='value'),
        ]
        )
    def update_output_div(n_clicks, chopper_select, chopper_freq, Ei):
        # print(n_clicks, chopper_select, Ei)
        try:
            E, res = get_data(chopper_select, chopper_freq, Ei)
        except Exception as e:
            status = str(e)
            curve = {}
            downloadlink = ''
            summary = ''
            python_formula = ''
            matlab_formula = ''
        else:
            order = 3
            yfit, python_formula, matlab_formula = wu.polyfit(E, res, order)
            curve = {
                'data': [
                    {'x': E, 'y': res, 'type': 'point', 'name': 'resolution'},
                    {'x': E, 'y': yfit, 'type': 'lines', 'name': 'resolution polynomial fit'},
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
                downloadlink = '/download/sequoia?chopper_select=%s&chopper_freq=%s&Ei=%s' % (
                    chopper_select, chopper_freq, Ei)
                elastic_res,flux = sequoiamodel.elastic_res_flux(
                    chopper=chopper_select, chopper_freq=chopper_freq, Ei=Ei)
                # data = exp.data[chopper_select]
                # indexes = (np.where(np.isclose(data.vdata.Energy, Ei)))[0]
                #if len(indexes):
                #    index = indexes[0]
                #    # print(data.FWHM[index])
                #    flux = '%g (PyChop); %g (Experiment)' % (flux, data.intensity[index])
                #else:
                #    flux = '%g (PyChop)' % flux
                summary = summary_format_str.format(
                    el_res=elastic_res, el_res_percentage=elastic_res/Ei*100., Ei=Ei, flux=flux)
        return curve, status, downloadlink, summary, python_formula, matlab_formula

    @app.server.route('/download/sequoia')
    def sequoia_download_csv():
        d = {}
        keys = ['chopper_select', 'chopper_freq', 'Ei']
        for k in keys:
            value = flask.request.args.get(k)
            try: value = float(value)
            except: pass
            d[k] = value
        E, res = get_data(**d)
        filename = "sequoia_res_{chopper_select}_Ei_{Ei}.csv".format(**d)
        return wu.send_file(np.array([E,res]).T, filename)

    return

summary_format_str = '''
* Incident energy: {Ei} meV
* Elastic resolution: {el_res:.3f} meV
* Elastic resolution percentage: {el_res_percentage:.2f}%
* Flux: {flux:.3g} counts/s/cm^2/MW
'''
# * Flux: {flux} counts/s/cm^2/MW

def get_data(chopper_select, chopper_freq, Ei):
    E = np.linspace(-Ei, Ei*.95, 100)
    res = sequoiamodel.res_vs_E(E, chopper=chopper_select, chopper_freq=chopper_freq, Ei=Ei)
    return E, res
