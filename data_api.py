import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def fetch_data():
    response = requests.get('http://localhost:3001/')
    data = response.json()

    df_kpi = pd.DataFrame(data['df_kpi'])

    latest_kpi = df_kpi.iloc[-1]

    total_revenue = data['total_revenue']
    current_year_revenue = 0
    current_year = latest_kpi['Year']
    new_contracts = latest_kpi['SoHopDongMoi']
    ty_le_lap_day = latest_kpi['TyLeLapDay']
    current_growth = float(latest_kpi['TangTruongDoanhThu'])

    # Tạo ô tăng trưởng doanh thu
    growth_fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=current_growth,
        delta={"reference": current_growth , "position": "bottom", "relative": False},
        title={"text": "Tăng Trưởng Doanh Thu"},
        number={"suffix": "%"}
    ))

    response = requests.get('http://localhost:3001/DoanhThuQuy')
    dataquy = response.json()

    # Khởi tạo danh sách để chứa dữ liệu đã chuyển đổi
    data_list = []
    data_list1 = []
    # Duyệt qua từng năm và từng quý để chuyển đổi dữ liệu
    for year, quarters in dataquy.items():
        for quarter, tangs in quarters.items():
            for tang, revenue in tangs.items():
                data_list.append({
                    'Year': int(year),
                    'Quy': quarter,
                    'Tang': tang,
                    'Revenue': revenue
                })
    for year, quarters in dataquy.items():
        for quarter, tangs in quarters.items():
            for tang, revenue in tangs.items():
                data_list1.append({
                    'Quy': quarter,
                    'Tang': tang,
                    'Revenue': revenue
                })
    data_list2 = []
    for year, quarters in dataquy.items():
        for quarter, tangs in quarters.items():
            for tang, revenue in tangs.items():
                data_list2.append({
                    'Year': int(year),
                    'Quy': quarter,
                    'Revenue': revenue
                })
    TheoQuy = pd.DataFrame(data_list2)
    doanhThuTheoQuy = TheoQuy.groupby(['Year', 'Quy']).agg({'Revenue': 'sum'}).reset_index()
    df_group2 = doanhThuTheoQuy[-4:]

    # Chuyển đổi danh sách thành DataFrame
    df = pd.DataFrame(data_list)

    def find_latest_nonzero_quarter(df, year):
        quarters = ['Q4', 'Q3', 'Q2', 'Q1']
        for quarter in quarters:
            df_quarter = df[(df['Year'] == year) & (df['Quy'] == quarter)]
            if df_quarter['Revenue'].sum() > 0:
                return df_quarter
        return None

    latest_year = df['Year'].max()
    Nam = find_latest_nonzero_quarter(df, latest_year)
    Quy = pd.DataFrame(data_list1)

    # Tính tổng doanh thu theo tầng cho từng năm
    doanhThuTheoTangNam = df.groupby(['Year', 'Tang']).agg({'Revenue': 'sum'}).reset_index()
    doanhThuTheoTangQuy = Nam.groupby(['Quy', 'Tang']).agg({'Revenue': 'sum'}).reset_index()
    df_group = doanhThuTheoTangNam[-4:]
    df_group1 = doanhThuTheoTangQuy[-4:]

    def find_latest_nonzero_quarter1(df, year):
        quarters = ['Q4', 'Q3', 'Q2', 'Q1']
        for quarter in quarters:
            df_quarter = df[(df['Year'] == year) & (df['Quy'] == quarter)]
            if not df_quarter.empty and df_quarter['Revenue'].sum() > 0:
                return quarter
        return None

    def calculate_total_revenue_up_to_quarter(df, year, quarter):
        # Chỉ lấy các hàng dữ liệu của năm cụ thể và từ Q1 đến quý hiện tại
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        quarters_to_include = quarters[:quarters.index(quarter) + 1]
        filtered_df = df[(df['Year'] == year) & (df['Quy'].isin(quarters_to_include))]
        # Tính tổng doanh thu
        total_revenue = filtered_df['Revenue'].sum()
        return total_revenue

    latest_quarter = find_latest_nonzero_quarter1(df, latest_year)
    total_revenue_this_year = calculate_total_revenue_up_to_quarter(df, latest_year, latest_quarter)

    indicators = [
        {"title": "Tổng Doanh Thu", "value": total_revenue },
        {"title": "Doanh Thu Năm Hiện Tại", "value": total_revenue_this_year},
        {"title": "Số Hợp Đồng Được Thuê Trong Quý", "value": df_kpi['SoHopDongDuocThue'].iloc[-1]},
        {"title": "Số Hợp Đồng Mới Ký Trong Quý", "value": new_contracts}
    ]

    # Tạo các biểu đồ khác
    fig5 = px.bar(df_group, x='Tang', y='Revenue', title='Doanh Thu Theo Tầng Trong Năm')
    fig6 = px.bar(df_group1, x='Tang', y='Revenue', title='Doanh Thu Theo Tầng Trong Quý')
    fig7 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ty_le_lap_day,
        title="Độ Lấp Đầy Phòng",
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "green"}},
    ))
    fig8 = px.bar(df_group2, x='Quy', y='Revenue', title='Doanh Thu Theo Quý')
    df_group3 = doanhThuTheoQuy[-8:-4]
    df_group4 = doanhThuTheoQuy[-12:-8]
    df_g = pd.concat([df_group2, df_group3, df_group4])
    fig9 = px.line(df_g, x='Quy', y='Revenue', color='Year', title='Tăng Trưởng Doanh Thu Theo Quý')
    fig10 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=df_kpi['TyLeTaiKy'].iloc[-1],  # Giá trị tỷ lệ tái ký từ dữ liệu
        title="Tỷ Lệ Tái Ký",
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "blue"}},
    ))

    return indicators, growth_fig, fig5, fig6, fig7, fig8, fig9, fig10, doanhThuTheoQuy ,current_year

app.layout = dbc.Container([
    dcc.Interval(id='interval-component', interval=3*1000, n_intervals=0),
    dbc.Row([
        dbc.Col(html.Div([
            html.Label("CHỌN QUÝ BC", className="header-label"),
            dcc.Dropdown(
                id='quy-dropdown',
                options=[{'label': f'Q{i}', 'value': i} for i in range(1, 5)],
                value=1,
                clearable=False,
                className="dropdown"
            ),
            html.H3(id="year-header", className="header-year"),
            html.Button("Xuất Báo Cáo CSV", id="btn_csv", className="btn btn-primary")
        ]), width=4),
        dbc.Col(html.Div(id='output'), width=8)
    ], className="header-row"),
    dbc.Row([
        dbc.Col(html.Div([
            html.Div(id='indicator-container', className="indicator-container")
        ]), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='growth-fig'), width=3, className="card-small bordered-box"),
        dbc.Col(dcc.Graph(id='filled-rate-fig'), width=2, className="card-small bordered-box"),
        dbc.Col(dcc.Graph(id='renew-rate-fig'), width=2, className="card-small bordered-box"),
        dbc.Col(dcc.Graph(id='annual-revenue-fig'), width=5, className="card")
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='quarter-revenue-fig'), width=4, className="card"),
        dbc.Col(dcc.Graph(id='annual-quarter-revenue-fig'), width=4, className="card"),
        dbc.Col(dcc.Graph(id='revenue-growth-fig'), width=4, className="card")
    ]),
    dcc.Download(id="download-dataframe-csv"),
    dcc.Store(id='current-year-store')
], fluid=True, className="main-container")



@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True
)
def func(n_clicks):
    _, _, _, _, _, _, _, _, doanhThuTheoQuy,_ = fetch_data()
    limited_data = doanhThuTheoQuy.tail(12)
    return dcc.send_data_frame(limited_data.to_csv, "bao_cao_doanh_thu.csv")



@app.callback(
    [Output('indicator-container', 'children'),
     Output('growth-fig', 'figure'),
     Output('filled-rate-fig', 'figure'),
     Output('renew-rate-fig', 'figure'),
     Output('annual-revenue-fig', 'figure'),
     Output('quarter-revenue-fig', 'figure'),
     Output('annual-quarter-revenue-fig', 'figure'),
     Output('revenue-growth-fig', 'figure'),
     Output('current-year-store', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    indicators, growth_fig, fig5, fig6, fig7, fig8, fig9, fig10, _,current_year= fetch_data()

    indicator_elements = [html.Div([
        html.P(indicator["title"], className="indicator-title"),
        html.H3(f'{indicator["value"]:,}', className="indicator-value")
    ], className="indicator-box") for indicator in indicators]

    return indicator_elements, growth_fig, fig7, fig10, fig5, fig6, fig8, fig9, current_year

@app.callback(
    Output('year-header', 'children'),
    Input('current-year-store', 'data')
)
def update_year_header(current_year):
    return f"Năm {current_year}"

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Dashboard Cho Thuê Trọ</title>
        {%favicon%}
        {%css%}
        <style>
            .header-label {
                font-weight: bold;
                font-size: 1.2em;
            }
            .header-year {
                font-size: 1.5em;
                margin-top: 10px;
            }
            .dropdown {
                margin-top: 5px;
            }
            .header-row {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 15px;
            }
            .main-container {
                margin: 0 auto;
                padding: 20px;
                max-width: 1600px; /* Increase the max-width here */
            }
            .indicator-container {
                display: flex;
                justify-content: space-around;
                margin-bottom: 30px;
            }
            .indicator-box {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                width: 23%;
                text-align: center;
                background-color: #fff;
            }
            .indicator-title {
                font-size: 1em;
                font-weight: bold;
                margin: 0;
            }
            .indicator-value {
                font-size: 1.5em;
                color: green;
                margin: 5px 0 0 0;
            }
            .card {
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 15px;
            }
            .card-small {
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 15px;
                height: 300px;
            }
            .card .dash-graph {
                height: 100%;
            }
            .card-small .dash-graph {
                height: 100%;
            }
            .bordered-box {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True)
