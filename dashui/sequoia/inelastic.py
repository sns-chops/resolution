import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask, io
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

import numpy as np
from . import model as arcsmodel, exp

# chopper freqs
chopper_freqs = range(120, 601, 120)
chopper_freq_opts = [dict(label=str(f), value=f) for f in chopper_freqs]

# select Ei
Ei_widget_elements = [
    html.Label('Incident energy (meV)'),
    dcc.Input(id='arcs_Ei_input', type='number', value=100.),
]

# select FC
FC_widget_elements = [
    html.Label('Fermi chopper'),
    dcc.Dropdown(
        id='arcs_chopper_select',
        options = [
            dict(label='ARCS-100-1.5-AST', value='ARCS-100-1.5-AST'),
            dict(label='ARCS-700-1.5-AST', value='ARCS-700-1.5-AST'),
            dict(label='ARCS-700-0.5-AST', value='ARCS-700-0.5-AST'),
            # dict(label='ARCS-100-1.5-SMI', value='ARCS-100-1.5-SMI'),
            # dict(label='ARCS-700-1.5-SMI', value='ARCS-700-1.5-SMI'),
            #dict(label='SEQ-100-2.0-AST', value='SEQ-100-2.0-AST'),
            #dict(label='SEQ-700-3.5-AST', value='SEQ-700-3.5-AST'),
        ],
        value = 'ARCS-100-1.5-AST',
    ),

    html.Label('Fermi chopper frequency'),
    dcc.Dropdown(id='arcs_chopper_freq', value=600, options=chopper_freq_opts),
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
        html.Div([html.Button('Calculate', id='arcs-calculate-button')], style=dict(padding='1em')),
        # status
        html.Div(id='arcs-status', children='', style=dict(padding='1em', color='red')),

        # summary
        html.Details([
            html.Summary('Summary'),
            dcc.Markdown('', id='arcs-summary'),
        ]),

        # plot
        html.Div([
            dcc.Graph(
                id='arcs-res_vs_E',
            ),
        ], style=dict(width="40em", margin='.3em')),

        # download button
        html.A(html.Button('Download', id='download-button'), id='arcs-download-link'),

    ])


def build_callbacks(app):
    @app.callback(
        [dd.Output(component_id='arcs-res_vs_E', component_property='figure'),
         dd.Output(component_id='arcs-status', component_property='children'),
         dd.Output('arcs-download-link', 'href'),
         dd.Output('arcs-summary', 'children'),
        ],
        [dd.Input('arcs-calculate-button', 'n_clicks'),
         ],
        [
         dd.State(component_id='arcs_chopper_select', component_property='value'),
         dd.State(component_id='arcs_chopper_freq', component_property='value'),
         dd.State(component_id='arcs_Ei_input', component_property='value'),
        ]
        )
    def update_output_div(n_clicks, chopper_select, chopper_freq, Ei):
        try:
            E, res = get_data(chopper_select, chopper_freq, Ei)
        except Exception as e:
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
                downloadlink = '/download?chopper_select=%s&chopper_freq=%s&Ei=%s' % (
                    chopper_select, chopper_freq, Ei)
                elastic_res,flux = arcsmodel.elastic_res_flux(chopper=chopper_select, chopper_freq=chopper_freq, Ei=Ei)
                data = exp.data[chopper_select]
                indexes = (np.where(np.isclose(data.vdata.Energy, Ei) * np.isclose(data.chopper_freqs, chopper_freq)))[0]
                if len(indexes):
                    index = indexes[0]
                    # print(data.FWHM[index])
                    flux = '%g (PyChop); %g (Experiment)' % (flux, data.intensity[index])
                else:
                    flux = '%g (PyChop)' % flux
                summary = summary_format_str.format(
                    el_res=elastic_res, el_res_percentage=elastic_res/Ei*100., Ei=Ei, flux=flux)
        return curve, status, downloadlink, summary

    @app.server.route('/download')
    def download_csv():
        d = {}
        keys = ['chopper_select', 'chopper_freq', 'Ei']
        for k in keys:
            value = flask.request.args.get(k)
            try: value = float(value)
            except: pass
            d[k] = value
        E, res = get_data(**d)
        filename = "arcs_res_{chopper_select}_{chopper_freq}_Ei_{Ei}.csv".format(**d)
        return send_file(np.array([E,res]).T, filename)

    return

summary_format_str = '''
* Incident energy: {Ei} meV
* Elastic resolution: {el_res:.3f} meV
* Elastic resolution percentage: {el_res_percentage:.2f}%
* Flux: {flux} counts/s/cm^2/MW
'''

def get_data(chopper_select, chopper_freq, Ei):
    E = np.linspace(-Ei*.2, Ei*.95, 100)
    res = arcsmodel.res_vs_E(E, chopper=chopper_select, chopper_freq=chopper_freq, Ei=Ei)
    return E, res

def send_file(nparr, filename):
    str_io = io.StringIO()
    np.savetxt(str_io, nparr, delimiter=',')
    mem = io.BytesIO()
    mem.write(str_io.getvalue().encode('utf-8'))
    mem.seek(0)
    str_io.close()
    return flask.send_file(
        mem,
        mimetype='text/csv',
        attachment_filename=filename,
        as_attachment=True)

