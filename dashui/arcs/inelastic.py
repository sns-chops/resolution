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


instrument_params = [
    dd.State(component_id='arcs_Ei_input', component_property='value'),
    dd.State(component_id='arcs_chopper_select', component_property='value'),
    dd.State(component_id='arcs_chopper_freq', component_property='value'),
]

from .configuration_widget import chopper_freqs, chopper_freq_opts, create
config_widget = create()

#
def get_data(Ei, chopper_select, chopper_freq):
    E = np.linspace(-Ei, Ei*.95, 100)
    res = arcsmodel.res_vs_E(E, chopper=chopper_select, chopper_freq=chopper_freq, Ei=Ei)
    if np.any(res!=res):
        raise RuntimeError("Error in calculating resolution")
    return E, res

from convolution import WidgetFactory as ConvolutionWF
conv_widget_factory = ConvolutionWF(instrument='arcs', instrument_params=instrument_params, res_function_calculator=get_data)

def build_interface(app):
    tab_style = dict(border="1px solid lightgray", padding='1em')
    summary = html.Div([
        dcc.Loading(dcc.Markdown('', id='arcs-summary')),
    ], style = tab_style,
    )
    formula = html.Details([
        html.Summary("Polynomial fit for the energy-transfer (x) dependence of resolution (FWHM)"),
        html.Div(id='arcs-pychop-polyfit-python-formula'),
        html.Div(id='arcs-pychop-polyfit-matlab-formula'),
    ])
    plot = html.Div([
        dcc.Loading(dcc.Graph(
            id='arcs-res_vs_E',
        )),
    ], style=dict(width="40em", margin='.3em'))
    # download button
    download = html.A(html.Button('Download', id='download-button'), id='arcs-download-link')
    #
    plotcontainer = html.Div([formula, plot, download], style=tab_style)
    #
    conv = conv_widget_factory.createInterface(app)
    conv.style = tab_style.copy()
    conv.style['width'] = '60em'

    return html.Div(children=[

        # input fields
        config_widget,

        # calculate button
        html.Div([html.Button('Calculate', id='arcs-calculate-button')], style=dict(padding='1em')),
        # status
        html.Div(id='arcs-status', children='', style=dict(padding='1em', color='red')),

        #
        dcc.Tabs(id="arcs-inel-tabs", children=[
            dcc.Tab(label='Summary', children=[summary], style=tab_style),
            dcc.Tab(label='Plot', children=[plotcontainer], style=tab_style),
            dcc.Tab(label='Convolution', children=[conv], style=tab_style),
        ]),
    ])


def build_callbacks(app):
    @app.callback(
        [dd.Output(component_id='arcs-res_vs_E', component_property='figure'),
         dd.Output(component_id='arcs-status', component_property='children'),
         dd.Output('arcs-download-link', 'href'),
         dd.Output('arcs-summary', 'children'),
         dd.Output('arcs-pychop-polyfit-python-formula', 'children'),
         dd.Output('arcs-pychop-polyfit-matlab-formula', 'children'),
         dd.Output(conv_widget_factory.conv_example_id, component_property='children'),
         dd.Output(conv_widget_factory.plot_widget_id, component_property='children'),
        ],
        [dd.Input('arcs-calculate-button', 'n_clicks'),
         dd.Input(conv_widget_factory.upload_widget_id, 'contents'),
        ],
        [dd.State(conv_widget_factory.upload_widget_id, 'filename'),
         dd.State(conv_widget_factory.upload_widget_id, 'last_modified'),
         dd.State(component_id='arcs_chopper_select', component_property='value'),
         dd.State(component_id='arcs_chopper_freq', component_property='value'),
         dd.State(component_id='arcs_Ei_input', component_property='value'),
        ]
        )
    def update_output_div(calc_btn, uploaded_contents, uploaded_filename, uploaded_last_modified,
                          chopper_select, chopper_freq, Ei):
        try:
            E, res = get_data(Ei, chopper_select, chopper_freq)
            failed = False
        except Exception as e:
            failed = True
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
        if failed:
            examplecurves = {}
            convplot = {}
        else:
            examplecurves = conv_widget_factory.exampleCurves(Ei, chopper_select, chopper_freq),
            convplot = conv_widget_factory.createPlotForUploadedData(
                uploaded_contents, uploaded_filename, uploaded_last_modified,
                Ei, chopper_select, chopper_freq,
            )
            
        return (
            curve, status, downloadlink, summary, python_formula, matlab_formula,
            examplecurves, convplot,
        )
            

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

