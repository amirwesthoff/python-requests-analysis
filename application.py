import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

df = pd.read_csv('./output.csv')

df_no_other = df.loc[df['Label'] != 'Other']
df_no_rolenotes = df_no_other.drop(columns=['Role Notes'], axis=1)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

fig_pie1 = px.pie(
    data_frame=df.loc[df['Label'] != 'Other'],
    names='Label',
    values='Required FTE'

)

fig_pie2 = px.pie(
    data_frame=df,
    names='Label',
    values='Required FTE'
)

fig_bar = px.bar(
    data_frame=df.loc[df['Label'] != 'Other'],
    x='Label',
    y='Required FTE',
    hover_data=['Team Request Name']
)

fig_line = px.line(
    data_frame=df.loc[df['Label'] != 'Other'],
    x='Role Start Date',
    y='Required FTE',
    line_group='Label',
    color='Label'
)


app.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([
        html.H3(children='Agile Roles'),

        html.Div(children='''
            # Subtitle
        '''),

        dcc.Graph(
            id='graph1',
            figure=fig_pie1
        ),
    ], className='six columns'),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H3(children='Agile Roles vs. Other'),

        html.Div(children='''
            # Subtitle
        '''),

        dcc.Graph(
            id='graph2',
            figure=fig_pie2
        ),
    ], className='six columns'),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H3(children='Bar Chart'),

        html.Div(children='''
            # Subtitle
        '''),

        dcc.Graph(
            id='graph3',
            figure=fig_bar
        ),
    ], className='row'),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H3(children='Line Chart'),

        html.Div(children='''
            # Subtitle
        '''),

        dcc.Graph(
            id='graph4',
            figure=fig_line
        ),
    ], className='row'),
    # DataTable
    html.Div([
        html.H3(children='Data Table'),

        html.Div(children='''
        # Subtitle
        '''),

        dash_table.DataTable(
            id='graph5',
            columns=[{'name': i, 'id': i} for i in df_no_rolenotes.columns],
            data=df_no_rolenotes.to_dict('records'),
            filter_action='native',
            sort_action='native',
            page_action='native',
            page_size=20
        )
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
