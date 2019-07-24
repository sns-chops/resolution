import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import dash, flask
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd

import numpy as np
import widget_utils as wu


def create(instrument='arcs', instrument_params=[], res_function_calculator=None):
    "return interface builder and callback builder"
    upload_widget_id = '%s-convolution-upload' % instrument
    plot_widget_id = '%s-convolution-plot' % instrument
    def interface_builder(app):
        return convolution_panel(upload_widget_id, plot_widget_id)
    def callback_builder(app):
        return build_callbacks(app, upload_widget_id, plot_widget_id, instrument_params, res_function_calculator)
    return interface_builder, callback_builder


def convolution_panel(upload_widget_id, plot_widget_id):
    return html.Div([
        html.Details([
            html.Summary('Convolution'),
            html.Div("Upload a 2-col ascii file for the I vs E curve, and calculate the curve with instrument broadening"),
            ]),
        
        dcc.Upload(
            id=upload_widget_id,
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
        html.Div(id=plot_widget_id, style=dict(width="40em", margin='.3em')),
    ])

def build_callbacks(app, upload_widget_id, plot_widget_id, instrument_params, res_function_calculator):
    # convolution
    inputs = [
        dd.State(upload_widget_id, 'filename'),
        dd.State(upload_widget_id, 'last_modified')
    ] + instrument_params
    @app.callback(dd.Output(plot_widget_id, component_property='children'),
                  [dd.Input(upload_widget_id, 'contents')],
                  inputs)
    def handle_convolution_upload(uploaded_contents, uploaded_filename, uploaded_last_modified, *args):
        if uploaded_contents is None: return []
        # load data
        try:
            E, I = dataarr_from_uploaded_ascii(uploaded_contents).T
        except Exception as e:
            return [html.P("Failed to load %s as 2-col ascii" % uploaded_filename,
                           style={'color': 'red', 'fontSize': 12})]
            import traceback as tb
            return [html.Pre(tb.format_exc(), style={'color': 'red', 'fontSize': 14})]
        if len(E)>500:
            return [html.P("Too many data points: %s" % len(E),
                           style={'color': 'red', 'fontSize': 12})]
        # get resolution function
        E1, res = res_function_calculator(*args)
        # fit
        order = 3
        a = np.polyfit(E1, res, order)
        # convolve
        E2, I2 = convolve(a, E, I)
        # plot
        curve = {
            'data': [
                {'x': E, 'y': I, 'type': 'point', 'name': 'Without resolution'},
                {'x': E2, 'y': I2, 'type': 'point', 'name': 'Convolved'},
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

def convolve(a, E, I):
    '''a: polynomial coeffs
    E,I: input spectrum
    '''
    order = len(a)-1
    # get FWHM for each point in the input E array
    FWHM_f = lambda E: sum( a[i]*E**(order-i) for i in range(order+1) )
    FWHM0 = FWHM_f(E[0])
    FWHM1 = FWHM_f(E[-1])
    dE = np.mean(E[1:] - E[:-1])
    # expand the range
    E0 = E[0] - FWHM0*5
    E1 = E[-1] + FWHM1*5
    E_new = np.arange(E0, E1, dE)
    # fwhm
    FWHM = FWHM_f(E_new)
    # matrix
    N = len(E_new)
    psf = np.zeros((N,N))
    for i, (E1, fwhm1) in enumerate(zip(E_new, FWHM)):
        psf[i] = gaussian(E_new - E1, fwhm1/2.355) * dE
        continue
    I_new = np.interp(E_new, E, I)
    I_new[E_new<E[0]] = 0; I_new[E_new>E[-1]] = 0
    # convolve
    y = np.dot(psf, I_new)
    return E_new, y


def gaussian(x, sigma):
    sigma2 = sigma*sigma
    return 1./np.sqrt(2.*np.pi)/sigma * np.exp(-x*x/2/sigma2)


def dataarr_from_uploaded_ascii(uploaded_contents):
    content_type, content_string = uploaded_contents.split(',')
    import base64; decoded = base64.b64decode(content_string)
    from StringIO import StringIO
    tmp = StringIO(decoded);
    return np.loadtxt(tmp)
