# -*- coding: utf-8 -*-
import plotly
import plotly.plotly as py
from plotly.grid_objs import Grid, Column
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
from unidecode import unidecode

plotly.tools.set_credentials_file(username='USER_NAME', api_key='API_KEY') #<--- Insert credentials

df = pd.read_csv('df.csv') #Obtained from fpl.py
df.drop(['Unnamed: 0', 'Points Bench', 'Gameweek Rank','Transfers made','Overall Rank'],axis=1,inplace=True)
#TO DO: It is probably better to adjust the code below instead of removing data from df.
df['Name_unidecoded']=df['Name'].apply(lambda x: unidecode(unicode(x,"utf-8")))
#Necessary as the gridding does not seem work with non-ASCII characters

df['Transfer Cost bubbles']=df['Transfer Cost']+10 #For visualisation

###Make the Grid
GWs_from_col = set(df['GW'])
GWs_ints = sorted(list(GWs_from_col))
GWs = [str(GW) for GW in GWs_ints]
names = [i for i in df['Name_unidecoded'].unique()]

columns = []
# make grid
for GW in GWs:
    for name in names:
        df_by_GW = df[df['GW'] == int(GW)]
        df_by_GW_and_cont = df_by_GW[df['Name_unidecoded'] == name]
        for col_name in df_by_GW_and_cont:
            column_name = '{GW}_{name}_{header}'.format(
                GW=GW, name=name, header=col_name
            )
            a_column = Column(list(df_by_GW_and_cont[col_name]), column_name)
            columns.append(a_column)

# upload grid
grid = Grid(columns)
url = py.grid_ops.upload(grid, 'fpl_grid'+str(time.time()), auto_open=False)

###Make the Figure
figure = {
    'data': [],
    'layout': {},
    'frames': [],
    'config': {'scrollzoom': True}
}

# fill in most of layout
figure['layout']['xaxis'] = {'range':[0,np.floor(df['Overall Points'].max()+100)] ,'title': 'Overall Points', 'type': 'linear', 'gridcolor': '#FFFFFF'}
figure['layout']['yaxis'] = {'range': [np.floor(df['Team Value'].min()-1), np.ceil(df['Team Value'].max()+1)], 'title': 'Team Value', 'gridcolor': '#FFFFFF'}
figure['layout']['title'] = 'Bubble size equals no. of hits'
figure['layout']['hovermode'] = 'closest'
figure['layout']['plot_bgcolor'] = 'rgb(223, 232, 243)'

#Add Slider and Sliders
figure['layout']['slider'] = {
    'args': [
        'slider.value', {
            'duration': 400,
            'ease': 'cubic-in-out'
        }
    ],
    'initialValue': '1',
    'plotlycommand': 'animate',
    'values': GWs,
    'visible': True
}

figure['layout']['updatemenus'] = [ {
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 500, 'redraw': False},
                         'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                'transition': {'duration': 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 87},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    } ]

sliders_dict = {
    'active': 0,
    'yanchor': 'top',
    'xanchor': 'left',
    'currentvalue': {
        'font': {'size': 20},
        'prefix': 'GW:',
        'visible': True,
        'xanchor': 'right'
    },
    'transition': {'duration': 300, 'easing': 'cubic-in-out'},
    'pad': {'b': 10, 't': 50},
    'len': 0.9,
    'x': 0.1,
    'y': 0,
    'steps': []
}

#Create colors (https://plot.ly/ipython-notebooks/color-scales/ may be better)
rgbs=np.linspace(0.01,1,len(names))
color_array=plt.cm.Paired(rgbs)[:,:3] #Only rgb
color_array_255=np.around(color_array*255)
colors=[]
for i in color_array_255:
    rgb_string='rgb('+str(int(i[0]))+', '+str(int(i[1]))+', '+str(int(i[2]))+')'
    colors.append(rgb_string)
player_colors = dict(zip(names, colors))

#Fill in Figure with Data and Frames
col_name_template = '{GW}_{name}_{header}'
for GW in GWs:
    frame = {'data': [], 'name': str(GW)}
    for name in names:
        data_dict = {
            'xsrc': grid.get_column_reference(col_name_template.format(
                GW=GW, name=name, header='Overall Points'
            )),
            'ysrc': grid.get_column_reference(col_name_template.format(
                GW=GW, name=name, header='Team Value'
            )),
            'mode': 'markers',
            'textsrc': grid.get_column_reference(col_name_template.format(
                GW=GW, name=name, header='Name'
                )),
            'marker': {
                'sizemode': 'diameter',
                'sizeref': 0.7, #The bubbles are sized according to this reference
                'sizesrc': grid.get_column_reference(col_name_template.format(
                    GW=GW, name=name, header='Transfer Cost bubbles'
                )),
                'color': player_colors[name]
            },
            'name': name
        }
        if int(GW)==1:
            figure['data'].append(data_dict) #Initiate the figure with GW=1 (TODO: Add GW=0)
        frame['data'].append(data_dict)

    figure['frames'].append(frame)
    slider_step = {'args': [
        [GW],
        {'frame': {'duration': 300, 'redraw': False},
         'mode': 'immediate',
       'transition': {'duration': 300}}
     ],
     'label': GW,
     'method': 'animate'}
    sliders_dict['steps'].append(slider_step)

figure['layout']['sliders'] = [sliders_dict]

py.icreate_animations(figure, 'fpl'+str(time.time()))
