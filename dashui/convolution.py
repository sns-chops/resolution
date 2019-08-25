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

    """provide methods to

    * create UI skeleton
    * update UI elements (to be used in callback functions)
    """

    def __init__(self, instrument='arcs', instrument_params=[], res_function_calculator=None):
        self.instrument = instrument
        self.instrument_params = instrument_params
        self.res_function_calculator = res_function_calculator
        # IDs
        self.tabs_id = '%s-convolution-tabs' % self.instrument
        # I(E)
        self.upload_widget_id = '%s-convolution-upload' % instrument
        self.plot_widget_id = '%s-convolution-plot' % instrument
        self.conv_example_id = "%s-conv-example" % self.instrument
        self.excitation_input_id = "%s-excitation-input" % self.instrument
        self.excitation_input_status_id = '%s-excitation-input-status' % self.instrument
        self.conv_example_plots_id = '%s-conv-example-plots' % self.instrument
        self.apply_excitations_button_id = '%s-apply-excitations' % self.instrument
        # I(Q,E)
        self.qgrid_dim_input_id = '%s-iqe-qgrid-dim-input' % self.instrument
        self.Nqsamples = '%s-iqe-qsample-input' % self.instrument
        self.phonopy_upload_widget_id = '%s-convolution-phonopy-upload' % instrument
        self.IQE_plot_widget_Id = '%s-convolution-IQE-plot' % instrument
        # 
        self.tab_style = dict(border="1px solid lightgray", padding='1em')
        return

    def createInterface(self, app):
        return html.Div([
            dcc.Tabs(id=self.tabs_id, children=[
                dcc.Tab(label='I(E)', children=[self.createIEInterface(app)], value='I(E)'),
                dcc.Tab(label='I(Q,E)', children=[self.createIQEInterface(app)], value='I(Q,E)'),
            ], value='I(E)', vertical=True)
        ], style=dict(border="1px solid lightgray", padding='1em'))

    def createIQEInterface(self, app):
        style = self.tab_style.copy()
        style['width'] = "60em"
        return html.Div([
            html.Div([
                html.H5('Powder I(Q,E) spectrum'),
                html.A("Example phonopy input file",
                       href="https://raw.githubusercontent.com/sns-chops/resolution/1e76dda84c5c4a356ba9806a8728c449fd77fa0f/dashui/data/graphite-DFT-DOS.dat",
                       target="_blank"),
                html.Label('Number of Q grid points along one dimension within 1BZ'),
                dcc.Input(id=self.qgrid_dim_input_id, type='number', value=31, max=51, min=11),
                html.Label('Number of Q samples'),
                dcc.Input(id=self.Nqsamples, type='number', value=1e5, min=1e4, max=1e6),
                convolution_panel(self.phonopy_upload_widget_id, self.IQE_plot_widget_Id, 'DFT FORCE_CONSTANTS'), 
            ], style = style)
        ])

    def createIEInterface(self, app):
        style = self.tab_style.copy()
        style['width'] = "60em"
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
                convolution_panel(self.upload_widget_id, self.plot_widget_id, "Energy spectrum"), # convolution
            ], style = style)
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
        mask = E<Ei*0.9
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
    
    # panel for excitations and plots
    def createExamplesSkeleton(self, app):
        "example section with delta function. contains textarea for excitations and plots"
        plots = html.Div(id=self.conv_example_plots_id)
        example_panel = html.Div(
            id = self.conv_example_id,
            children = html.Div([
                self.createExcitationPanelSkeleton(),
                dcc.Loading(plots)])
        )
        return html.Details([
            html.Summary('Expand for delta function example'),
            example_panel,
        ])

    def createExcitationPanelSkeleton(self):
        instrument = self.instrument
        inputarea = dcc.Textarea(
            id = self.excitation_input_id, value="",
            style={'width': '30em', 'height': '10em', 'margin-top': "1em"}
        )
        inputarea_container = html.Div([inputarea], style={'display': 'inline-flex'})
        status = html.Div(
            id=self.excitation_input_status_id,
            children=[],
            style=dict(padding='1em', color='red')
        )
        apply_button = html.Button('Apply', id = self.apply_excitations_button_id)
        right = html.Div(
            children = [apply_button, status],
            style=dict(display='inline-flex', margin ='1em')
        )
        return html.Details([
            html.Summary('Edit excitations'),
            html.Div(children=[inputarea_container, right]),
        ], style={'margin': '1em'})

    def updateExamplePanel(self, excitations_text, Ei, *args):
        """update the example panel. this includes the text area of excitations, and the plots

        * excitations_text: textarea text for excitations
        * Ei
        * *args: additional args for convolution

        Output: the textarea value, textarea status, the plots
        """
        error = False
        status = ""
        if not excitations_text.strip():
            excitations = np.linspace(-.45*Ei, Ei*.9, 8), np.ones(8)
            header = '# current configuration. type to change\n# COL1: energy(meV)\tCOL2: intensity\n'
            excitations_text = header + '\n'.join(['%8.3f\t%8.3f' % (e,I) for e, I in zip(*excitations)])
        else:
            try:
                excitations = excitations_text.strip().splitlines()
                excitations = [map(float, e.split()) for e in excitations if e.strip()]
                excitations = np.array(excitations).T
                assert excitations.shape[0] == 2, "Has to be 2 col ascii"
                excitations = excitations[0], excitations[1]
            except Exception as e:
                status = str(e)
                error = True
        if not error:
            E, I = IE_from_excitations(excitations, -.5*Ei, Ei*.95, 100)
            cE, cI = self.convolve((E,I), Ei, *args)
            plots = html.Div([IEplot((E,I), "Original"), IEplot((cE,cI), "Convolved")])
        else:
            plots = ''
        return excitations_text, status, plots

    def updateSQEConvolution(
            self, uploaded_contents, uploaded_filename,
            qgrid_dim, Nqsamples,
            Ei, *args):
        if uploaded_contents is None: return
        zipfile = binfile_from_uploaded(uploaded_contents, uploaded_filename)
        # compute sqe
        Eaxis = np.linspace(-.2*Ei, .9*Ei, 110)
        from mcni.utils import conversion
        Qmax = conversion.e2k(Ei)*2
        Qaxis = np.linspace(0, Qmax, 100)
        from phonon import SQE_from_FCzip
        sqe = SQE_from_FCzip(Qaxis, Eaxis, zipfile, Ei, max_det_angle=140., T=300., qgrid_dim=qgrid_dim, Nqpoints=Nqsamples)
        os.unlink(zipfile)
        # plot sqe
        import plotly.graph_objs as go
        fig = go.Figure(
            data=[go.Heatmap(
                z=sqe.I.T,
                x=sqe.Q,
                y=sqe.E,
                colorscale='Viridis')],
            layout = {
                'title': 'Original',
            }
        )
        # convolve
        E_new, Q, I_new = self.convolveSQE(sqe, Ei, *args)
        fig2 = go.Figure(
            data=[go.Heatmap(
                z=I_new.T,
                x=Q,
                y=E_new,
                colorscale='Viridis')],
            layout = {
                'title': 'Convolved',
            }
        )
        graph_style ={'height': '25em', 'width': '30em'}
        inline = {"display": "inline-flex"}
        return html.Div([
            html.Div([dcc.Graph(figure=fig, style=graph_style)], style=inline),
            html.Div([dcc.Graph(figure=fig2, style=graph_style)], style=inline),
        ], style = {"display": "inline-flex"})

    # utils
    def convolveSQE(self, IQE, *args):
        a = self.calc_res_a(*args)
        E_new, Q, I_new = convolveSQE(a, IQE)
        return E_new, Q, I_new
    
    def convolve(self, IE, *args):
        a = self.calc_res_a(*args)
        # convolve
        E, I = IE
        E2, I2 = convolve(a, E, I)
        return E2, I2

    def calc_res_a(self, *args):
        # get resolution function
        E1, res = self.res_function_calculator(*args)
        if np.any(res!=res):
            raise RuntimeError("invalid resolution function")
        # fit
        order = 3
        return np.polyfit(E1, res, order)
    
def IE_from_excitations(excitations, Emin, Emax, N):
    """Create I(E) curve from a bunch of excitations

    Inputs
    * Emin, Emax, N: define energy axis of output
    * excitations is a tuple of Es and Is. excitation is assumed to be with no intrinsic width
      - Es: a list of energies of excitations
      - Is: a list of intensities of excitations

    Output: (E,I)
    """
    E = np.linspace(Emin,Emax,N)
    dE = E[1]-E[0]
    I = np.zeros(E.size)
    # set delta functions
    for E1,I1 in zip(*excitations):
        condition = np.abs(E-E1)<0.50000001*dE
        I[condition] = I1
    return E,I


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
    


def convolution_panel(upload_widget_id, plot_widget_id, filetype):
    return html.Div([
        # plot
        dcc.Loading(
            html.Div(id=plot_widget_id, style=dict(
                width="40em", margin='.3em', display="inline-flex",
            ))
        ),
        html.Div(
            dcc.Upload(
                id=upload_widget_id,
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select a file'),
                    ' for ', filetype,
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
    E_new, FWHM_f, psf = makePSF(a, E)
    ys = []
    FWHM0 = FWHM_f(E[0])
    FWHM1 = FWHM_f(E[-1])
    smaller_range = (E_new>E[0]-FWHM0) * (E_new<E[-1]+FWHM1)
    I_new = np.interp(E_new, E, I)
    I_new[E_new<E[0]] = 0; I_new[E_new>E[-1]] = 0
    # convolve
    y = np.dot(psf, I_new)
    return E_new[smaller_range], y[smaller_range]

def convolveSQE(a, SQE):
    E = SQE.E; Q = SQE.Q
    Is = SQE.I.copy()
    mask = Is!=Is
    Is[Is!=Is] = 0
    E_new, I_new_list = convolve_spectra(a, E, Is)
    return E_new, Q, np.array(I_new_list)

def convolve_spectra(a, E, Is):
    '''a: polynomial coeffs
    E: input energy axis
    Is: a list of spectra
    '''
    E_new, FWHM_f, psf = makePSF(a, E)
    ys = []
    FWHM0 = FWHM_f(E[0])
    FWHM1 = FWHM_f(E[-1])
    smaller_range = (E_new>E[0]-FWHM0) * (E_new<E[-1]+FWHM1)
    for i, I in enumerate(Is):
        I_new = np.interp(E_new, E, I)
        I_new[E_new<E[0]] = 0; I_new[E_new>E[-1]] = 0
        # convolve
        y = np.dot(psf, I_new)
        y = y[smaller_range]
        ys.append(y)
        continue
    return E_new[smaller_range], ys


def makePSF(a, E):
    """make PSF matrix

    a: polnomial fit for FWHM
    E: energy axis
    """
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
    return E_new, FWHM_f, psf


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

def binfile_from_uploaded(uploaded_contents, uploaded_filename):
    content_type, content_string = uploaded_contents.split(',')
    import base64; decoded = base64.b64decode(content_string)
    import tempfile
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, uploaded_filename)
    f = open(path, 'w')
    f.write(decoded)
    f.close()
    # print path
    return path
