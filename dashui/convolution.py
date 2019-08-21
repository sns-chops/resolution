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
        self.confirm_config_btn_id = '%s-confirm-config-button' % self.instrument
        return

    def createInterface(self, app):
        # button to confirm instrument configuration
        confirmBtn = html.Button(
            'Confirm configuration',
            id=self.confirm_config_btn_id,
            style={'margin': '.5em'}
        )
        return html.Div([
            confirmBtn, # confirm configuration
            html.Div([
                html.H5('Energy spectrum (e.g., phonon DOS)'),
                self.createExamplesSkeleton(app),  # examples
                html.Div("Upload a 2-col ascii file for the I vs E curve, and calculate the instrument-broadened curve. The comment line should contain the unit of energy/frequency axis: meV or TeraHz"),
                convolution_panel(self.upload_widget_id, self.plot_widget_id), # convolution
            ], style = {"border-top": "1px solid lightgray", "margin-top": "1em"}),
        ])

    def createCallbacks(self, app):
        upload_widget_id = self.upload_widget_id
        plot_widget_id = self.plot_widget_id
        instrument_params = self.instrument_params
        res_function_calculator = self.res_function_calculator

        # configuration
        @app.callback(
            dd.Output(self.conv_example_id, component_property='children'),
            [dd.Input(self.confirm_config_btn_id, 'n_clicks'),],
            instrument_params
        )
        def handle_confirm_instrumentconfig(btn, *args):
            return self.exampleCurves(*args)
        
        # convolution
        inputs = [
            dd.State(upload_widget_id, 'filename'),
            dd.State(upload_widget_id, 'last_modified')
        ] + instrument_params
        @app.callback(
            dd.Output(plot_widget_id, component_property='children'),
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
            if len(E)>1000:
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

    def exampleCurves(self, Ei, *args):
        print Ei, args
        E = np.linspace(-.5*Ei, Ei*.95, 100)
        I = np.zeros(E.size)
        indexes = range(5, 100, 12)
        for ind in indexes: I[ind] = 1.
        cE, cI = self.convolve((E,I), Ei, *args)
        return html.Div([IEplot((E,I), "Original"), IEplot((cE,cI), "Convolved")])

    def createExamplesSkeleton(self, app):
        plots = html.Div(id = self.conv_example_id)
        return html.Details([
            html.Summary('Examples'),
            plots,
        ])                

    def convolve(self, IE, *args):
        # get resolution function
        E1, res = self.res_function_calculator(*args)
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
            style= {
                # 'display': 'inline-block',
            }
        ),
        # plot
        html.Div(id=plot_widget_id, style=dict(
            width="40em", margin='.3em',
            #display='inline-block'
        )),
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
    tmp = StringIO(decoded);
    return np.loadtxt(tmp)
