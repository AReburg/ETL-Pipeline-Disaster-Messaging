# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from urllib.request import urlopen
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import gunicorn
# loop over the list of csv files
import os
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import joblib
import sqlite3
import random


def set_c(color):
    return random.choice(px.colors.qualitative.Set2)

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)
    return clean_tokens


test = [str(f'rgb({j},{j},{j})') for j in range(80,255)]
# load model
model = joblib.load("./models/classifier.pkl")
# load data
database_filepath = "./data/DisasterResponse.db"
con = sqlite3.connect(os.path.join(os.path.dirname(__file__), database_filepath))
df = pd.read_sql_query("SELECT * FROM model_data", con)
df2 = None
model_input =''
# [80+j*round((255-80)/36) for j in range(0,36)]

category_all = df.columns[2:]
df3 = pd.DataFrame(data={'color': [str("") for i in category_all]})
df3['color'] = df3.apply(lambda x: set_c(x['color']), axis=1)


# Define color sets of paintings
night_colors = ['rgb(56, 75, 126)', 'rgb(18, 36, 37)', 'rgb(34, 53, 101)']
fig_test = go.Figure(data=[go.Pie(values=df.genre.value_counts().to_list(), labels=df.genre.unique(), textinfo='label',
                                  insidetextorientation='radial', hole=.25, marker_colors=night_colors)])
fig_test.update_layout(legend_font_size=14,font=dict(family="Open Sans"))
fig_test.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
fig_test.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig_test.update(layout_showlegend=False)
fig_test.update_traces(marker=dict(line=dict(color='#9c9c9c', width=1.5)))
fig_test.update_traces(opacity=0.7)



# Plotting of Categories Distribution in Direct Genre
direct_cate = df[df.genre == 'direct']

direct_cate_counts = (direct_cate.mean() * direct_cate.shape[0]).sort_values(ascending=False)
direct_cate_names = list(direct_cate_counts.index)
fig_test2 = px.bar(x=[i.replace("_", " ").title() for i in direct_cate_names], y=direct_cate_counts)
fig_test2.update_traces(marker_color=night_colors[0], marker_line_color='#9c9c9c', marker_line_width=1, opacity=0.7)
fig_test2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
fig_test2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

fig_test2.update_layout(xaxis={'visible': True, 'showticklabels': True})
fig_test2.update_layout(yaxis={'visible': True, 'showticklabels': True})
fig_test2.update_yaxes(tickfont=dict(family='Helvetica', color='#9c9c9c'),
                 title_font_color='#9c9c9c', mirror=True,
                 ticks='outside', showline=True, gridwidth=1, gridcolor='#4c4c4c')
fig_test2.update_xaxes(tickfont=dict(family='Helvetica', color='#9c9c9c'),
                 title_font_color='#9c9c9c', mirror=True,
                 ticks='outside', showline=True, gridwidth=1, gridcolor='#4c4c4c')
fig_test2.update_layout(yaxis_title=None, xaxis_title=None)

app = Dash(__name__)
server = app.server

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    },
    'dash-graph2': {
        'height': '700px'
    }
}



app.layout = html.Div([

    html.Div([
        html.Div([html.Img(src=app.get_asset_url('logo.png'), height='25 px', width='auto')],
                className = 'col-2', style={'align-items': 'center', 'padding-top' : '1%', 'height' : 'auto'}),
        html.H2('Disaster Response Project'),
        html.P("Analyzing message data for  disaster response."),
        html.Br(),
        html.P("""This ML-model is trained on messages that were send during natural disasters. 
        Classifying these messages, would allow a disaster relief agency to take the appropriate measures. 
        There are 36 pre-defined categories such as "Aid related", "Search and Rescue", "Shelter" or "Medical Help". 
        Use the text input on the left to enter a message for classification."""),
        html.Div([f"Genre distribution of the {df.shape[0]} samples:"], className='text-padding'),
        html.Br(),
        html.Div([dcc.Graph(figure=fig_test),], style={'width': '250px', 'align-items': 'center'}),
        html.Div([dcc.Graph(figure=fig_test2),],),

        ], className='four columns div-user-controls'),


    html.Div([
        html.Div(
            [
        html.Br(),
        html.Br(),
        html.Br(),
                html.H4("Enter a message and hit enter"),

                html.Div(
                    children=[dcc.Input(id="input1", style={'border-radius': '8px', #'border': '4px solid red'
                                                            'background-color': '#31302f', 'color': 'white',
                                                            'width': '100%',
                                                            'padding':'5px'})],  # fill out your Input however you need
                    style=dict(display='flex', justifyContent='center')
                ),
                html.Br(),
                html.Div(id="output1"),
            ]
        ),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H2("Categorization based on the 36 pre-defined topics"),
        html.Br(),
        html.Div([dcc.Graph(id='result-histogram', figure={}, config={'displayModeBar': False},
                            style={'height': '900px', 'width': '1200px'})], className='dash-graph')
    ], className='eight columns div-for-charts bg-grey')
])


@app.callback(
    Output("output1", "children"),
    Input("input1", "value"),
)
def update_output(input1):
    if not input1:
        return ''
    else:
        model_input = tokenize(input1)
        print(f"{model_input} from \'{input1}\'")
        txt = ", ".join(str(x) for x in model_input)
        return u'{}'.format(txt)


@app.callback(
    Output('result-histogram', 'figure'),
    Input("output1", "children"))
def update_x_timeseries(output1):
    # use model to predict classification for query

    # use model to predict classification for query
    try:
        classification_labels = model.predict([model_input])[0]
        print(classification_labels)
        # classification_results = dict(zip(df.columns[4:], classification_labels))
    except:
        pass

    outp = [random.randint(0,1) for i in category_all]
    outp = [random.choice(category_all) for i in outp if i==1]
    category_all_n = [i.replace("_", " ").title() for i in category_all]

    d = {'cate': category_all_n, 'val': [1 if i in outp else 0 for i in category_all], 'color': [str("") for i in category_all]}
    df2 = pd.DataFrame(data=d)

    df2['color'] = df2.apply(lambda x: set_c(x['color']), axis=1)

    fig = px.bar(df2, x='val', y='cate', hover_data=['cate'], orientation='h')#, color='color')
    fig.update_layout(xaxis={'visible': False, 'showticklabels': False})
    fig.update_layout(yaxis={'visible': True, 'showticklabels': True})
    fig.update_yaxes(tickfont=dict(family='Helvetica', color='#9c9c9c'),
                     title_font_color='#9c9c9c',#mirror=True,
                     ticks='outside', showline=True, gridwidth=1, gridcolor='#4c4c4c')
    fig.update_layout(yaxis_title=None)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(marker_color=night_colors[0], marker_line_color='#9c9c9c', marker_line_width=1, opacity=0.7)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
    print(px.colors.qualitative.Set2)