import numpy as np
from dash.dependencies import State, Input, Output
from dash import Dash, html, dash_table, dcc, callback, ctx
import pandas as pd
import plotly.express as px
from urllib.request import urlopen
import json

jobs_df = pd.read_csv('jobs_df.csv')

# Create county_counts df
county_counts = pd.DataFrame(jobs_df.groupby(['fips', 'county']).count()['name'])
county_counts = county_counts.reset_index().rename(columns={'name': 'num_jobs'})
county_counts.fips = [int(fip) for fip in county_counts.fips]

# Create county_salaries df
county_salaries = pd.DataFrame(jobs_df.groupby(['fips', 'county'])['salary'].mean())
county_salaries = county_salaries.reset_index().rename(columns={'name': 'num_jobs'})

# Create fips df
fips_codes = pd.read_csv('school_salaries - fips codes.csv')
fips_codes = fips_codes.rename(columns={'Unnamed: 1': 'county'})
fips_codes.fips = fips_codes.fips.str[3:]
fips_codes.fips = [int(fip) for fip in fips_codes.fips]
fips_codes = fips_codes.merge(county_counts, how='left').fillna(0)
fips_codes = fips_codes.merge(county_salaries, how='left').fillna(0)
# salaries = ["{:,.0f}".format(sal) for sal in fips_codes['salary']]
# fips_codes['salary_formatted'] = salaries

new_lists = []

for lst in jobs_df['school_type2'].fillna(0):
    if lst != 0:
        weird_list = lst.split()
        new_list = [item.strip('"[],').strip("'") for item in weird_list]
        new_lists.append(new_list)
    else:
        new_lists.append(0)

jobs_df.school_type2 = new_lists

new_school_types = []
for type_list in jobs_df['school_type2'].fillna(0):
    if type_list == 0:
        new_school_types.append('Elementary/Middle/High')
    elif len(list(type_list)) == 1:
        new_school_types.append(type_list[0])
    elif len(list(type_list)) == 2:
        new_school_types.append(type_list[0] + "/" + type_list[1])
    elif len(list(type_list)) == 3:
        new_school_types.append(type_list[0] +
                                "/" + type_list[1] +
                                "/" + type_list[2])
    else:
        new_school_types.append('Elementary/Middle/High')
jobs_df['school_type2_updated'] = new_school_types
jobs_df['school_designations'] = [g.split('/') for g in jobs_df['school_type2_updated']]

# Create simple jobs df
jobs_simple = (jobs_df[['name', 'district', 'school',
                        'county', 'category', 'school_type',
                        'salary', 'school_type2', 'school_type2_updated', 'school_designations']]
               .sort_values(['county', 'district']))

# Load TN county geojson
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# Start Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1('April 2025 Tennessee Teacher Job Dashboard',
            style={'textAlign': 'center', 'color': 'black', 'font': 'Arial'}),
    html.Div([
        html.Div([
            html.Div([
                dcc.RadioItems(
                    options=['By # of job postings', 'By salary'],
                    value='By # of job postings',
                    inline=True,
                    id='map-radio-buttons'
                )
            ], style={'textAlign': 'center'}),

            html.Div([
                html.Div([
                    dcc.Graph(id='controls-and-graph', style={'height': '400px'}),
                    html.Div(id='selected-county', style={'display': 'none'}),
                ], style={'display': 'inline-block',
                          'verticalAlign': 'top'}),
                html.Button("Reset Map", id='reset-map-button', n_clicks=0, style={'marginTop': '10px'})
            ], style={'textAlign': 'center'})
        ], style={'border-style': 'solid', 'border-width': '1px', 'width': '50%', 'display': 'inline-block'}),

        html.Div([
            html.H4("School Grades"),
            dcc.Checklist(['Elementary', 'Middle', 'High'], id='school-grade-checklist',
                          inline=True,
                          style={'marginBottom': 20}),
            html.H4("Job Type"),
            dcc.Checklist(sorted(list(jobs_simple.category.unique())),
                          id='job-type-checklist',
                          labelStyle={'display': 'inline-block', 'width': '48%', 'marginRight': '5px',
                                      'whiteSpace': 'nowrap'})
        ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': 20}),

        html.Div([
            html.H3("District Average Salary"),
            html.Div(id='avg-salary-box', style={'fontSize': 20, 'marginBottom': 30})
        ], style={'width': '50%', 'display': 'inline-block', 'textAlign': 'center'})
    ]),

    html.Div([
        html.Div([
            html.H3("Available Jobs"),
            dash_table.DataTable(
                id='job-table',
                columns=[{"name": i, "id": i} for i in ['name', 'district', 'school', 'county']],
                page_size=15,
                style_table={'overflowY': 'auto'},
                row_selectable='single',
                style_cell={
                    'font_family': 'tahoma',
                    'font_size': '12px',
                    'text_align': 'center'
                },
            )
        ], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            html.H3("Job Details"),
            html.Div(id='job-detail-box')
        ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': 40})
    ]),

    html.Spacer(),

    html.Div([
        html.Footer([
            html.H3("DATA 304 Final Project")
        ], style={'display': 'inline-block', 'paddingLeft': 20, 'width': '90%'}),
        html.Footer([
            html.H3("Greta Goss")
        ], style={'display': 'inline-block', 'textAlign': 'center'})
    ], style={'backgroundColor': 'rgb(225,225,225)'})
], style={'font-family': 'tahoma', 'backgroundColor': 'rgb(235, 243, 250)'})


@callback(
    Output('controls-and-graph', 'figure'),
    Input('map-radio-buttons', 'value')
)
def update_map(option):
    if option == 'By # of job postings':
        colorscale = [[0, 'rgb(225,225,225)'],
                      [0.0001, 'rgb(225,225,225)'],
                      [0.0001, 'rgb(242,165,163)'],
                      [1, 'rgb(180,34,27)']]
        fig = px.choropleth(
            fips_codes,
            geojson=counties,
            scope='usa',
            locations='fips',
            color='num_jobs',
            color_continuous_scale=colorscale,
            range_color=(1, fips_codes['num_jobs'].max()),
            hover_data={'county': True, 'num_jobs': True, 'fips': False}
        )
    else:
        colorscale = [[0, 'rgb(225,225,225)'],
                      [0.01, 'rgb(225,225,225)'],
                      [0.6, 'rgb(235, 243, 250)'],
                      [1, 'rgb(27,84,125)']]
        fig = px.choropleth(
            fips_codes,
            geojson=counties,
            scope='usa',
            locations='fips',
            color='salary',
            color_continuous_scale=colorscale,
            range_color=(fips_codes['salary'].min(), fips_codes['salary'].max()),
            hover_data={'county': True,
                        # 'salary_formatted': ':$',
                        'fips': False,
                        'salary': ':$.0f'}
        )
    fig.update_geos(fitbounds="locations", visible=False)
    return fig


@callback(
    Output('job-table', 'data'),
    Output('avg-salary-box', 'children'),
    Input('controls-and-graph', 'clickData'),
    Input('reset-map-button', 'n_clicks'),
    Input('job-type-checklist', 'value'),
    Input('school-grade-checklist', 'value')
)
def update_jobs(clickData, reset_clicks, sel_job_types, sel_grades):

    trigger_id = ctx.triggered_id

    sel_job_types = sel_job_types or list(jobs_simple['category'].unique())
    sel_grades = sel_grades or ['Elementary', 'Middle', 'High']

    if trigger_id == 'reset-map-button':
        county_name = None
        filtered_df = jobs_simple
    elif clickData and 'points' in clickData:
        county_name = clickData['points'][0]['customdata'][0]
        filtered_df = jobs_simple[jobs_simple['county'] == county_name]
    else:
        filtered_df = jobs_simple
        county_name = None

    filtered_df = filtered_df[filtered_df['category'].isin(sel_job_types)]

    filtered_df = filtered_df[
        filtered_df['school_designations'].apply(lambda g: any(grade in g for grade in sel_grades) if isinstance(g, list) else False)
    ]

    if county_name:
        if filtered_df.empty:
            salary = fips_codes[fips_codes['county'] == county_name]['salary'].values
            avg_salary = f"${int(salary[0]):,}" if len(salary) > 0 else "N/A"
            return [], f"{county_name} County: {avg_salary}"
        else:
            salary = fips_codes[fips_codes['county'] == county_name]['salary'].values
            avg_salary = f"${int(salary[0]):,}" if len(salary) > 0 else "N/A"
            filtered_df = filtered_df[['name', 'category', 'school', 'county', 'district', 'school_type', 'school_type2_updated']]
            return filtered_df.to_dict('records'), f"{county_name} County: {avg_salary}"
    else:
        if filtered_df.empty:
            return [], "Select a county to see average salary."
        else:
            filtered_df = filtered_df[['name', 'category', 'school', 'county', 'district', 'school_type', 'school_type2_updated']]
            return filtered_df.to_dict('records'), "Select a county to see average salary."


@callback(
    Output('job-detail-box', 'children'),
    Input('job-table', 'selected_rows'),
    State('job-table', 'data')
)
def show_job_details(selected_rows, job_data):
    if selected_rows is None or not selected_rows:
        return "Click on a job to see details."
    job = job_data[selected_rows[0]]
    return html.Div([
        html.H4("Title", style={"line-height": ".4"}),
        html.P(f"{job['name']}"),
        html.H4("Category"),
        html.P(f"{job['category']}"),
        html.H4("School"),
        html.P(f"{job['school']}"),
        html.H4("District"),
        html.P(f"{job['district']}"),
        html.H4("School Type"),
        html.P(f"{job['school_type']}, {job['school_type2_updated']}")
    ])


if __name__ == '__main__':
    app.run(debug=True)
