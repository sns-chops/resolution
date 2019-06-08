import os, sys
here = os.path.abspath(os.path.dirname(__file__))

# data
import resolution_plot
fc1data = resolution_plot.ExpData(os.path.join(here, '../../ARCS//V_Cali_Int_Res_FC1_2018_v2.dat'))
fc2data = resolution_plot.ExpData(os.path.join(here, '../../ARCS/V_Cali_Int_Res_FC2_2018_v2.dat'))
fc1_highres_data = resolution_plot.ExpData(os.path.join(here, '../../ARCS/V_Cali_Int_Res_FC1_HighRes_2018_v2.dat'))
vscatt_scale = 2.6e4
vscatt_scale *=60./1.4
vscatt_scale *= 1.5/2
fc1data.intensity *= vscatt_scale
fc2data.intensity *= vscatt_scale
fc1_highres_data.intensity *= vscatt_scale

data = {
    'ARCS-700-1.5-AST': fc1data,
    'ARCS-100-1.5-AST': fc2data,
    'ARCS-700-0.5-AST': fc1_highres_data,
}
