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
    factory = WidgetFactory(instrument, instrument_params, res_function_calculator)
    return factory.createInterface, factory.createCallbacks


class WidgetFactory:

    def __init__(self, instrument='arcs', instrument_params=[], res_function_calculator=None):
        self.instrument = instrument
        self.instrument_params = instrument_params
        self.res_function_calculator = res_function_calculator
        self.upload_widget_id = '%s-convolution-upload' % instrument
        self.plot_widget_id = '%s-convolution-plot' % instrument
        self.conv_example_id = "%s-conv-example" % self.instrument
        return

    def createInterface(self, app):
        return html.Div([
            html.Div([
                html.H5('Energy spectrum (e.g., phonon DOS)'),
                self.createExamplesSkeleton(app),  # examples
                html.Div(
                    "Upload a 2-col ascii file for the I vs E curve, and calculate the instrument-broadened curve. "
                    "The comment line should contain the unit of energy/frequency axis: meV or TeraHz",
                    style=dict(margin="1em 0"),
                ),
                html.A("Example 2-col ascii file",
                       href="https://raw.githubusercontent.com/sns-chops/resolution/1e76dda84c5c4a356ba9806a8728c449fd77fa0f/dashui/data/graphite-DFT-DOS.dat",
                       target="_blank"),
                convolution_panel(self.upload_widget_id, self.plot_widget_id), # convolution
            ], style = {"margin-top": "1em"}),
        ])

    def createPlotForUploadedData(self, uploaded_contents, uploaded_filename, uploaded_last_modified, Ei, *args):
        if uploaded_contents is None: return []
        # load data
        try:
            E, I = dataarr_from_uploaded_ascii(uploaded_contents).T
        except Exception as e:
            # return [html.P("Failed to load %s as 2-col ascii" % uploaded_filename,
            #               style={'color': 'red', 'fontSize': 12})]
            import traceback as tb
            return [html.Pre(tb.format_exc(), style={'color': 'red', 'fontSize': 14})]
        if len(E)>1000:
            return [html.P("Too many data points: %s" % len(E),
                           style={'color': 'red', 'fontSize': 12})]
        mask = E<Ei
        E1 = E[mask]; I1 = I[mask]
        E2, I2 = self.convolve((E1,I1), Ei, *args)
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
        return [dcc.Graph(figure=curve, style={'height': '25em', 'width': '50em'})]
    
    def exampleCurves(self, Ei, *args):
        print Ei, args
        E = np.linspace(-.5*Ei, Ei*.95, 100)
        I = np.zeros(E.size)
        indexes = range(5, 100, 12)
        for ind in indexes: I[ind] = 1.
        cE, cI = self.convolve((E,I), Ei, *args)
        return html.Div([IEplot((E,I), "Original"), IEplot((cE,cI), "Convolved")])

    def createExamplesSkeleton(self, app):
        plots = dcc.Loading(html.Div(id = self.conv_example_id))
        return html.Details([
            html.Summary('Example: delta functions'),
            plots,
        ])                

    def convolve(self, IE, *args):
        # get resolution function
        E1, res = self.res_function_calculator(*args)
        if np.any(res!=res):
            raise RuntimeError("invalid resolution function")
        # fit
        order = 3
        a = np.polyfit(E1, res, order)
        # convolve
        E, I = IE
        E2, I2 = convolve(a, E, I)
        return E2, I2
    


def IEplot(IE, title, display="inline-block"):
    "display two plots. left: original I(E), right: convolved I(E)"
    E, I = IE
    # plot
    curve = {
        'data': [
            {'x': E, 'y': I, 'type': 'point', 'name': 'Without resolution'},
        ],
        'layout': {
            'title': title,
            'xaxis':{
                'title':'E (meV)'
            },
            'yaxis':{
                'title':'Intensity (arb. unit)'
            },
        }
    }
    return html.Div(
        [
            dcc.Graph(figure=curve, style={'height': '25em', 'width': '30em'}),
        ],
        style = {
            'display': display
        }
    )
    


def convolution_panel(upload_widget_id, plot_widget_id):
    return html.Div([
        # plot
        dcc.Loading(
            html.Div(id=plot_widget_id, style=dict(
                width="40em", margin='.3em',
            ))
        ),
        html.Div(
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
                    'margin': '10px',
                },
                # Allow multiple files to be uploaded
            multiple=False
            ),
        ),
    ])


def convolve(a, E, I):
    '''a: polynomial coeffs
    E,I: input spectrum
    '''
    order = len(a)-1
    # get FWHM for each point in the input E array
    FWHM_f = lambda E: sum( a[i]*E**(order-i) for i in range(order+1) )
    FWHM0 = FWHM_f(E[0])
    FWHM1 = FWHM_f(E[-1])
    dE = np.mean(E[1:] - E[:-1])/5.
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
    #
    smaller_range = (E_new>E[0]-FWHM0) * (E_new<E[-1]+FWHM1)
    return E_new[smaller_range], y[smaller_range]


def gaussian(x, sigma):
    sigma2 = sigma*sigma
    return 1./np.sqrt(2.*np.pi)/sigma * np.exp(-x*x/2/sigma2)


def dataarr_from_uploaded_ascii(uploaded_contents):
    content_type, content_string = uploaded_contents.split(',')
    import base64; decoded = base64.b64decode(content_string)
    from StringIO import StringIO
    # tmp = StringIO(decoded);
    # return np.loadtxt(tmp)
    import tempfile
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(decoded)
    f.close()
    from mccomponents.sample.phonon import read_dos
    doshist = read_dos.doshist_fromascii(f.name)
    os.unlink(f.name)
    return np.array([doshist.energy, doshist.I]).T
