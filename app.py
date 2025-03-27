from dash import Dash, html, dcc, Input, Output, dash_table, State, ctx
from mongodb_utils import get_keyword_trend, get_keyword_list
from neo4j_utils import get_univ_list, get_prof_list
from neo4j_utils import get_top_professor, get_top_keywords_of_univ, get_top_keywords_of_prof
from mysql_utils import fetch_all_fav_keywords, add_fav_keyword, delete_fav_keyword
from mysql_utils import get_recommended_prof, get_recommended_univ
import dash_bootstrap_components as dbc
import plotly.express as px

# create the Dash app
app = Dash(external_stylesheets=[dbc.themes.SOLAR])

# get lists of options
keyword_options = [{'label': keyword, 'value': keyword}
                   for keyword in get_keyword_list()]

university_options = [{'label': univ, 'value': univ}
                      for univ in get_univ_list()]

faculty_options = [{'label': prof, 'value': prof}
                     for prof in get_prof_list()]

# create the layout
app.layout = dbc.Container([
    dbc.Row([
        html.H1("Research Field Explorer",
                style={'textAlign': 'center', 'color':'white','fontWeight': 'bold' }),
    ], align="center", justify="center", class_name='pt-3'),

    # first row
    dbc.Row([
        # first widget
        dbc.Col([
            html.H2("See the Trend of Research Field", style={'color': 'white'}),
            html.Div([
                html.H4("Select Research Field", style={'color': 'white'}),
                dcc.Dropdown(
                    id="keyword",
                    options=keyword_options,
                    value=keyword_options[0]["value"],
                )
            ]),
            html.Div([
                dcc.Graph(
                    id="keyword-trend",
                    figure={}
                )
            ]),
        ], width=5),

        # second widget
        dbc.Col([
            html.H2("Top 10 Professors of Research Field", style={'color': 'white'}),
            
            dbc.Row([
                    html.H4("Select Research Field", style={'color': 'white'}),
                    dcc.Dropdown(
                        id="keyword-dropdown",
                        options=keyword_options,
                        value=keyword_options[0]['value']
                    )
                    ], class_name='my-3'),
            
            dbc.Row([
                html.H4("Select Year Range", style={'color': 'white'}),
                dcc.RangeSlider(
                    id="year-range-slider",
                    min=1980,
                    max=2020,
                    step=1,
                    value=[1980, 2020],
                    marks={
                        str(year): str(year)
                        for year in range(1980, 2020, 5)
                    }
                )
            ], class_name='my-3'),

            dash_table.DataTable(
                id="results-table",
                columns=[{"name": "Professor", "id": "Professor"},
                         {"name": "Institute", "id": "Institute"},
                         {"name": "Citation Score", "id": "Citation Score"}],
                editable=False,
                row_deletable=False,
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(8, 132, 204)', 'color': 'white', 'textAlign': 'center', 'fontWeight': 'bold'},
                style_table={'marginBottom': '10px'},
            ),

            html.H6("Ranked by Keyword-Relevant Citation (KRC)", style={'color': 'white'}),
        ], width=5),
    ], class_name='p-3 d-flex justify-content-around'),

    # second row
    dbc.Row([
        # third widget
        dbc.Col([
            html.H2("Top Research Keywords of University", style={'color': 'white'}),
            
            html.Div([
                html.H4("Select University", style={'color': 'white'}),
                dcc.Dropdown(
                    id="university",
                    options=university_options,
                    value=university_options[0]["value"],
                )
            ]),
            html.Div([
                dcc.Graph(
                    id="keyword-scores",
                    figure={}
                )
            ]),
            html.H6("Ranked by number of faculty interested in the field", style={'color': 'white'}),
        ], width=5),

        # fourth widget
        dbc.Col([
            html.H2('Top Keywords of Professor', style={'color': 'white'}),
            
            dbc.Row([
                html.H4("Select Professor", style={'color': 'white'}),
                dcc.Dropdown(
                    id="faculty-dropdown",
                    options=faculty_options,
                    value=faculty_options[2]["value"],
                )
            ], className='my-3'),

            html.Div(id='table-container'),
            html.H6("Ranked by Keyword-Relevant Citation (KRC)", style={'color': 'white'}),

        ], width=5)
    ], class_name='p-3 d-flex justify-content-around'),

    # third row

    dbc.Row([
        # add to Favorite Keywords 
        dbc.Col([
            html.H2("Add Your Favorite Keywords", style={'color': 'white'}),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='keyword-dropdown-2',
                        options=keyword_options,
                        value='',
                    ),
                ]),
                dbc.Col([
                    dbc.Button('Add', id='add-to-fav-button',
                               n_clicks=0, color='secondary', className='mr-2')
                ]),
            ], className='my-3'),
            dash_table.DataTable(
                id='fav-keywords-table',
                columns=[{"name": "Favorite Keywords", "id": "keywords"}],
                data=[{"keywords": k}
                      for k in fetch_all_fav_keywords()],
                editable=True,
                sort_action="native",
                sort_mode="multi",
                row_deletable=True,
                page_size=10,
                selected_rows=[],
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(8, 132, 204)', 'color': 'white', 'textAlign': 'center', 'fontWeight': 'bold'},
                style_table={'marginBottom': '10px'},

            ),
        ], width=5, style={'paddingRight': '50px', 'paddingLeft': '100px', 'marginTop': '40px', 'marginBottom': '10px'}),

        # fifth widget

        dbc.Col([
            html.H2("Recommended Professors", style={'color': 'white'}),
            dash_table.DataTable(
                id='top-faculty-table',
                columns=[{"name": "Professor", "id": "Professor"},
                         {"name": "University", "id": "Institute"},
                         {"name": "Total Citation Score", "id": "Total Citation Score"}],
                data=get_recommended_prof(),
                sort_action="native",
                sort_mode="multi",
                page_size=10,
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(8, 132, 204)', 'color': 'white', 'textAlign': 'center', 'fontWeight': 'bold'},
                style_table={'marginBottom': '10px'},
            ),
        ], width=5, style={ 'marginTop': '40px'}),

        
    ], class_name='p-3 d-flex justify-content-around'),

    # fourth row
    dbc.Row([

        dbc.Col(width = 5),
        # sixth widget 
        dbc.Col([
            html.H2("Recommended Universities", style={'color': 'white'}),
            dash_table.DataTable(
                id='top-university-table',
                columns=[
                        {"name": "University", "id": "Institute"},
                        {"name": "Related Professor Count", "id": "Related Professor Count"},
                        {"name": "Total Citation Score", "id": "Total Citation Score"}],
                data=get_recommended_univ(),
                sort_action="native",
                sort_mode="multi",
                page_size=10,
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(8, 132, 204)', 'color': 'white', 'textAlign': 'center', 'fontWeight': 'bold'},
                style_table={'marginBottom': '10px'},
            ),
        ], width=5)

    ], class_name='p-3 d-flex justify-content-around')
], fluid=True)


# first widget callbacks
@app.callback(
    Output(component_id='keyword-trend', component_property='figure'),
    [Input(component_id='keyword', component_property='value')]
)
def update_keyword_trend(keyword): 
    df = get_keyword_trend(keyword)
    fig = {
        'data': [{
            
            'x': df['year'],
            'y': df['publication count'],
            'type': 'line',
            'marker': {'color': 'blue'}
        }],
        'layout': {
            'title': f'Trend for {keyword}',
            'xaxis': {'title': 'Year'},
            'yaxis': {'title': 'Publication Count'}
        }
    }
    return fig

# second widget callback
@app.callback(
    Output("results-table", "data"),
    [Input("keyword-dropdown", "value"),
     Input("year-range-slider", "value")]
)
def update_results_table(keyword, year_range):
    start_year, end_year = year_range    
    df = get_top_professor(keyword, start_year, end_year)
    # return the data for the dash_table component
    return df.to_dict("records")

# third widget callbacks
@app.callback(
    Output(component_id='keyword-scores', component_property='figure'),
    [Input(component_id='university', component_property='value')]
)
def update_keyword_rank(university):
    df = get_top_keywords_of_univ(university)
    df = df.sort_values('Professor Count', ascending=True)
    fig = {
        'data': [{
            'x': df['Professor Count'],
            'y': df['Keyword'],
            'type': 'bar',
            'orientation': 'h',  # horizontal bar chart
            'marker': {'color': 'blue'}
        }],
        'layout': {
            'title': f'Top 10 Research Keywords for {university}',
            'xaxis': {'title': 'Professor Count'},
            'margin': {'l': 200, 'r': 50, 't': 50, 'b': 50} 
           
        }
    }
    return fig

# fourth widget callbacks
@app.callback(
    Output('table-container', 'children'),
    Input('faculty-dropdown', 'value')
)
def update_table(prof):
    df = get_top_keywords_of_prof(prof)
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df.columns],
        style_cell={'textAlign': 'left'},
         style_header={
                    'backgroundColor': 'rgb(8, 132, 204)', 'color': 'white', 'textAlign': 'center', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}]
    )
    return table

# fifth & six widgets callbacks
@app.callback(
    [Output('fav-keywords-table', 'data', allow_duplicate=True),
     Output('top-faculty-table', 'data', allow_duplicate=True),
     Output('top-university-table', 'data', allow_duplicate=True)],
    [Input('add-to-fav-button', 'n_clicks')],
    [State('keyword-dropdown-2', 'value'),
     State('fav-keywords-table', 'data')],
    prevent_initial_call=True
)
def update_favorite_table(n_clicks, selected_keyword, table_data):
    if n_clicks is None:
        print("no click")
        # This means that the callback was triggered by something other than the button click
        return table_data, [], []

    if 'add-to-fav-button' == ctx.triggered_id and selected_keyword:
        print("click btn")
        if {'keywords': selected_keyword} not in table_data:
            add_fav_keyword(selected_keyword)
            table_data.append({'keywords': selected_keyword})
            top_faculty = get_recommended_prof()
            top_university = get_recommended_univ()
            print("top faculty", top_faculty)
            print("top university", top_university)
            return table_data, top_faculty, top_university
        
    print('error return empty')
    return table_data, [], []

# callback to delete keyword from favorite table
@app.callback(
    [Output('fav-keywords-table', 'data', allow_duplicate=True),
     Output('top-faculty-table', 'data', allow_duplicate=True),
     Output('top-university-table', 'data', allow_duplicate=True)],
    [Input('fav-keywords-table', 'data'),
     Input('top-faculty-table', 'data'),
     Input('top-university-table', 'data')],
    prevent_initial_call=True
)
def delete_fav_keyword_callback(data, faculty_data, university_data):
    # get list of keywords in the table before deletion
    keywords_before_delete = fetch_all_fav_keywords()

    # get list of keywords in the table after the row was deleted
    keywords_after_delete = [row['keywords'] for row in data]

    # find the keyword that was deleted
    deleted_keyword = None
    if len(set(keywords_before_delete).difference(set(keywords_after_delete))) > 0:
        deleted_keyword = set(keywords_before_delete).difference(
            set(keywords_after_delete)).pop()

    # delete the keyword from the database, update recommended profs & univs
    if deleted_keyword:
        delete_fav_keyword(deleted_keyword)
        top_faculty = get_recommended_prof()
        top_university = get_recommended_univ()
        return data, top_faculty, top_university

    print('error return empty')
    return data, faculty_data, university_data


if __name__ == "__main__":
    app.run_server(debug=False)

