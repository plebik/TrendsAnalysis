import pandas as pd
from constants import *
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
import math


def create_plot(frame, category='', experience='', yaxis_title='', yaxis=None, save=False):
    fig_ = go.Figure()

    # change years to string
    years_in_string = frame.index.astype(str)

    # Plot each series with a specified color
    for name in frame.columns:
        fig_.add_trace(go.Scatter(x=years_in_string, y=frame[name], mode='lines+markers', name=f"{name}_{experience}",
                                  line=dict(width=4), marker=dict(size=10)))

    layout_ = {
        "title": experience,
        "xaxis_title": "Year",
        "yaxis_title": yaxis_title,
        "legend": dict(title="Company Size")
    }

    if yaxis is not None:
        layout_['yaxis'] = yaxis

    fig_.update_layout(**layout_)

    if save:
        pio.write_image(fig_, f'plots/{yaxis_title}/{category}_{experience}.svg')

    return fig_


def create_subplots(figures: list, category, yaxis_title, save=False):
    num_figures = len(figures)
    num_rows = num_cols = int(math.ceil(math.sqrt(num_figures)))

    subplot_titles = [fi.layout.title.text for fi in figures]
    fig_ = make_subplots(rows=num_rows, cols=num_cols, subplot_titles=subplot_titles)

    prefix_color_mapping = {'L': '#cc3535', 'M': '#f1c232', 'S': '#6aa84f'}

    for i, f in enumerate(figures):
        row = i // num_cols + 1
        col = i % num_cols + 1
        for r in f['data']:
            trace_name = r['name']

            # Extract the prefix from the trace name
            prefix = trace_name[0] if trace_name else ''

            # Get the color based on the prefix from the mapping
            color = prefix_color_mapping.get(prefix, 'yellow')

            # Set the color for the trace
            r['marker']['color'] = color
            r['line']['color'] = color

            # Add the trace to the subplot
            fig_.add_trace(r, row=row, col=col)

    layout_ = {
        "title": f"Category: {category}",
        "width": 1920,
        "height": 1080,
    }

    fig_.update_layout(**layout_)
    fig_.update_yaxes(title_text=yaxis_title)
    fig_.update_xaxes(title_text="Year")

    if save:
        pio.write_image(fig_, f'plots/{yaxis_title}/{category}.svg')

    return fig_


data = pd.read_csv('data.csv')
data.columns = ['year', 'title', 'category', 'currency', 'salary', 'salary_in_dollars', 'employee_residence',
                'experience', 'employment_type', 'working_mode', 'company_location', 'company_size']

# limit the data only to Europe countries both for company_location and employee_residence and to Full-time employment_type
limited_data = data[(data['employment_type'] == 'Full-time') & (data['employee_residence'].isin(european_countries)) & (
    data['company_location'].isin(european_countries))]
limited_data.reset_index(drop=True, inplace=True)
limited_data = limited_data.drop(columns=['employment_type', 'salary', 'currency', 'title'])

# category = limited_data['category'].unique()
experience = limited_data['experience'].unique()
size = limited_data['company_size'].unique()
year = sorted(limited_data['year'].unique())

category = ['Data Analysis']

tmp_dict = {}

for c in category:
    tmp_dict[c] = {}

    figures_of_averages = []
    figures_of_pct_changes = []

    for e in experience:
        tmp_dict[c][e] = {}
        for s in size:
            tmp_dict[c][e][s] = {}
            for y in year:
                tmp_frame = limited_data[(limited_data['category'] == c) & (limited_data['experience'] == e) & (
                        limited_data['company_size'] == s) & (limited_data['year'] == y)]

                monthly_salary = tmp_frame['salary_in_dollars']
                tmp_dict[c][e][s][y] = round(monthly_salary.mean(), 2)

        # plot creation
        plot_frame = pd.DataFrame(tmp_dict[c][e])

        # create simple average salary plot
        figures_of_averages.append(
            create_plot(plot_frame, category=c, experience=e, yaxis_title='Avg. Salary'))

        # create percentage change
        no_na_frame = plot_frame.ffill()
        pct_change_frame = no_na_frame.pct_change(fill_method=None)
        figures_of_pct_changes.append(create_plot(pct_change_frame, category=c, experience=e, yaxis_title='Pct. Change',
                                                  yaxis=dict(tickformat=".2%")))

    create_subplots(figures_of_averages, category=c, yaxis_title='Avg. Salary', save=True)
