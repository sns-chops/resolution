# to run, add parent directory of PyChop to PYTHONPATH
# then $ python {thisfile}
#
# Main app: http://localhost:8050/
# Download: http://localhost:8050/download?chopper_select=ARCS-100-1.5-AST&chopper_freq=600&Ei=100

import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

import numpy as np
from . import model as arcsmodel, exp
import widget_utils as wu

# chopper freqs
chopper_freqs = range(60, 601, 60)
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

        # formula
        html.Details([
            html.Summary("Polynomial fit for the energy-transfer (x) dependence of resolution (FWHM)"),
            html.Div(id='arcs-pychop-polyfit-python-formula'),
            html.Div(id='arcs-pychop-polyfit-matlab-formula'),
        ]),

        # plot
        html.Div([
            dcc.Graph(
                id='arcs-res_vs_E',
            ),
        ], style=dict(width="40em", margin='.3em')),

        # download button
        html.A(html.Button('Download', id='download-button'), id='arcs-download-link'),

        html.Hr(),
        # convolution
        convolution_panel(),
    ])


def convolution_panel():
    return html.Div([
        html.Details([
            html.Summary('Convolution'),
            html.Div("Upload a 2-col ascii file for the I vs E curve, and calculate the curve with instrument broadening"),
            ]),
        
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a file')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=False
        ),

        # plot
        html.Div(id='arcs-uploaded-IE-wrapper', style=dict(width="40em", margin='.3em')),
        
    ])

def build_callbacks(app):
    @app.callback(
        [dd.Output(component_id='arcs-res_vs_E', component_property='figure'),
         dd.Output(component_id='arcs-status', component_property='children'),
         dd.Output('arcs-download-link', 'href'),
         dd.Output('arcs-summary', 'children'),
         dd.Output('arcs-pychop-polyfit-python-formula', 'children'),
         dd.Output('arcs-pychop-polyfit-matlab-formula', 'children'),
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
                downloadlink = '/download/arcs?chopper_select=%s&chopper_freq=%s&Ei=%s' % (
                    chopper_select, chopper_freq, Ei)
                elastic_res,flux = arcsmodel.elastic_res_flux(chopper=chopper_select, chopper_freq=chopper_freq, Ei=Ei)
                data = exp.data[chopper_select]
                indexes = (np.where(np.isclose(data.vdata.Energy, Ei) * np.isclose(data.chopper_freqs, chopper_freq)))[0]
                if len(indexes):
                    index = indexes[0]
                    # print(data.FWHM[index])
                    flux = '%.3g (PyChop); %.3g (Experiment)' % (flux, data.intensity[index])
                else:
                    flux = '%.3g (PyChop)' % flux
                summary = summary_format_str.format(
                    el_res=elastic_res, el_res_percentage=elastic_res/Ei*100., Ei=Ei, flux=flux)
        return curve, status, downloadlink, summary, python_formula, matlab_formula

    @app.server.route('/download/arcs')
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
        return wu.send_file(np.array([E,res]).T, filename)

    # convolution
    @app.callback(dd.Output('arcs-uploaded-IE-wrapper', component_property='children'),
                  [dd.Input('upload-data', 'contents')],
                  [dd.State('upload-data', 'filename'),
                   dd.State('upload-data', 'last_modified')])
    def handle_convolution_upload(uploaded_contents, uploaded_filename, uploaded_last_modified):
        if uploaded_contents is None: return []
        # load data
        try:
            E, I = dataarr_from_uploaded_ascii(uploaded_contents).T
        except Exception as e:
            return [html.P("Failed to load %s as 2-col ascii" % uploaded_filename,
                           style={'color': 'red', 'fontSize': 14})]            
            import traceback as tb
            return [html.Pre(tb.format_exc(), style={'color': 'red', 'fontSize': 14})]
        # plot
        curve = {
            'data': [
                {'x': E, 'y': I, 'type': 'point', 'name': 'Without resolution'},
            ],
            'layout': {
                'title': 'I(E) curve',
                'xaxis':{
                    'title':'E (meV)'
                },
                'yaxis':{
                    'title':'Intensity (arb. unit)'
                }
            }
        }
        return [dcc.Graph(figure=curve)]

    return


def dataarr_from_uploaded_ascii(uploaded_contents):
    content_type, content_string = uploaded_contents.split(',')
    import base64; decoded = base64.b64decode(content_string)
    from StringIO import StringIO
    tmp = StringIO(decoded);
    return np.loadtxt(tmp)
    

summary_format_str = '''
* Incident energy: {Ei} meV
* Elastic resolution: {el_res:.3f} meV
* Elastic resolution percentage: {el_res_percentage:.2f}%
* Flux: {flux} counts/s/cm^2/MW
'''

def get_data(chopper_select, chopper_freq, Ei):
    E = np.linspace(-Ei, Ei*.95, 100)
    res = arcsmodel.res_vs_E(E, chopper=chopper_select, chopper_freq=chopper_freq, Ei=Ei)
    return E, res

