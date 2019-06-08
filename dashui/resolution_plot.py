# coding: utf-8

import os, numpy as np
import pandas as pd
import scipy as sp
import plotly, plotly.plotly as py, plotly.figure_factory as ff, plotly.graph_objs as go


class ExpData:
    
    def getDataArr(self, name):
        if hasattr(self, name): return getattr(self, name)
        return getattr(self.vdata, name)


    def createPlotXY(self, Ei, x, y, extra_info={}, max_res_percentage=None, extra_condition=None):
        # print x,y
        condition = np.isclose(self.vdata.Energy, Ei)
        if max_res_percentage:
            condition = np.logical_and(condition, self.FWHM_percentages < max_res_percentage)
        if extra_condition is not None:
            condition = np.logical_and(condition, extra_condition)
        labels = [''] * condition.sum()
        for attr_name, (attr_label, format_str) in extra_info.items():
            fmt = '%s='+format_str
            for i,v in enumerate(self.getDataArr(attr_name)[condition]):
                labels[i] += fmt % (attr_label, v) + '\n'
                continue
            continue
        trace = go.Scatter(
            x = self.getDataArr(x)[condition],
            y = self.getDataArr(y)[condition],
            mode = 'markers', # 'markers+text',
            text = labels,
            textposition='top center',
            hoverinfo = 'x + y + text'
        )
        return trace



