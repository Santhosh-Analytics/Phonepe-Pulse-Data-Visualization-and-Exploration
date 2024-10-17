# Import necessary libraries


from PIL import Image
import io
import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import ydata_profiling
import streamlit_extras
from streamlit_player import st_player
from streamlit_pandas_profiling import st_profile_report
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_option_menu import option_menu
import streamlit_extras.metric_cards as metric_cards
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
import _json
# import sys



image=Image.open("phonepe-logo-icon.jpg")
you_image=Image.open("Youtube.png")


page_bg_img = '''
<style>
    .stApp {
        # background-image: url("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fe1.pxfuel.com%2Fdesktop-wallpaper%2F246%2F629%2Fdesktop-wallpaper-glossy-black-shiny-black.jpg&f=1&nofb=1&ipt=94aa5d1f9d650cac934f99411cce8fa55ef43d1aabce3f3faffc7ed1776c144e&ipo=images");
        background-image:url("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwallpaperset.com%2Fw%2Ffull%2Fc%2F4%2F2%2F2932.jpg&f=1&nofb=1&ipt=167b8ede7fb9039711212e5ae543004922bc451239b539ed9d447699ccab439d&ipo=images")
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
</style>
'''
# Streamlit page configuration

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_title="Phonepe Pulse DB",
    page_icon=image,
    )


st.markdown("""
    <style>
    /* Tabs */
    div.stTabs [data-baseweb="tab-list"] button {
        font-size: 25px !important;
        color: #f9f9f9 !important;
        background-color: darkgreen !important;
        padding: 10px 20px !important;
        margin: 10px 2px !important;
        border-radius: 10px !important;
        shadow: 0 4px 8px #ddd !important;
        
    }
    div.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #009688 !important;
        color: white !important;
        shadow: 0 4px 8px #ddd !important;
        
    }

    div.stTabs [data-baseweb="tab-list"] button:hover {
        background-color: #3e8e41 !important;;
        color: white !important;;
        margin: 0px !important;;
        cursor: pointer !important;;
        shadow: 0 4px 8px #ddd !important;
        border-radius: 22px !important;
        
        
    }
    /* Button */
    .stButton>button {
        font-size: 22px ;
        background-color: Aquamarine !important;
        color: white !important;
        border-color: darkgreen !important;
        padding: 5px 5px !important;
        text-align: center !important;
        margin: 4px 2px !important;
        cursor: pointer !important;
        border-radius: 12px !important;
        shadow: 0 4px 8px #ddd !important;
    }
    .stButton>button:hover {
        background-color: darkgreen !important;
        color: white !important;
        font-size: 22px;
        text-decoration: text-overflow !important;
        transition: width 2s !important;
        border-radius: 22px !important;
        border-color: darkred !important;
        shadow: 0 4px 8px #ddd !important;
    }
    </style>
    """, unsafe_allow_html=True)


def get_db_connection():
    # Construct the database URL based on the type
    if db_type == 'mysql':
        connection_string = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    elif db_type == 'postgresql':
        connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    else:
        raise ValueError("Unsupported database type")
    
    engine = create_engine(connection_string)
    return engine

with st.sidebar:
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)
    
    selected = option_menu("Main Menu", ["Home", 'Datasets','Overview','Transactions','Users','Trend','Comparison'], 
        icons=['house-door-fill', 'database-fill-gear','bar-chart-fill','credit-card','people-fill','graph-up-arrow', 'tropical-storm'], menu_icon="cast", default_index=0,styles={
        "container": {"padding": "0!important", "background-color": "#242a44"},
        "icon": {"color": "rgb(235, 48, 84)", "font-size": "25px"}, 
        "nav-link": {"font-size": "22px", "color": "#ffffff","text-align": "left", "margin":"0px", "--hover-color": "#84706E"},
        "nav-link-selected": {"background-color": "#84706E  ","color": "white","font-size": "20px"},
    })
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)


st.markdown(""" <style> button[data-baseweb="tab"] > di v[data-testid="stMarkdownContainer"] > p {font-size: 28px;} </style>""", unsafe_allow_html=True)



st.markdown("<h1 style='text-align: center; font-size: 38px; color: #5f1f9c ; font-weight: 700;font-family:PhonePeSans;'>Phonepe Pulse Data Visualization and Exploration </h1>", unsafe_allow_html=True)

load_dotenv()

db_type = os.getenv('DB_TYPE')
db_user = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '3306')
db_name = 'phonepe_pulse'

@st.cache_data(ttl=None,persist="disk")
def fetch_create_df(db_name,db_cond_substring):
    
    # engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    con=get_db_connection().connect()
    tbls={}
    result =con.execute(text('show tables')).fetchall()
    for i in result:
        tb=i[0]
        if any(sub in tb for sub in db_cond_substring):
            data=con.execute(text(f'select * from {tb}')).fetchall()
            columns = [column[0] for column in con.execute(text(f'select * from {tb}')).cursor.description] 
            df=pd.DataFrame(data,columns=columns)
            tbls[tb]=df
        else:
            pass
    for tb_name,df in tbls.items():
        globals()[tb_name] = df 
    return tbls

tbls = fetch_create_df("phonepe_pulse",["user","tran"])

@st.cache_data(ttl=None,persist="disk")
def year_to_str(df):
    df['Year'] = df["Year"].astype(str)


@st.cache_data(ttl=None,persist="disk")
def SQL_QRY(query):
    # engine = get_db_connection()
    con=get_db_connection().connect()
    result =con.execute(text(query))
    data=result.fetchall()
    qry_df =pd.DataFrame(data)
    return qry_df



# st.write(tbls['agg_tran'].head())
# for df_name, df in tbls.items():
#     if "user" in df_name or "tran" in df_name:
#         st.write(df_name)
#         df[' Year '] = df[" Year "].astype(str)



if selected =="Home":
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)
    # add_vertical_space(1)
    st.markdown("<h3 style='text-align:left; color: #dd9933;'> About Phonepe Pulse Data:  </h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left; font-size: 18px; color: #e6e2d3; font-weight: 400;font-family:PhonePeSans;'>The Indian digital payments story has truly captured the world's imagination. From the largest towns to the remotest villages, there is a payments revolution being driven by the penetration of mobile phones and data.PhonePe Pulse is your window to the world of how India transacts with interesting trends, deep insights and in-depth analysis based on our data put together by the PhonePe team.</p>", unsafe_allow_html=True)
    # add_vertical_space(2)
    st_player(url=("https://www.youtube.com/watch?v=c_1H6vivsiA"))

    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:left; color: #dd9933;'> About this app:  </h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left; font-size: 18px; color: #e6e2d3; font-weight: 400;font-family:PhonePeSans;'>    In this Streamlit app you can see the visualized PhonePe pulse data and gain a lot of insights. Used Plotly to create a dynamic dashboard with interactive charts and graphs, providing users with a visual insight. Using dashboards we can Explore transaction trends, including transaction amounts, type breakdowns, and geographical distribution. These unveils hidden patterns and trends in PhonePe Pulse data. </p>", unsafe_allow_html=True)


if selected=="Datasets":

    st.markdown("<h1 style='text-align: center; font-size: 38px; color:rgb(235, 48, 84) ; font-weight: 700;font-family:PhonePeSans;'>Datasets and it's insights </h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    col, buff = st.columns([4, 4])
    col.markdown("<h3 style='text-align: left; color: rgb(235, 48, 84);font-family:PhonePeSans;'> Select Dataset to Explore and Download: </h3>", unsafe_allow_html=True)
    option = col.selectbox(
                                label="",
                            options=list(tbls.keys()),
                            key='df'
                            )

    st.markdown('<style>div.css-1jpvgo6 {font-size: 16px; font-weight: bolder;font-family:PhonePeSans; } </style>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(['Report and Dataset', 'Download Dataset'])

    
    pr= None

    # @st.cache_data(ttl=None,persist="disk",experimental_allow_widgets=True)
    def  load_pr(df_name):       
        pr = df_name.profile_report() 
        with st.container():
            st_profile_report(pr)


    with tab1:
        column1, column2, buffer = st.columns([2, 2, 4])
            
        show_profile = column1.button(label = 'Show Detailed Report', key = 'show')
        show_df = column2.button(label = 'Show Dataset', key = 'show_df')
        st.markdown(""" <style> div.stButton > button:first-child {background-color: #563f46    ;color:white;font-size:8px;height:3em;width:30em;border-radius:5px 5px 5px 5px;}  </style>""", unsafe_allow_html=True)

        if show_profile:
            load_pr( tbls[option])
                    
        if show_df:
            lenth = len(tbls[option])
            st.data_editor(
                data = tbls[option].head(100),
                use_container_width=True, height=1000
                )
            
 
    with tab2:
        col1, col2, col3 = st.columns(3)

        csv = tbls[option].to_csv()
        json = tbls[option].to_json(orient ='records')
        excel_buffer = io.BytesIO()
        writer = pd.ExcelWriter(excel_buffer, engine='xlsxwriter') 
        tbls[option].to_excel(writer, index=False)
        writer.close()
        excel_bytes = excel_buffer.getvalue()
        
        col1.download_button(
                            "Download as CSV", data = csv,
                            file_name = f'{option}.csv',
                            mime = 'text/csv', key = 'csv'
                            )
        col2.download_button(
                            "Download as JSON", data = json,
                            file_name = f'{option}.json',
                            mime = 'application/json', key = 'json'
                            )
        col3.download_button("Download as Excel", data = excel_bytes,
                            file_name = f'{option}.xlsx',
                            mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            key = 'excel'
                            )


def filter_list(df,suff,multi_st=False):
    col1,col2,col3= st.columns([4, 3, 2])
    state_list = df['State'].unique()
    year_list = df['Year'].unique()
    if multi_st:
        state_opts = col1.multiselect(f'State (Select Multiple)', state_list, key=f'state_opts{suff}')
    else:
        state_opts = col1.selectbox(f'State', ["All"] + list(map(str, state_list)), key=f'state_opts{suff}')
    year_opts = col2.selectbox(f'Year', year_list, key=f'year_opts{suff}')

    available_qtrs = df.loc[df['Year'] == year_opts, 'Quarter'].unique()
    qtr_list = ['All'] + list(map(int, available_qtrs))
    qtr_opts = col3.selectbox(f'Quarter', qtr_list, key=f'qtr_opts{suff}')
    filtered_df=df[df["Year"] == year_opts]
    if  multi_st and state_opts is not None:
            filtered_df = filtered_df[filtered_df["State"].isin(state_opts)]

    elif multi_st ==False and state_opts !='All':
            filtered_df=filtered_df[(filtered_df["State"] == state_opts)]
    
    elif multi_st ==False and state_opts =='All':
            filtered_df=filtered_df
    else:
        st.info('Select state to show chart')
        return None, None, None, None
    if qtr_opts!='All':
        filtered_df=filtered_df[filtered_df["Quarter"] == qtr_opts]
    return filtered_df,qtr_opts,state_opts,year_opts


@st.cache_data(ttl=None,persist="disk")
def create_plotly_charts(data, chart_type, x_column, y_column, widthv=None,heightv=None,grid=False ,**kwargs):
    if chart_type == 'Pie':
        fig = px.pie(data, values=y_column, names=x_column, **kwargs)
    if chart_type == 'lne':
        fig=px.line(data,x=x_column,y=y_column,**kwargs)
    elif chart_type == 'Treemap':
        fig=px.treemap(data,path=x_column,values=y_column,**kwargs)
    elif chart_type=='densitymap':
        fig=px.density_mapbox(data,lat=x_column,lon=y_column,**kwargs)
    elif chart_type == 'Bar':
        if 'text_auto' in kwargs:
            kwargs.pop('text_auto')  # Remove 'text_auto' from kwargs
            fig = px.bar(data, x=x_column, y=y_column, text=y_column, **kwargs).update_layout(width=widthv, height=heightv)
        else:
            fig = px.bar(data, x=x_column, y=y_column, **kwargs).update_layout(width=widthv, height=heightv)
    if not grid:
        if chart_type == 'Bar':
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=False)
    return fig

def filter_top_trans_dist(top_trans_dist, year, quarter):
    filtered_top_trans_dist = top_trans_dist[top_trans_dist['Year'] == year]
    if quarter != 'All':
        filtered_top_trans_dist = filtered_top_trans_dist[filtered_top_trans_dist['Quarter'] == quarter]
    return filtered_top_trans_dist

if selected == 'Overview':
        
    st.markdown("<h1 style='text-align: center; font-size: 38px; color:#dd9933 ; font-weight: 700;font-family:PhonePeSans;'>Overview </h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: left; color: #dd9933;font-family:PhonePeSans;'> Comprehensive Highlights of PhonePe Pulse Data: </h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    style_metric_cards(background_color='black', border_color='Teal', border_left_color="Teal")
    total_reg_users = tbls['top_user_dist']['Registered_users'].sum()
    col1.metric(
                label = 'Total Registered Users',
                value = '{:.2f} Cr'.format(total_reg_users/10000000),
                delta = 'Forward Trend',
                )

    total_app_opens = tbls['map_user']['App_opens'].sum()
    col2.metric(
                label = 'Total App Opens', 
                value = '{:.2f} Cr'.format(total_app_opens/10000000),
                delta = 'Forward Trend'
                )
    agg_trans = tbls['agg_tran']['Transaction_count'].sum()
    col3.metric(label = 'Total Transaction Count', value = '{:.2f} Cr'.format(agg_trans/10000000), delta = 'Forward Trend')

    agg_trans =tbls['agg_tran']['Transaction_amount'].sum()
    col4.metric(label = 'Total Transaction Amount', value = '{:.2f} K Cr.'.format(agg_trans/10000000000), delta = 'Forward Trend')
    add_vertical_space(1)

    
    Tran_type = tbls['agg_tran'].groupby(['Transaction_type'])['Transaction_count'].sum()

    san = []
    for type, count in Tran_type.items():
        label = type
        value = '{:.2f} Cr'.format(count / 10000000)
        delta = 'Forward Trend'
        san.append((label, value, delta))

    # Split the screen into columns
    columns = st.columns(len(san))

    # Create and display metrics in the columns
    for i, (label, value, delta) in enumerate(san):
        with columns[i]:
            st.metric(label=f'{label} Tran_count', value=value, delta=delta)

    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center; font-size: 30px;color: #dd9933;font-family:PhonePeSans;'>Key Primary Observations  </h3>", unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:left; font-size: 20px;color: #dd9933;font-family:PhonePeSans;'>Let's explore some fundamental findings from the Phonepe Pulse data.  </h3>", unsafe_allow_html=True)

    Ques_0 = '👇 --Select--👇'
    Ques_1 = '1. What are the top regions based on both transaction count and transaction amount?'
    Ques_2 = '2. What is the transaction count breakdown by transaction type, and compare year by year?'
    Ques_3 = "3. What is the transaction count categorized by brand?"
    Ques_4 = "4. What are the top 10 states based on year and transaction amount with an option to analyze the data by State and quarter wise?"
    Ques_5 = '5. What are the Top 10 districts based on Year and transactions amount with an option to  drill down the data by State and quarter wise? '
    Ques_6 = '6. What is the transaction count determined by the brand with option to narrow down the data based on State, year, and quarter?'
    Ques_7 = "7. Which are the top 10 states where the PhonePe app is predominantly used? Included the filter to analyze the data by State, year, and quarter wise."
    Ques_8 = '8. How does the transaction amount vary when comparing different regions?'
    Ques_9 = '9. What are the key districts with the highest concentration of registered users? Included the filter to drill down the data by State and quarter wise.'
    Ques_10 ='10. What are the Top 10 Pincodes based on Year and transactions amount? '

    ques = st.selectbox('Lets find something..!🕵️‍♂️',(Ques_0,Ques_1,Ques_2,Ques_3,Ques_4,Ques_5,Ques_6,Ques_7,Ques_8,Ques_9,Ques_10))
    

    Dir, SQL = st.tabs(['Direct Data', 'Data from MYSQL'])
    with Dir:
        if ques==Ques_1:
            agg_trans_data = tbls['agg_tran'].groupby('Region').agg({'Transaction_amount': 'sum', 'Transaction_count': 'sum'}).reset_index()
            agg_trans_data['Transaction_count']=round(agg_trans_data['Transaction_count']/1e10,2)
            agg_trans_data['Transaction_amount']=round(agg_trans_data['Transaction_amount']/1e10,2)

            agg_trans_data1=tbls['agg_tran'].groupby('Year')['Transaction_count'].sum().reset_index()
            agg_trans_data1['Transaction_count']=round(agg_trans_data1['Transaction_count'] / 10000000,2)

            st.markdown("<h3 style='text-align:center; font-size: 30px;color: #dd9933;font-family:PhonePeSans;'>Transaction Count and Amount by Region  </h3>", unsafe_allow_html=True)
            st.info("The Southern region holds a prominent position over all other regions in terms of Transaction Count.")
            agg_col1,agg_col2,agg_col3=st.columns([3,0.1,3])
            qry_df = SQL_QRY('SELECT Region, SUM(Transaction_amount) as Amount, SUM(Transaction_count) as Count FROM agg_tran  GROUP BY Region')

            agg_col1.plotly_chart(
            create_plotly_charts( qry_df,'Pie','Region','Count',
            grid=False,hole=0.55,color_discrete_sequence=px.colors.sequential.Magma)
            .update_traces(visible=True,textfont=dict(size=15, color='grey'),hoverinfo='label+percent+value',customdata=qry_df['Amount'],hovertemplate='<b>%{label}</b><br>Transaction Count: %{value:,.2f} Billion  </br> Transaction Amount: ₹ %{customdata:.2f} Billion', 
                          hoverlabel=dict( font_size=14, font_family="Arial" ))
            .update_layout(width=400, height=400,legend=dict(font=dict(size=14,color='white')) ,  legend_title_text='Regions',title="Transaction Count", title_x=0.5,title_y=0.95),
            use_container_width=False)   
        
            agg_col2.markdown("<div style='border-left: 3px solid #5f1f9c;font-family:PhonePeSans; height: 380px;'></div>", unsafe_allow_html=True)

            agg_col3.plotly_chart(
                create_plotly_charts(qry_df,'Pie','Region','Amount',
                grid=False,hole=0.55,color_discrete_sequence=px.colors.sequential.Magma)
                .update_traces(visible=True,textfont=dict(size=15, color='#FFFFFF'),hoverinfo='label+percent+value',customdata=qry_df['Count'],hovertemplate='<b>%{label}</b><br>Transaction Amount: %{value:,.2f} Billion. </br> Transaction Count: ₹ %{customdata:.2f} Billion',  
                              hoverlabel=dict( font_size=14, font_family="Arial" ))
                .update_layout(width=400, height=400,legend=dict(font=dict(size=14,color='white')),legend_title_text='Regions',title="Transaction Amount",title_x=0.3,title_y=0.95),
                use_container_width=False)

            expand = st.expander(label = 'Detailed view',expanded=True)
            expand_data = (agg_trans_data.loc[:, ['Region', 'Transaction_count', 'Transaction_amount']].reset_index(drop=True))
            expand_data.index +=1
            expand.write(expand_data)

        if ques==Ques_2:
            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)
            type_col1, type_col2, type_col3=st.columns([2.5,0.01,3])
        
            agg_trans_data2=tbls['agg_tran'].groupby(['Transaction_type','Year'])['Transaction_count'].sum().reset_index()
            agg_trans_data2['Transaction_count']=round(agg_trans_data2['Transaction_count'] / 10000000,2)
            agg_trans_data3=tbls['agg_tran'].groupby('Transaction_type')['Transaction_count'].sum().reset_index().sort_values(by='Transaction_count',ascending=False)
            agg_trans_data3['Transaction_count']=round(agg_trans_data3['Transaction_count']/ 10000000,2)

            type_col1.markdown("<h3 style='text-align:center; font-size: 30px;color: #dd9933;font-family:PhonePeSans;'>Transaction Count in Cr. by  type  </h3>", unsafe_allow_html=True)
            type_col1.info("The Merchant  payment holds a prominent position over all transaction type.")

            type_col1.plotly_chart(
                create_plotly_charts(agg_trans_data3, 'Bar', 'Transaction_type', 'Transaction_count',
                                    grid=False,color='Transaction_type',text_auto=True,color_discrete_sequence=px.colors.sequential.Magma)
                                    .update_traces( visible=True, showlegend=False,textfont=dict(size=15),textfont_color='#FFFFFF',textposition='outside',texttemplate="₹%{y:,.2f} Cr",hoverlabel=dict(  font_size=14, font_family="Arial" ))
                                    .update_yaxes(title='Count in Crores',title_font=dict(size=18),tickfont=dict(size=15),ticksuffix=' Cr',tickprefix='₹')
                                    .update_xaxes(title='Transaction Type',title_font=dict(size=18),tickfont=dict(size=15)),
                                        use_container_width=True)
                                    

            type_col2.markdown("<div style='border-left: 3px solid #5f1f9c;font-family:PhonePeSans; height: 550px;'></div>", unsafe_allow_html=True)

            type_col3.markdown("<h3 style='text-align:center; font-size: 30px;color: #dd9933;font-family:PhonePeSans;'>Transaction  Count by Year and Type </h3>", unsafe_allow_html=True)
            type_col3.info("Yearly, overall transactions rise; Peer to Peer and Merchants notably grow by over 200%.")

            type_col3.plotly_chart(
                create_plotly_charts(agg_trans_data2, 'Bar', 'Year', 'Transaction_count',heightv=500,
                                    grid=False,color='Transaction_type',text_auto=True,color_discrete_sequence=px.colors.sequential.Magma)
                                    .update_traces( visible=True, showlegend=True,textfont=dict(size=14),textfont_color='#FFFFFF',textposition='outside',texttemplate="₹%{y:,.2f} Cr",hoverlabel=dict( font_size=14, font_family="Arial" ))
                                    .update_yaxes(title='Count in Crores',title_font=dict(size=18),tickfont=dict(size=15),ticksuffix=' Cr',tickprefix='₹')
                                    .update_layout(legend=dict(font=dict(size=14,color='white'))),
                                    use_container_width=True)


            type_col1.write(agg_trans_data3)
            type_col3.write(agg_trans_data2)

            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)


        if ques==Ques_3:
            user_col1,user_col2,user_col3=st.columns([3,0.001,3.1])


            agg_user = tbls['agg_user'].groupby('Brand')['Transaction_count'].sum().reset_index()
            t_hold=12388624
            small_brands = agg_user[agg_user['Transaction_count'] < t_hold]
            small_brands_sum = small_brands['Transaction_count'].sum()
            agg_user = agg_user[agg_user['Transaction_count'] >= t_hold]
            if 'Others' not in agg_user['Brand'].values:
                agg_user = pd.concat([agg_user, pd.DataFrame({'Brand': ['Others'], 'Transaction_count': [small_brands_sum]})], ignore_index=True)
                
                agg_user = agg_user.sort_values(by='Transaction_count')

            agg_user1 = tbls['agg_user'].groupby(["Year", "Brand"])['Transaction_count'].sum().reset_index()
            small_brands = agg_user1[agg_user1['Transaction_count'] < t_hold]
            small_brands_sum = small_brands['Transaction_count'].sum()
            agg_user1 = agg_user1[agg_user1['Transaction_count'] >= t_hold]
            if 'Others' not in agg_user1['Brand'].values:
                agg_user1 = pd.concat([agg_user1, pd.DataFrame({'Year': ['Others'], 'Transaction_count': [small_brands_sum]})], ignore_index=True)
                agg_user1 = agg_user1.sort_values(by=['Year', 'Transaction_count'], ascending=[True, True])


            others = pd.DataFrame({'Brand': ['Others'], 'Transaction_count': [small_brands['Transaction_count'].sum()]})
            agg_user1 = agg_user1[agg_user1['Transaction_count'] >= t_hold]
            agg_user1 = pd.concat([agg_user1, others], ignore_index=True)
            agg_user1['Transaction_count'] = round(agg_user1['Transaction_count'] / 1000000, 2)
            agg_users1 = agg_user1.sort_values(by='Year',ascending=True)  

            
            agg_user['Transaction_count']=round(agg_user['Transaction_count']/1000000,2)
            user_col1.markdown("<h3 style='text-align:center; font-size: 30px;color: #dd9933;font-family:PhonePeSans;'>Transaction Count in Cr. by  Brand  </h3>", unsafe_allow_html=True)
            user_col1.info("Xiaomi phones dominate, suggesting PhonePe's popularity extends to economically diverse users.")
            user_col1.plotly_chart(
                create_plotly_charts(agg_user, 'Bar', 'Transaction_count', 'Brand', grid=False, orientation='h',
                                    color='Transaction_count', color_continuous_scale='Magma',text='Transaction_count',)
                                    .update_layout( xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'})
                                    .update_traces( visible=True, showlegend=False,textfont=dict(size=12),textfont_color='#FFFFFF',textposition='outside',texttemplate="₹%{x:,.2f} Cr",hoverlabel=dict( font_size=14, font_family="Arial" ))
                                    .update_xaxes(title='Count in Crores',title_font=dict(size=18),tickfont=dict(size=14),tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹')
                                    .update_yaxes(title_font=dict(size=18),tickfont=dict(size=15))
                                    , use_container_width=True)
            
            user_col2.markdown("<div style='border-left: 3px solid #5f1f9c;font-family:PhonePeSans; height: 550px;'></div>", unsafe_allow_html=True)

            user_col3.markdown("<h3 style='text-align:center; font-size: 30px;color: #dd9933;font-family:PhonePeSans;'>Transaction  Count in Cr. by Brand, Year  </h3>", unsafe_allow_html=True)
            user_col3.info("The transaction count increases year by year, regardless of the device used.")
            user_col3.plotly_chart(
                create_plotly_charts(agg_users1, 'Bar', 'Transaction_count', 'Brand', grid=False, orientation='h',
                                    color="Transaction_count",hover_name='Year',
                                    hover_data = {'Brand':True,'Transaction_count':True},
                                    color_continuous_scale='Magma').update_layout(
                xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'})
                .update_xaxes(title='Count in Crores',title_font=dict(size=18),tickfont=dict(size=15),tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹')
                                    .update_yaxes(title_font=dict(size=18),tickfont=dict(size=15))
                                    .update_traces(hoverlabel=dict( font_size=14, font_family="Arial" ))
                , use_container_width=True)
            
            user_col1.write(agg_user)
            user_col3.write(agg_user1)

        if ques==Ques_4:

            top_dist_tran = tbls['top_tran_dist']
            df,qtr_opts,state_opts,year_opts=filter_list(top_dist_tran,suff=4)
            
            suffix1 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
            title3=f'Top 10 districts across {state_opts} state by Transactions count in {year_opts}, {qtr_opts}{suffix1}'

            df['Transaction_amount']=round(df['Transaction_amount']/10000000,2)
            dff= df.groupby("State")["Transaction_amount"].sum().nlargest(10).index.tolist()
            df = df[df["State"].isin(dff)]
            st.plotly_chart(
                    create_plotly_charts(
                        df,
                        'Bar',
                        'Transaction_amount',
                        'State',
                        widthv=900,
                        heightv=500,
                        grid=False,
                        color='Transaction_amount',
                        color_continuous_scale='Magma',
                        orientation='h',
                    ).update_xaxes(title_text='Amount in Crores',tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹', showgrid=False,title_font=dict(size=18),tickfont=dict(size=15))
                    .update_yaxes(title_text='', showgrid=False,title_font=dict(size=18),tickfont=dict(size=15)).update_layout(
                xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'},title={ 'text': title3, 'x': 0.45, 'xanchor': 'center', 'y': 0.94, 'yanchor': 'bottom' }
            ).update_traces(hoverlabel=dict(  font_size=14, font_family="Arial" )),
                    use_container_width=True
                )
            expander4  = st.expander(label = 'Top Transactions by State, Detailed view')
            expander4.write(df.loc[:, ['State', 'Year','Quarter', 'District','Transaction_amount']].reset_index(drop=True))

        if ques==Ques_5:
            top_dist_tran = tbls['top_tran_dist']
            df,qtr_opts,state_opts,year_opts=filter_list(top_dist_tran,suff=4)
            
            suffix1 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
            title3=f'Top 10 districts across {state_opts} state by Transactions count in {year_opts}, {qtr_opts}{suffix1}'

            df['Transaction_amount']=round(df['Transaction_amount']/10000000,2)
            dff= df.groupby("District")["Transaction_amount"].sum().nlargest(10).index.tolist()
            df = df[df["District"].isin(dff)]
            st.plotly_chart(
                    create_plotly_charts(
                        df,
                        'Bar',
                        'Transaction_amount',
                        'District',
                        widthv=900,
                        heightv=500,
                        grid=False,
                        color='Transaction_amount',
                        color_continuous_scale='Magma',
                        orientation='h',
                    ).update_xaxes(title_text='Amount in Crores',tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹', showgrid=False,title_font=dict(size=18),tickfont=dict(size=15))
                    .update_yaxes(title_text='', showgrid=False,title_font=dict(size=18),tickfont=dict(size=15)).update_layout(
                xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'},title={ 'text': title3, 'x': 0.45, 'xanchor': 'center', 'y': 0.94, 'yanchor': 'bottom' }
            ).update_traces(hoverlabel=dict(  font_size=14, font_family="Arial" )),
                    use_container_width=True
                )
            expander4  = st.expander(label = 'Top Transactions by State, Detailed view')
            expander4.write(df.loc[:, ['State', 'Year','Quarter', 'District','Transaction_amount']].reset_index(drop=True))

        if ques==Ques_6:
            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)
            agg_user = tbls['agg_user']
            df,qtr_opts,state_opts,year_opts=filter_list(agg_user,suff=22)

            df['count']=df['Transaction_count']/100000
        
            suffix4 = " quarters" if qtr_opts == 'All' else "st" if qtr_opts == 1 else "nd" if qtr_opts == 2 else "rd" if qtr_opts == 3 else "th"
            title4=f"Transaction Count in lakhs. and Percentage in {state_opts} for {qtr_opts}{suffix4} {'' if qtr_opts== 'All' else 'quarter'} of {year_opts}"

        
            t_map=create_plotly_charts(
            df,'Treemap',['Brand'],'count',color='Percentage',
            hover_data={'count':True,'Percentage': ':.2%','State':False,'Year':True,'Quarter':False},color_continuous_scale='phase',)
        
            t_map.update_layout(height=700,title = {"text": title4 ,'x': 0.45, 'xanchor': 'center','y': 0.89,'yanchor': 'bottom'})
            t_map.update_traces(marker=dict(cornerradius=5),hovertemplate='<b>%{label}</b><br>Transaction Count: %{customdata[0]:,.2f} lakhs<br>Percentage: %{customdata[1]:.2%}')
        
            st.plotly_chart(t_map.update_traces(hoverlabel=dict(  font_size=14, font_family="Arial" )),use_container_width=True)
        
            expander3 = st.expander(label = 'Transaction Count  Percentage by Brand, Detailed view')
            expander3.write(df.loc[:, ['State', 'Year','Quarter', 'Brand','Transaction_count','Percentage']].reset_index(drop=True))

        if ques==Ques_7:
            map_user=tbls['map_user']
            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)


        
        
            df,qtr_opts,state_opts,year_opts=filter_list(map_user,suff=23)
        
            if state_opts !='All':
                zoom_level = 6
                center_lat = df[df["State"] == state_opts]["Latitude"].mean() 
                center_lon = df[df["State"] == state_opts]["Longitude"].mean()
                rad=10

            else:
                zoom_level = 3.5
                center_lat = 23.5937 
                center_lon =78.9629
                rad=10

            suffix7 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
            title7=f'App opens Hotspot  across {state_opts} state  in {year_opts}, {qtr_opts}{suffix7} <br>(App Opens count in Lakhs & Registered user count in Lakhs)'


            if year_opts == '2018':
                add_vertical_space(1)
                st.info('No Data for the year 2018')
                add_vertical_space(1)
                expanded=True

            elif (year_opts=='2019') & (qtr_opts==1):
                add_vertical_space(1)
                st.info('No Data for the year 2019, Quarter 1')
                add_vertical_space(1)
                expanded=True

            else:
                reg_user_plot = px.density_mapbox(df, lat='Latitude', lon='Longitude', z='App_opens', opacity=.6, color_continuous_scale='Magma', 
                                                    mapbox_style="carto-positron", radius=rad, hover_data={"Latitude": False, "Longitude": False, "District": True, "App_opens": True, 'Registered_users':True,'Region':True}, 
                                                    hover_name='District', center=dict(lat=0, lon=180), zoom=zoom_level)
                reg_user_plot   .update_layout( mapbox_zoom=zoom_level,  geo=dict(scope='asia', projection_type='equirectangular'), mapbox_center={"lat": center_lat, "lon": center_lon}, margin={"r": 0, "t": 0, "l": 0, "b": 0}, width=800, height=550)
                reg_user_plot.update_traces(hovertemplate='<b>%{hovertext}</b><br>App Opens: %{z:,.2f} Lakhs<br>Registered Users: %{customdata[3]:,.2f} Lakhs<br>Region - %{customdata[4]}')
                reg_user_plot  .add_annotation(go.layout.Annotation( text=title7,
                align='center',
                showarrow=False,
                xref='paper',
                yref='paper',
                x=0.5,
                y=1.001,
                font=dict(color='black',size=18,family='Balto'),
                bgcolor='white',  
                borderpad=6,
                opacity=0.8,
                bordercolor='black',
                borderwidth=2,
            )
            )
                st.plotly_chart(reg_user_plot, use_container_width=True)
                expanded=False

            st.expander1 = st.expander(label='App opens Hotspots Detailed view',expanded=expanded)
            st.expander1.write(df.loc[:, ['State', 'District', 'Year', 'App_opens','Registered_users']].reset_index(drop=True))

            
        if ques==Ques_8:
            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

            trans_df1 = trans_df2 =tbls['agg_tran']
            
            title ='Regionwise Transaction amount in Trillions'

            trans_df1['Transaction_amt']=round(trans_df1['Transaction_amount']/1e12,2)
            ab=create_plotly_charts(trans_df1,'Treemap',['Region','Year'],'Transaction_amt' ,color='Transaction_amount',color_continuous_scale='curl',hover_data={'Transaction_amt': True,'Transaction_amount':True,})
            ab.update_layout( height=500,title = {"text": title ,'x': 0.45, 'xanchor': 'center','y': 0.847,'yanchor': 'bottom','font':dict(color='#ffffff')},).update_traces(marker=dict(cornerradius=11),root_color="red",hovertemplate='<b>%{label}</b><br>Transaction Amount: %{customdata[0]:,.2f} Trillions.')
            ab.update_coloraxes(showscale=False) 

            st.plotly_chart(ab,use_container_width=True)
    

            trans_df11=trans_df1.groupby('Region')["Transaction_amount"].sum()
            st.dataframe(trans_df11)
            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)


        if ques==Ques_9:
            map_user = tbls['map_user']
            map_user['Registered_users'] = map_user['Registered_users'] / 100000
            map_user['App_opens'] = map_user['App_opens'] / 100000
            df, qtr_opts, state_opts, year_opts = filter_list(map_user, suff=24)

            if state_opts != 'All':
                zoom_level = 5
                center_lat = df[df["State"] == state_opts]["Latitude"].mean()
                center_lon = df[df["State"] == state_opts]["Longitude"].mean()
            else:
                zoom_level = 3.5
                center_lat = 23.5937
                center_lon = 78.9629

            suffix5 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
            chart_title1 = f"""{state_opts} Registered user hotspots for {qtr_opts}{suffix5} of {year_opts}.<br>(Registered users in Lakhs & App Opens in Lakhs)"""

            reg_user_plot = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', size='Registered_users',
                                            color='Registered_users', size_max=25, hover_data={"Longitude": False, "Latitude": False, "Registered_users": True, "App_opens": True, 'Region': False},
                                            text='District', color_continuous_scale='Viridis', )

            reg_user_plot.add_annotation(go.layout.Annotation(text=chart_title1,
                                                            align='center',
                                                            showarrow=False,
                                                            xref='paper',
                                                            yref='paper',
                                                            x=0.5,
                                                            y=1.001,
                                                            font=dict(color='black', size=18, family='Balto'),
                                                            bgcolor='#ffffff',
                                                            borderpad=6,
                                                            opacity=0.8,
                                                            bordercolor='#000000',
                                                            borderwidth=2,
                                                            )
                                        )
            reg_user_plot.update_layout(mapbox_style='carto-positron', mapbox_zoom=zoom_level, mapbox_center={"lat": center_lat, "lon": center_lon},
                                        geo=dict(scope='asia', projection_type='equirectangular'),
                                        margin={"r": 0, "t": 0, "l": 0, "b": 0}, width=400, height=500)
            reg_user_plot.update_traces(
                hovertemplate='<b>%{text}</b><br>Registered users -  %{customdata[2]:,.2f} Lakhs<br>App_opens - %{customdata[3]:,.2f} Lakhs<br>Region - %{customdata[4]}'
            )

            st.plotly_chart(reg_user_plot, use_container_width=True)

            expander22 = st.expander(label='Registered user Hotspots Detailed view')
            expander22.write(df.loc[:, ['State', 'District', 'Year', 'Quarter', 'Registered_users', 'App_opens']].reset_index(drop=True))

            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

        if ques==Ques_10:
            pin_tran=tbls['top_tran_pin']
            filtered_top_pin=pin_tran.groupby('Pincode')['Transaction_amount'].sum().reset_index().sort_values('Transaction_amount',ascending=False).head(10)
            
            filtered_top_pin['Transaction_amount']=filtered_top_pin['Transaction_amount']/10000000
            title17 = f"Top 10 pincode locations by Transaction volume. Value in Crores"
            st.plotly_chart(
            create_plotly_charts(
                filtered_top_pin,
                'Bar',
                'Transaction_amount',
                'Pincode',
                widthv=900,
                heightv=500,
                grid=False,
                color='Transaction_amount',
                color_continuous_scale='curl',
                orientation='h',
            ).update_xaxes(title_text='', showgrid=False,tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹')
            .update_yaxes(title_text='', showgrid=False)
                        .update_traces(texttemplate="₹%{x:,.2f} Cr",hovertemplate='<br>Transaction Amount: ₹%{x:,.2f} Cr')

            .update_layout(yaxis_type='category',xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'},title={ 'text': title17, 'x': 0.4, 'xanchor': 'center', 'y': 0.94, 'yanchor': 'bottom' }
    ),
            use_container_width=True
        )
            expander11=st.expander(label=title17)
            expander11.dataframe(filtered_top_pin.reset_index(drop = True))

    with SQL:
        if ques==Ques_1:

            qry_df2=SQL_QRY('SELECT Region, SUM(Transaction_count) as Transactions, SUM(Transaction_amount) AS Amount FROM agg_tran GROUP BY Region;')

            # qry_df2['Tran in Cr.']=qry_df2['Transactions'].astype(float)
            qry_df2['Transactions']=round(qry_df2['Transactions'].astype(float)/1e10,2)
            qry_df2 = qry_df2.sort_values(by='Transactions',ascending=False)

        
            qry_df2['Amount']=round(qry_df2['Amount']/1e10,2)

            # agg_trans_data1=tbls['agg_tran'].groupby('Year')['Transaction_count'].sum().reset_index()
            # agg_trans_data1['Transaction_count']=round(agg_trans_data1['Transaction_count'] / 10000000,2)

            st.markdown("<h3 style='text-align:center; font-size: 30px;color: #dd9933;font-family:PhonePeSans;'>Transaction Count and Amount by Region  </h3>", unsafe_allow_html=True)
            st.info("The Southern region holds a prominent position over all other regions in terms of Transaction Count.")
            agg_col1,agg_col2,agg_col3=st.columns([3,0.1,3])
            qry_df = SQL_QRY('SELECT Region, SUM(Transaction_amount) as Amount, SUM(Transaction_count) as Count FROM agg_tran  GROUP BY Region')

            agg_col1.plotly_chart(
            create_plotly_charts( qry_df2,'Pie','Region','Transactions',
            grid=False,hole=0.55,color_discrete_sequence=px.colors.sequential.Magma)
            .update_traces(visible=True,textfont=dict(size=15, color='#FFFFFF'),hoverinfo='label+percent+value',customdata=qry_df2['Amount'],hovertemplate='<b>%{label}</b><br>Transaction Count: %{value:,.2f} Billion  </br> Transaction Amount: ₹ %{customdata:.2f} Billion',  )
            .update_layout(width=400, height=400,   legend_font=dict(size=13),legend_title_text='Regions',title="Transaction Count", title_x=0.5,title_y=0.95),
            use_container_width=False)   
        
            agg_col2.markdown("<div style='border-left: 3px solid #5f1f9c;font-family:PhonePeSans; height: 380px;'></div>", unsafe_allow_html=True)

            agg_col3.plotly_chart(
                create_plotly_charts(qry_df2,'Pie','Region','Amount',
                grid=False,hole=0.55,color_discrete_sequence=px.colors.sequential.Magma)
                .update_traces(visible=True,textfont=dict(size=15, color='#FFFFFF'),hoverinfo='label+percent+value',customdata=qry_df2['Transactions'],hovertemplate='<b>%{label}</b><br>Transaction Amount: %{value:,.2f} Billion. </br> Transaction Count: ₹ %{customdata:.2f} Billion',  )
                .update_layout(width=400, height=400,legend_font=dict(size=13),legend_title_text='Regions',title="Transaction Amount",title_x=0.3,title_y=0.95),
                use_container_width=False)
            st.write(qry_df2.to_html(index=False), unsafe_allow_html=True)


        if ques==Ques_2:
            qry_df3=SQL_QRY('SELECT  Transaction_type, SUM(Transaction_count) as Transactions  FROM agg_tran GROUP BY Transaction_type;')            
            qry_df4=SQL_QRY('SELECT Year, Transaction_type, SUM(Transaction_amount) AS Amount FROM agg_tran GROUP BY Year,Transaction_type;')            

            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)
            type_col1, type_col2, type_col3=st.columns([2.5,0.01,3])
        
            qry_df3['Trans_Cr.']=round(qry_df3['Transactions'] .astype(float)/ 10000000,2)
            qry_df4['Amt_Trillions']=round(qry_df4['Amount']/ 1000000000000,2)

            type_col1.markdown("<h3 style='text-align:center; font-size: 30px;color: #dd9933;font-family:PhonePeSans;'>Transaction Count in Cr. by  type  </h3>", unsafe_allow_html=True)
            type_col1.info("The Merchant  payment holds a prominent position over all transaction type.")
            
            
        

            type_col1.plotly_chart(
                create_plotly_charts(qry_df3, 'Bar', 'Transaction_type', 'Trans_Cr.',
                                    grid=False,color='Transactions',text_auto=True,color_discrete_sequence=px.colors.sequential.Magma)
                                    .update_traces( visible=True, showlegend=False,textfont=dict(size=15),textfont_color='#FFFFFF',textposition='outside',texttemplate="%{y:,.2f} Cr",)
                                    .update_yaxes(title='Count in Crores',title_font=dict(size=18),tickfont=dict(size=15),ticksuffix=' Cr',tickprefix='')
                                    .update_xaxes(title='Transaction Type',title_font=dict(size=18),tickfont=dict(size=15)),
                                        use_container_width=True)

            type_col2.markdown("<div style='border-left: 3px solid #5f1f9c;font-family:PhonePeSans; height: 630px;'></div>", unsafe_allow_html=True)

            type_col3.markdown("<h3 style='text-align:center; font-size: 30px;color: #dd9933;font-family:PhonePeSans;'>Transaction  Count by Year and Type </h3>", unsafe_allow_html=True)
            type_col3.info("Yearly, overall transactions rise; Peer to Peer and Merchants notably grow by over 200%.")

            type_col3.plotly_chart(
                create_plotly_charts(qry_df4, 'Bar', 'Year', 'Amt_Trillions',heightv=500,
                                    grid=False,color='Transaction_type',text_auto=True,color_discrete_sequence=px.colors.sequential.Magma)
                                    .update_traces( visible=True, showlegend=True,textfont=dict(size=14),textfont_color='#FFFFFF',textposition='outside',texttemplate="₹%{y:,.2f} T")
                                    .update_yaxes(title='Amount in Trillions',title_font=dict(size=18),tickfont=dict(size=15),ticksuffix='T',tickprefix='₹'),
                                    use_container_width=True)

            type_col1.markdown("<br>", unsafe_allow_html=True)
            type_col1.markdown("<br>", unsafe_allow_html=True)

            type_col1.write(qry_df3.to_html(index=False), unsafe_allow_html=True)
            type_col3.write(qry_df4.to_html(index=False), unsafe_allow_html=True)

            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)


        if ques==Ques_3:
            user_col1,user_col2,user_col3=st.columns([3,0.001,3.1])
            
            qry_df=SQL_QRY('SELECT brand, SUM(Transaction_count) AS Transactions FROM agg_user GROUP BY brand;')

            qry_df['Tran in Cr.']=qry_df['Transactions'].astype(float)
            qry_df['Tran in Cr.']=round(qry_df['Tran in Cr.']/1000000,2)
            qry_df = qry_df.sort_values(by='Transactions',ascending=False)
            
            user_col1.markdown("<h3 style='text-align:center; font-size: 30px;color: #dd9933;font-family:PhonePeSans;'>Transaction Count in Cr. by  Brand  </h3>", unsafe_allow_html=True)
            user_col1.info("Xiaomi phones dominate, suggesting PhonePe's popularity extends to economically diverse users.")
            user_col1.plotly_chart(
                create_plotly_charts(qry_df, 'Bar', 'Tran in Cr.', 'brand', grid=False, orientation='h',hover_name='brand',
                                    color='Transactions', color_continuous_scale='Magma',text='Tran in Cr.',)
                                    .update_layout( xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'})
                                    .update_traces( visible=True, showlegend=False,textfont=dict(size=12),textfont_color='#FFFFFF',textposition='outside',texttemplate="%{x:,.2f} Cr")
                                    .update_xaxes(title='Count in Crores',title_font=dict(size=18),tickfont=dict(size=14),tickformat=",.2f ",ticksuffix=' Cr',tickprefix=' ')
                                    .update_yaxes(title_font=dict(size=18),tickfont=dict(size=15))
                                    , use_container_width=True)
            
            qry_df1=SQL_QRY('SELECT Region, brand, SUM(Transaction_count) AS Transaction_count FROM agg_user GROUP BY Region , brand;')
            

            qry_df1['Count in Cr.']=round(qry_df1['Transaction_count'].astype(float)/10000000,2)
            qry_df1 = qry_df1.sort_values(by='Count in Cr.',ascending=False)

            user_col2.markdown("<div style='border-left: 3px solid #5f1f9c;font-family:PhonePeSans; height: 550px;'></div>", unsafe_allow_html=True)

            user_col3.markdown("<h3 style='text-align:center; font-size: 30px;color: #dd9933;font-family:PhonePeSans;'>Transaction  Count in Cr. by Brand, Year  </h3>", unsafe_allow_html=True)
            user_col3.info("Southern region dominates irrespective of devices")
            user_col3.plotly_chart(
                create_plotly_charts(qry_df1, 'Bar', 'Count in Cr.', 'brand', grid=False, orientation='h',
                                    color="Count in Cr.",hover_name='Region',
                                    hover_data = {'brand':True,'Count in Cr.':True},
                                    color_continuous_scale='Magma').update_layout(
                xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'})
                .update_traces( visible=True, showlegend=False,textfont=dict(size=12),textfont_color='#FFFFFF',textposition='outside',texttemplate="%{x:,.2f} Cr")

                .update_xaxes(title='Count in Cr.',title_font=dict(size=18),tickfont=dict(size=15),tickformat=",.2f ",ticksuffix=' Cr',tickprefix=' ')
                                    .update_yaxes(title_font=dict(size=18),tickfont=dict(size=15))
                , use_container_width=True)
            
            user_col1.write(qry_df.to_html(index=False), unsafe_allow_html=True)
            user_col3.write(qry_df1.to_html(index=False), unsafe_allow_html=True)



        if ques==Ques_4:
            qry_df5=SQL_QRY('SELECT Year, Quarter, State, SUM(Transaction_count) AS Transactions,SUM(Transaction_amount) AS Amount FROM top_tran_dist GROUP BY Year, Quarter, State;')

            df,qtr_opts,state_opts,year_opts=filter_list(qry_df5,suff=88)
            df['Year']=df['Year'].astype(int)
            suffix1 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
            title3=f'Top 10 districts across {state_opts} state by Transactions count in {year_opts}, {qtr_opts}{suffix1}'

            df['Amt_Cr']=round(df['Amount']/10000000,2)
            dff= df.groupby("State")["Amount"].sum().nlargest(10).index.tolist()
            df = df[df["State"].isin(dff)]
            st.plotly_chart(
                    create_plotly_charts(
                        df,
                        'Bar',
                        'Amt_Cr',
                        'State',
                        widthv=900,
                        heightv=500,
                        grid=False,
                        color='Amt_Cr',
                        color_continuous_scale='Phase',
                        orientation='h',
                    ).update_xaxes(title_text='Amount in Crores',tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹', showgrid=False,title_font=dict(size=18),tickfont=dict(size=15))
                    .update_yaxes(title_text='', showgrid=False,title_font=dict(size=18),tickfont=dict(size=15)).update_layout(
                xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'},title={ 'text': title3, 'x': 0.45, 'xanchor': 'center', 'y': 0.94, 'yanchor': 'bottom' }
            ),
                    use_container_width=True
                )
            expander4  = st.expander(label = 'Top Transactions by State, Detailed view')
            expander4.write(df.loc[:, ['State', 'Year','Quarter','Amount']].reset_index(drop=True))

        if ques==Ques_5:
            qry_df6=SQL_QRY('SELECT Year, Quarter, State, District, SUM(Transaction_count) AS Transactions,SUM(Transaction_amount) AS Amount FROM top_tran_dist GROUP BY Year, Quarter, State,District;')

            df,qtr_opts,state_opts,year_opts=filter_list(qry_df6,suff=98)
            df['Year']=df['Year'].astype(int)
            suffix1 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
            title3=f'Top 10 districts across {state_opts} state by Transactions count in {year_opts}, {qtr_opts}{suffix1}'

            df['Amt_Cr']=round(df['Amount']/10000000,2)
            dff= df.groupby("District")["Amount"].sum().nlargest(10).index.tolist()
            df = df[df["District"].isin(dff)]
            st.plotly_chart(
                    create_plotly_charts(
                        df,
                        'Bar',
                        'Amt_Cr',
                        'District',
                        widthv=900,
                        heightv=500,
                        grid=False,
                        color='Amt_Cr',
                        color_continuous_scale='Plasma',
                        orientation='h',
                    ).update_xaxes(title_text='Amount in Crores',tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹', showgrid=False,title_font=dict(size=18),tickfont=dict(size=15))
                    .update_yaxes(title_text='', showgrid=False,title_font=dict(size=18),tickfont=dict(size=15)).update_layout(
                xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'},title={ 'text': title3, 'x': 0.45, 'xanchor': 'center', 'y': 0.94, 'yanchor': 'bottom' }
            ),
                    use_container_width=True
                )
            expander44  = st.expander(label = 'Top Transactions by State, Detailed view')
            expander44.write(df.loc[:, ['State', 'District','Year','Quarter','Amount']].reset_index(drop=True))

        if ques==Ques_6:
            qry_df7=SQL_QRY('SELECT Year, Quarter, Brand, State, SUM(Transaction_count) AS Transaction_count,sum(Percentage) as Percentage FROM agg_user GROUP BY Year, Quarter, Brand, State;')

            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)
            df,qtr_opts,state_opts,year_opts=filter_list(qry_df7,suff=89)

            df['count']=df['Transaction_count']/100000
        
            suffix4 = " quarters" if qtr_opts == 'All' else "st" if qtr_opts == 1 else "nd" if qtr_opts == 2 else "rd" if qtr_opts == 3 else "th"
            title4=f"Transaction Count in lakhs. and Percentage in {state_opts} for {qtr_opts}{suffix4} {'' if qtr_opts== 'All' else 'quarter'} of {year_opts}"

        
            t_map=create_plotly_charts(
            df,'Treemap',['Brand'],'count',color='Percentage',
            hover_data={'count':True,'Percentage': ':.2%','State':False,'Year':True,'Quarter':False},color_continuous_scale='phase',)
        
            t_map.update_layout(height=700,title = {"text": title4 ,'x': 0.45, 'xanchor': 'center','y': 0.89,'yanchor': 'bottom'})
            t_map.update_traces(marker=dict(cornerradius=5),hovertemplate='<b>%{label}</b><br>Transaction Count: %{customdata[0]:,.2f} lakhs<br>Percentage: %{customdata[1]:.2%}')
        
            st.plotly_chart(t_map,use_container_width=True)
        
            expander33 = st.expander(label = 'Transaction Count  Percentage by Brand, Detailed view')
            expander33.write(df.loc[:, ['State', 'Year','Quarter', 'Brand','Transaction_count','Percentage']].reset_index(drop=True))

        if ques==Ques_7:
            qry_df8=SQL_QRY('SELECT Year, Quarter, Region,State, District, SUM(Registered_users) AS Registered_users,SUM(App_opens) AS App_opens,Latitude,Longitude FROM map_user GROUP BY Year, Quarter, Region,State,District,Latitude,Longitude;')

            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)        
        
            df,qtr_opts,state_opts,year_opts=filter_list(qry_df8,suff=90)


            if state_opts !='All':
                zoom_level = 6
                center_lat = df[df["State"] == state_opts]["Latitude"].mean() 
                center_lon = df[df["State"] == state_opts]["Longitude"].mean()
                rad=10

            else:
                zoom_level = 3.5
                center_lat = 23.5937 
                center_lon =78.9629
                rad=10

            suffix7 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
            title7=f'App opens Hotspot  across {state_opts} state  in {year_opts}, {qtr_opts}{suffix7} <br>(App Opens count in Lakhs & Registered user count in Lakhs)'


            if year_opts == '2018':
                add_vertical_space(1)
                st.info('No Data for the year 2018')
                add_vertical_space(1)
                expanded=True

            elif (year_opts=='2019') & (qtr_opts==1):
                add_vertical_space(1)
                st.info('No Data for the year 2019, Quarter 1')
                add_vertical_space(1)
                expanded=True

            else:
                reg_user_plot = px.density_mapbox(df, lat='Latitude', lon='Longitude', z='App_opens', opacity=.3, color_continuous_scale='Viridis', 
                                                    mapbox_style="carto-positron", radius=rad, hover_data={"Latitude": False, "Longitude": False, "District": True, "App_opens": True, 'Registered_users':True,'Region':True}, 
                                                    hover_name='District', center=dict(lat=0, lon=180), zoom=zoom_level)
                reg_user_plot   .update_layout( mapbox_zoom=zoom_level,  geo=dict(scope='asia', projection_type='equirectangular'), mapbox_center={"lat": center_lat, "lon": center_lon}, margin={"r": 0, "t": 0, "l": 0, "b": 0}, width=800, height=550)
                reg_user_plot.update_traces(hovertemplate='<b>%{hovertext}</b><br>App Opens: %{z:,.2f} Lakhs<br>Registered Users: %{customdata[3]:,.2f} Lakhs<br>Region - %{customdata[4]}')
                reg_user_plot  .add_annotation(go.layout.Annotation( text=title7,
                align='center',
                showarrow=False,
                xref='paper',
                yref='paper',
                x=0.5,
                y=1.001,
                font=dict(color='black',size=18,family='Balto'),
                bgcolor='#ffffff',  
                borderpad=6,
                opacity=0.8,
                bordercolor='#000000',
                borderwidth=2,
            )
            )
                st.plotly_chart(reg_user_plot, use_container_width=True)
                expanded=False

            st.expander11= st.expander(label='App opens Hotspots Detailed view',expanded=expanded)
            st.expander11.write(df.loc[:, ['State', 'District', 'Year', 'App_opens','Registered_users']].reset_index(drop=True))

            
        if ques==Ques_8:
            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)
            qry_df8=SQL_QRY('SELECT Year,Region, State,  SUM(Transaction_amount) AS Transaction_amount FROM agg_tran GROUP BY Year, Region, State;')


            
            title ='Regionwise Transaction amount in Trillions'

            qry_df8['Amt_Tri']=round(qry_df8['Transaction_amount']/1e12,2)
            ab=create_plotly_charts(qry_df8,'Treemap',['Region','Year'],'Amt_Tri' ,color='Amt_Tri',color_continuous_scale='curl',hover_data={'Amt_Tri': True,'Transaction_amount':True,})
            ab.update_layout( height=500,title = {"text": title ,'x': 0.45, 'xanchor': 'center','y': 0.847,'yanchor': 'bottom','font':dict(color='#ffffff')},).update_traces(marker=dict(cornerradius=11),root_color="red",hovertemplate='<b>%{label}</b><br>Transaction Amount: %{customdata[0]:,.2f} Trillions.')
            ab.update_coloraxes(showscale=False) 

            st.plotly_chart(ab,use_container_width=True)
    
            qry_df8 = qry_df8.groupby('Region').agg({'Transaction_amount': 'sum'}).reset_index()
            st.expander11= st.expander(label='Regionwise Transaction amount',expanded=False)
            st.expander11.write(qry_df8.loc[:, ['Region', 'Transaction_amount']].reset_index(drop=True))

            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)


        if ques==Ques_9:

            qry_df9=SQL_QRY('SELECT Year,Quarter,Region, Latitude,Longitude,State,  District, SUM(Registered_users) AS Registered_users,SUM(App_opens) AS App_opens FROM map_user GROUP BY Year,Quarter,Region, Latitude,Longitude,State,  District;')
     
 
            df, qtr_opts, state_opts, year_opts = filter_list(qry_df9, suff=91)
            df['Year'] = df['Year'].astype(str).str.strip().str.replace(',', '').astype(int)
            columns_to_convert = ['Registered_users', 'App_opens','Year']
            col_to_con = ['Latitude', 'Longitude',]
            df[columns_to_convert] = df[columns_to_convert].astype(int)
            df[col_to_con]=df[col_to_con].astype(float)

            if state_opts != 'All':
                zoom_level = 5
                center_lat = df[df["State"] == state_opts]["Latitude"].mean()
                center_lon = df[df["State"] == state_opts]["Longitude"].mean()
            else:
                zoom_level = 3.5
                center_lat = 23.5937
                center_lon = 78.9629

            suffix5 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
            chart_title1 = f"""{state_opts} Registered user hotspots for {qtr_opts}{suffix5} of {year_opts}.<br>(Registered users in Lakhs & App Opens in Lakhs)"""

            reg_user_plot = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', size='Registered_users',
                                            color='Registered_users', size_max=17, hover_data={"Longitude": False, "Latitude": False, "Registered_users": True, "App_opens": True, 'Region': False},
                                            text='District', color_continuous_scale='Rainbow', )

            reg_user_plot.add_annotation(go.layout.Annotation(text=chart_title1,
                                                            align='center',
                                                            showarrow=False,
                                                            xref='paper',
                                                            yref='paper',
                                                            x=0.5,
                                                            y=1.001,
                                                            font=dict(color='black', size=18, family='Balto'),
                                                            bgcolor='#ffffff',
                                                            borderpad=6,
                                                            opacity=0.8,
                                                            bordercolor='#000000',
                                                            borderwidth=2,
                                                            )
                                        )
            reg_user_plot.update_layout(mapbox_style='carto-positron', mapbox_zoom=zoom_level, mapbox_center={"lat": center_lat, "lon": center_lon},
                                        geo=dict(scope='asia', projection_type='equirectangular'),
                                        margin={"r": 0, "t": 0, "l": 0, "b": 0}, width=400, height=500)
            reg_user_plot.update_traces(
                hovertemplate='<b>%{text}</b><br>Registered users -  %{customdata[2]:,.2f} Lakhs<br>App_opens - %{customdata[3]:,.2f} Lakhs<br>Region - %{customdata[4]}'
            )

            st.plotly_chart(reg_user_plot, use_container_width=True)

            expander22 = st.expander(label='Registered user Hotspots Detailed view')
            expander22.write(df.loc[:, ['State', 'District', 'Year', 'Quarter', 'Registered_users', 'App_opens']].reset_index(drop=True))

            st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

        if ques==Ques_10:
            qry_df10=SQL_QRY('SELECT Pincode, SUM(Transaction_amount) AS Transaction_amount FROM top_tran_pin GROUP BY Pincode;')

            pin_tran=tbls['top_tran_pin']
            qry_df10_fil=qry_df10.groupby('Pincode')['Transaction_amount'].sum().reset_index().sort_values('Transaction_amount',ascending=False).head(10)
            
            qry_df10_fil['Transaction_amount']=qry_df10_fil['Transaction_amount']/10000000
            title17 = f"Top 10 pincode locations by Transaction volume. Value in Crores"
            st.plotly_chart(
            create_plotly_charts(
                qry_df10_fil,
                'Bar',
                'Transaction_amount',
                'Pincode',
                widthv=900,
                heightv=500,
                grid=False,
                color='Transaction_amount',
                color_continuous_scale='curl',
                orientation='h',
            ).update_xaxes(title_text='', showgrid=False,tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹')
            .update_yaxes(title_text='', showgrid=False)
                        .update_traces(texttemplate="₹%{x:,.2f} Cr",hovertemplate='<br>Transaction Amount: ₹%{x:,.2f} Cr')

            .update_layout(yaxis_type='category',xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'},title={ 'text': title17, 'x': 0.4, 'xanchor': 'center', 'y': 0.94, 'yanchor': 'bottom' }
    ),
            use_container_width=True
        )
            expander111=st.expander(label=title17)
            expander111.dataframe(qry_df10_fil.reset_index(drop = True))



if selected == 'Transactions':

    st.markdown("<h1 style='text-align: center; font-size: 38px; color:#60b4ff ; font-weight: 700;font-family:PhonePeSans;'>Transactions Overview </h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)


    st.subheader(':blue[Transaction amount breakdown]')

    agg_trans=tbls['agg_tran']

    df,qtr_opts,state_opts,year_opts=filter_list(agg_trans,suff=1)

    suffix = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == '1' else "'nd quarter" if qtr_opts == '2' else "'rd quarter" if qtr_opts == '3' else "'th quarter"
    chart_title=f"Transaction details of {state_opts} for  {qtr_opts}{suffix} of {year_opts}."
    df=df.groupby(['State','Transaction_type','Year','Quarter'])['Transaction_amount'].sum().reset_index()

    df['Transaction_amount']=round(df['Transaction_amount']/10000000,2)
    sorted_df = df.sort_values(by='Transaction_amount', ascending=False) 
    st.plotly_chart(create_plotly_charts(
        sorted_df,'Bar','Transaction_type','Transaction_amount',color='Transaction_amount',
        color_continuous_scale='phase', title=chart_title,labels=dict(Transaction_amount='Transaction Amount', Transaction_type='Transaction Type'),
        hover_data={'Quarter': True,'Transaction_amount':True,'Year':True,'State':True})
        .update_layout(showlegend=False, title={'x': 0.5,'xanchor': 'center','y': 0.9,'yanchor': 'top'},width = 900, height = 500)
        .update_traces(marker = dict(line = dict(width = 1, color = 'DarkSlateGrey')))
        .update_yaxes(tickformat=",.2f ",title='Amount in thousand Crores',ticksuffix='  Cr',tickprefix='₹',title_font=dict(size=18),tickfont=dict(size=15))
        .update_xaxes(title_font=dict(size=18),tickfont=dict(size=14))
        ,use_container_width=True)
    
    expander1 = st.expander(label = 'Detailed view')
    expander1.write(sorted_df.loc[:, ['Quarter', 'Transaction_type', 'Transaction_amount']].reset_index(drop=True))
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.subheader(':blue[Transaction  Hotspots - Districts]')

    state_col,year_col, quarter_col = st.columns([4,3,2])
    map_user = tbls['map_tran']


    df,qtr_opts,state_opts,year_opts=filter_list(map_user,suff=2)
    
    if state_opts !='All':
        zoom_level = 5
        center_lat = df[df["State"] == state_opts]["Latitude"].mean()
        center_lon = df[df["State"] == state_opts]["Longitude"].mean()
        state=f'{state_opts} state'
    else:
        zoom_level = 3.5
        center_lat = 23.5937
        center_lon =78.9629
        state=f'{state_opts} states'

    suffix2 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
    chart_title2=f"""Transaction hotspots of {state} for {qtr_opts}{suffix2} of {year_opts}. <br>(Amount in Crore & count in lakhs)"""

    df['Transaction_count']=df['Transaction_count']/100000
    df['Transaction_amount']=df['Transaction_amount']/10000000
    

    map_user_plot = px.scatter_mapbox(df,lat='Latitude',lon='Longitude',size='Transaction_count',
                                      size_max=25,hover_data = {'Longitude':False,'Latitude':False,"Transaction_count": True, "Transaction_amount": True, 'Quarter': True},
                                      hover_name='District',title=chart_title2,text='District',color_discrete_sequence=px.colors.sequential.Viridis,)
    map_user_plot.add_annotation(go.layout.Annotation( text=chart_title2,
        align='center',
        showarrow=False,
        xref='paper',
        yref='paper',
        x=0.5,
        y=1.001,
        font=dict(color='black',size=18,family='Balto'),
        bgcolor='#ffffff',  
        borderpad=6,
        opacity=0.8,
        bordercolor='#000000',
        borderwidth=2,
    )
)
    map_user_plot.update_layout(mapbox_style='carto-positron',mapbox_zoom = zoom_level, mapbox_center = {"lat": center_lat, "lon": center_lon},geo=dict(scope = 'asia', projection_type = 'equirectangular'),margin={"r":0,"t":0,"l":0,"b":0}, width = 100, height = 500)
    map_user_plot.update_traces(hovertemplate='<b>%{text}</b><br>Transaction Count: ₹%{customdata[2]:,.2f} lakhs<br>Transaction Amount: ₹%{customdata[3]:,.2f} Cr<br>Quarter: %{customdata[4]}')
    st.plotly_chart(map_user_plot,use_container_width=True)

    st.expander1 = st.expander(label = 'Transaction Hotspots Detailed view')
    st.expander1.write(df.loc[:, ['State','District', 'Year','Quarter', 'Transaction_amount','Transaction_count']].reset_index(drop=True))
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.subheader(":blue[Transaction count breakdown:]")

    agg_trans=tbls['agg_tran']
    df,qtr_opts,state_opts,year_opts=filter_list(agg_trans,suff=3)

    TC_Break,buff,TC_Break1=st.columns([2.5,0.001,3])

    TC_Break.plotly_chart(
        create_plotly_charts(
            df, 'Pie', 'Transaction_type', 'Transaction_count', grid=False,hole=0.55,color_discrete_sequence=px.colors.sequential.Magma,
            hover_data = {"State": True, "Year": True, 'Quarter': True})
            .update_traces( visible=True, showlegend=True   ,textfont=dict(size=15),textfont_color='#FFFFFF'),
            use_container_width=True)

    buff.markdown("<div style='border-left: 3px solid #5f1f9c;font-family:PhonePeSans; height: 400px;'></div>", unsafe_allow_html=True)
    df['Transaction_count']=df['Transaction_count']/10000000
    TC_Break1.plotly_chart(
        create_plotly_charts(
            df, 'Bar', 'Transaction_type', 'Transaction_count',grid=False,color='Transaction_type',color_discrete_sequence=px.colors.sequential.Magma,
            hover_data = {"State": True, "Year": True, 'Quarter': True})
             .update_traces( visible=True, showlegend=False   ,textfont=dict(size=15),textfont_color='#FFFFFF')
            .update_yaxes(tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹',title='Count in Crores',title_font=dict(size=18),tickfont=dict(size=15))
            .update_xaxes(title_font=dict(size=18),tickfont=dict(size=15)),
              use_container_width=True)
    
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.subheader(":blue[Top Transactions by Districts:]")

    top_dist_tran = tbls['top_tran_dist']
    df,qtr_opts,state_opts,year_opts=filter_list(top_dist_tran,suff=4)
    
    suffix1 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
    title3=f'Top 10 districts across {state_opts} state by Transactions count in {year_opts}, {qtr_opts}{suffix1}'

    df['Transaction_count']=df['Transaction_count']/10000000
    dff= df.groupby("District")["Transaction_count"].sum().nlargest(10).index.tolist()
    df = df[df["District"].isin(dff)]
    st.plotly_chart(
            create_plotly_charts(
                df,
                'Bar',
                'Transaction_count',
                'District',
                widthv=900,
                heightv=500,
                grid=False,
                color='Transaction_count',
                color_continuous_scale='Magma',
                orientation='h',
            ).update_xaxes(title_text='Count in Crores',tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹', showgrid=False,title_font=dict(size=18),tickfont=dict(size=15))
            .update_yaxes(title_text='', showgrid=False,title_font=dict(size=18),tickfont=dict(size=15)).update_layout(
        xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'},title={ 'text': title3, 'x': 0.45, 'xanchor': 'center', 'y': 0.94, 'yanchor': 'bottom' }
    ),
            use_container_width=True
        )
    expander4  = st.expander(label = 'Top Transactions by Districts, Detailed view')
    expander4.write(df.loc[:, ['State', 'Year','Quarter', 'District','Transaction_count']].reset_index(drop=True))

if selected == 'Users':
    st.markdown("<h1 style='text-align: center; font-size: 38px; color:#ff4b4b ; font-weight: 700;font-family:PhonePeSans;'>Users Overview </h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.subheader(":red[Transaction Count  Percentage by Brand:]")
    agg_user = tbls['agg_user']
    
    df,qtr_opts,state_opts,year_opts=filter_list(agg_user,suff=5)

    df['count']=df['Transaction_count']/100000
    
    suffix4 = " quarters" if qtr_opts == 'All' else "st" if qtr_opts == 1 else "nd" if qtr_opts == 2 else "rd" if qtr_opts == 3 else "th"
    title4=f"Transaction Count in lakhs. and Percentage in {state_opts} for {qtr_opts}{suffix4} {'' if qtr_opts== 'All' else 'quarter'} of {year_opts}"

    
    t_map=create_plotly_charts(
        df,'Treemap',['Brand'],'count',color='Percentage',
        hover_data={'count':True,'Percentage': ':.2%','State':False,'Year':True,'Quarter':False},color_continuous_scale='phase',)
    
    t_map.update_layout(height=700,title = {"text": title4 ,'x': 0.45, 'xanchor': 'center','y': 0.89,'yanchor': 'bottom'})
    t_map.update_traces(marker=dict(cornerradius=5),hovertemplate='<b>%{label}</b><br>Transaction Count: %{customdata[0]:,.2f} lakhs<br>Percentage: %{customdata[1]:.2%}')
    
    st.plotly_chart(t_map,
        use_container_width=True)
    
    expander3 = st.expander(label = 'Transaction Count  Percentage by Brand, Detailed view')
    expander3.write(df.loc[:, ['State', 'Year','Quarter', 'Brand','Transaction_count','Percentage']].reset_index(drop=True))

    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.subheader(":red[Registered Users Hotspots - Disrict:]")

    map_user=tbls['map_user']
    map_user['Registered_users']=map_user['Registered_users']/100000
    map_user['App_opens']=map_user['App_opens']/100000


    df,qtr_opts,state_opts,year_opts=filter_list(map_user,suff=6)

    if state_opts != 'All':
        zoom_level = 5
        center_lat = df[df["State"] == state_opts]["Latitude"].mean()
        center_lon = df[df["State"] == state_opts]["Longitude"].mean()
    else:
        zoom_level = 3.5
        center_lat = 23.5937
        center_lon =78.9629


    suffix5 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
    chart_title1=f"""{state_opts} Registered user hotspots for {qtr_opts}{suffix5} of {year_opts}.<br>(Registered users in Lakhs &App Opens in Lakhs)"""
    
    reg_user_plot = px.scatter_mapbox(df,lat='Latitude',lon='Longitude',size='Registered_users',
                                      color='Registered_users',size_max=25, hover_data = {"Longitude": False,"Latitude": False, "Registered_users": True, "App_opens": True, 'Region': False},
                                      text='District',color_continuous_scale='Viridis',)

    reg_user_plot .add_annotation(go.layout.Annotation( text=chart_title1,
        align='center',
        showarrow=False,
        xref='paper',
        yref='paper',
        x=0.5,
        y=1.001,
        font=dict(color='black',size=18,family='Balto'),
        bgcolor='#ffffff',  
        borderpad=6,
        opacity=0.8,
        bordercolor='#000000',
        borderwidth=2,
    )
)    
    reg_user_plot.update_layout(mapbox_style='carto-positron',mapbox_zoom = zoom_level, mapbox_center = {"lat": center_lat, "lon": center_lon},
                                geo=dict(scope = 'asia', projection_type = 'equirectangular'), 
                                margin={"r":0,"t":0,"l":0,"b":0}, width = 400, height = 500)
    reg_user_plot.update_traces(hovertemplate='<b>%{text}</b><br>Registered users -  %{customdata[2]:,.2f} Lakhs<br>App_opens - %{customdata[3]:,.2f} Lakhs<br>Region - %{customdata[4]}')
    
    st.plotly_chart(reg_user_plot,use_container_width=True)
    
    expander2 = st.expander(label = 'Regitered user Hotspots Detailed view')
    expander2.write(df.loc[:, ['State','District', 'Year','Quarter', 'Registered_users','App_opens']].reset_index(drop=True))

    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.subheader(":red[Top Districts by Registered Users:]")

    top_dist_user=tbls['top_user_dist']
    df,qtr_opts,state_opts,year_opts=filter_list(top_dist_user,suff=7)


    suffix3 = " quarters" if qtr_opts== 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
    title4=f'Top 10 districts across {state_opts} state by registered user count in {year_opts}, {qtr_opts}{suffix3} '
    df['Registered_users']=round(df['Registered_users']/100000,2)
    top_dist_user_grpy_df=df.groupby('District')['Registered_users'].sum().nlargest(10).index.tolist()
    
    df = df[df['District'].isin(top_dist_user_grpy_df)]
    
    st.plotly_chart(
            create_plotly_charts(
                df,
                'Bar',
                'Registered_users',
                'District',
                widthv=900,
                heightv=500,
                grid=False,
                color='Registered_users',
                color_continuous_scale='phase',
                orientation='h',
                hover_data={'Registered_users':True,'State':True,'Year':False,'Quarter':False},

            ).update_xaxes(title_text='Count in Lakhs', showgrid=False,tickformat=",.2f ",ticksuffix=' Lakhs',tickprefix='', title_font=dict(size=18),tickfont=dict(size=15))
            .update_yaxes(title_text='', showgrid=False,tickfont=dict(size=15))
            .update_layout(xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'},
                           title={ 'text': title4, 'x': 0.4, 'xanchor': 'center', 'y': 0.94, 'yanchor': 'bottom' }
    ).update_traces(hovertemplate='<b>%{y}</b><br>Registered Users: %{x:,.2f} Lakhs<br>State: %{customdata[0]}')
,
            use_container_width=True
        )
    expander5  = st.expander(label = 'Top Transactions by Districts, Detailed view')
    expander5.write(df.loc[:, [  'District','Registered_users']].reset_index(drop=True))
    
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.subheader(":red[Number of app opens by District:]")
    
    
    df,qtr_opts,state_opts,year_opts=filter_list(map_user,suff=8)
    
    if state_opts !='All':
        zoom_level = 6
        center_lat = df[df["State"] == state_opts]["Latitude"].mean() 
        center_lon = df[df["State"] == state_opts]["Longitude"].mean()
        rad=10

    else:
        zoom_level = 3.5
        center_lat = 23.5937 
        center_lon =78.9629
        rad=10

    suffix7 = " quarters" if qtr_opts == 'All' else "'st quarter" if qtr_opts == 1 else "'nd quarter" if qtr_opts == 2 else "'rd quarter" if qtr_opts == 3 else "'th quarter"
    title7=f'App opens Hotspot  across {state_opts} state  in {year_opts}, {qtr_opts}{suffix7} <br>(App Opens count in Lakhs & Registered user count in Lakhs)'


    if year_opts == '2018':
        add_vertical_space(1)
        st.info('No Data for the year 2018')
        add_vertical_space(1)
        expanded=True

    elif (year_opts=='2019') & (qtr_opts==1):
        add_vertical_space(1)
        st.info('No Data for the year 2019, Quarter 1')
        add_vertical_space(1)
        expanded=True

    else:
        reg_user_plot = px.density_mapbox(df, lat='Latitude', lon='Longitude', z='App_opens', opacity=.8, color_continuous_scale='phase', 
                                          mapbox_style="carto-positron", radius=rad, hover_data={"Latitude": False, "Longitude": False, "District": True, "App_opens": True, 'Registered_users':True,'Region':True}, 
                                          hover_name='District', center=dict(lat=0, lon=180), zoom=zoom_level)
        reg_user_plot   .update_layout( mapbox_zoom=zoom_level,  geo=dict(scope='asia', projection_type='equirectangular'), mapbox_center={"lat": center_lat, "lon": center_lon}, margin={"r": 0, "t": 0, "l": 0, "b": 0}, width=800, height=550)
        reg_user_plot.update_traces(hovertemplate='<b>%{hovertext}</b><br>App Opens: %{z:,.2f} Lakhs<br>Registered Users: %{customdata[3]:,.2f} Lakhs<br>Region - %{customdata[4]}')
        reg_user_plot  .add_annotation(go.layout.Annotation( text=title7,
        align='center',
        showarrow=False,
        xref='paper',
        yref='paper',
        x=0.5,
        y=1.001,
        font=dict(color='black',size=18,family='Balto'),
        bgcolor='#ffffff',  
        borderpad=6,
        opacity=0.8,
        bordercolor='#000000',
        borderwidth=2,
    )
)
        st.plotly_chart(reg_user_plot, use_container_width=True)
        expanded=False

    st.expander1 = st.expander(label='App opens Hotspots Detailed view',expanded=expanded)
    st.expander1.write(df.loc[:, ['State', 'District', 'Year', 'App_opens','Registered_users']].reset_index(drop=True))

if selected == "Trend":

    st.markdown("<h1 style='text-align: center; font-size: 38px; color:#3dd56d ; font-weight: 700;font-family:PhonePeSans;'>Trend Analysis </h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)


    map_tran=tbls['map_tran']
    top_tran_dist =dist_tran= tbls['top_tran_dist']
    pin_tran=tbls['top_tran_pin']
    
    st.subheader(':green[Transaction Count and Amount - Trend over the years]')
    add_vertical_space(1)
    
    col1,col2,col3,col4=st.columns([4,4,4,2])
    region = col1.selectbox('Region', map_tran["Region"].unique(), key='Region')
    df=map_tran[map_tran["Region"]==region]
    state=col2.selectbox('State', df["State"].unique(), key='State')
    df=df[df['State']==state]
    dist=col3.selectbox('District', df["District"].unique(), key='District')
    df=df[df['District']==dist]
    year=col4.selectbox('Year', ['All']+list(map(str,map_tran["Year"].unique())), key='Year ')

    title=f'Transaction count  trend for {dist} district in {state} across {str(year).lower()} years'
    title1=f'Transaction amount trend for {dist} district in {state} during {str(year).lower()} years'
    
    if year !='All':
        df=df[df['Year']==year]
        title=f"Transaction count in  thousands (K)trend for {dist} district in {state} during {str(year).lower()} "
        title1=f"Transaction amount in Crores trend for {dist} district in {state} during {str(year).lower()} "

    tab1,tab2=st.tabs(['📊Transaction Count Trend', '💰Transaction Amount Trend'])
    df['Transaction_amount']=round(df['Transaction_amount']/10000000,2)
    df['Transaction_count']=round(df['Transaction_count']/1000,2)

    tab1.plotly_chart(
            create_plotly_charts(
                df,
                'lne',
                'Quarter',
                'Transaction_count',
                text='Transaction_count',
                line_group='Year',
                line_dash='Year',
                hover_data={'Transaction_amount':True,'Year':True,'Quarter':False},
                color='Year',
                markers=True,
                grid=True,
                color_discrete_sequence=px.colors.sequential.Magma_r,
                title=title
            ).update_layout( height = 500, width = 900, yaxis_title = 'Count in Crores', title={ 'x': 0.5, 'xanchor': 'center', 'y': 0.9, 'yanchor': 'bottom' } )
            .update_traces(textposition="bottom right",texttemplate="%{y:,.2f} K",hovertemplate='<b>%{customdata[1]}</b><br>Transaction Count: %{y:,.2f} K<br>Transaction Amount: ₹%{customdata[0]:,.2f} Cr')
            .update_yaxes(tickformat=",.2f ",ticksuffix=' Cr')
,use_container_width=True)
    expander6=tab1.expander('Transaction Count tred view')
    expander6.write((df.loc[:, ['Region', 'District', 'Year', 'Quarter', 'Transaction_count']].reset_index(drop = True)))


    tab2.plotly_chart(
                create_plotly_charts(
                    df,
                    'lne',
                    'Quarter',
                    'Transaction_amount',
                      text='Transaction_amount',
                    line_group='Year',
                    line_dash='Year',
                hover_data={'Transaction_amount':True,'Year':True,'Quarter':False,'Transaction_count':True},
                    color='Year',
                    markers=True,
                    grid=True,
                    color_discrete_sequence=px.colors.sequential.Magma_r,
                    title=title1
                ).update_layout( height = 600, width = 900, yaxis_title = 'Amount in Crores', title={ 'x': 0.5, 'xanchor': 'center', 'y': 0.9, 'yanchor': 'bottom' } )
                .update_traces(textposition="bottom right",texttemplate="%{y:,.2f} Cr",hovertemplate='<b> %{customdata[0]}</b><br>Transaction Amount: ₹%{y:,.2f} Cr<br>Transaction Count:%{customdata[1]:,.2f} K')
                  .update_yaxes(tickformat=",.2f ",ticksuffix=' Cr',tickprefix=' ₹')
                ,use_container_width=True)
    
    expander7=tab2.expander('Transaction Amount tred view')
    expander7.write((df.loc[:, ['Region', 'District', 'Year', 'Quarter', 'Transaction_amount']].reset_index(drop = True)))
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.subheader(':green[Transaction Count and Amount - Top Districts]')

    df,qtr_opts,state_opts,year_opts=filter_list(top_tran_dist,suff=8)

    df1=df.groupby("District")["Transaction_count"].sum().nlargest(10).index.tolist()
    df2=df[df["District"].isin(df1)]

    df2['Transaction_count']=df2['Transaction_count']/100000
    df2['Transaction_amount']=df2['Transaction_amount']/10000000

    suffix8=" quarters" if qtr_opts == 'All' else "st" if qtr_opts == 1 else "nd" if qtr_opts == 2 else "rd" if qtr_opts == 3 else "th"
    title8 = f"Top districts in {'India' if state_opts == 'All' else state_opts} by Transaction count during {str(qtr_opts).lower()}{suffix8} {'' if qtr_opts == 'All' else 'quarter'} of {year_opts}"

    df3=df.groupby("District")["Transaction_amount"].sum().nlargest(10).index.tolist()
    df4=df[df["District"].isin(df3)]

    suffix9=" quarters" if qtr_opts == 'All' else "st" if qtr_opts == 1 else "nd" if qtr_opts == 2 else "rd" if qtr_opts == 3 else "th"
    title9 = f"Top districts in {'India' if state_opts == 'All' else state_opts} by Transaction amount during {str(qtr_opts).lower()}{suffix9} {'' if qtr_opts == 'All' else 'quarter'} of {year_opts}"

    tab3,tab4=st.tabs(['📊Top District - Transaction Count','💰Top District -  Transaction Amount'])
    tab3.plotly_chart(
            create_plotly_charts(
                df2,
                'Bar',
                'Transaction_count',
                'District',
                text='Transaction_count',
                widthv=900,
                heightv=500,
                grid=False,
                color='Transaction_count',
                color_continuous_scale='curl',
                hover_data={'Transaction_amount':True,'Year':True,'Quarter':True},
                orientation='h',
            ).update_xaxes(title_text='', showgrid=False,tickformat=",.2f ",ticksuffix=' Lakhs',tickprefix='')
            .update_yaxes(title_text='', showgrid=False)
            .update_traces(texttemplate="%{x:,.2f} Lakhs",hovertemplate='<b>%{customdata[1]}</b><br>Transaction Count: %{x:,.2f} Lakhs<br>Transaction Amount: ₹%{customdata[0]:,.2f} Cr')
            .update_layout(
        xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'},title={ 'text': title8, 'x': 0.4, 'xanchor': 'center', 'y': 0.94, 'yanchor': 'bottom' }
    ),
            use_container_width=True
        )
    expander9  = tab3.expander(label = 'Top Transactions count by Districts, Detailed view')
    expander9.write(df2.loc[:, ['State', 'Year','Quarter', 'District','Transaction_count']].reset_index(drop=True))
    tab4.plotly_chart(
            create_plotly_charts(
                df2,
                'Bar',
                'Transaction_amount',
                'District',
                text='Transaction_amount',
                widthv=900,
                heightv=500,
                grid=False,
                hover_data={'Transaction_count':True,'Year':True,'Quarter':True},
                color='Transaction_amount',
                color_continuous_scale='curl',
                orientation='h',
            ).update_xaxes(title_text='', showgrid=False,tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹')
            .update_yaxes(title_text='', showgrid=False)
            .update_traces(texttemplate="₹%{x:,.2f} Cr",hovertemplate='<b>%{customdata[1]}</b><br>Transaction Amount: ₹%{x:,.2f} Cr<br>Transaction Count: %{customdata[0]:,.2f} Cr')

            .update_layout(
        xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'},title={ 'text': title9, 'x': 0.4, 'xanchor': 'center', 'y': 0.94, 'yanchor': 'bottom' }
    ),
            use_container_width=True
        )
    expander10  = tab4.expander(label = 'Top Transactions amount by Districts, Detailed view')
    expander10.write(df2.loc[:, ['State', 'Year','Quarter', 'District','Transaction_amount']].reset_index(drop=True))
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.subheader(':green[Other Key Trends over the years]')
    
    col5,col6,col7=st.columns([5,4,3])
    trend=col5.selectbox('Trend',( 'Top 10 States by Transaction Volume', 'Top 10 Districts by Transaction Volume', 'Top 10 Pincodes by Transaction Volume' ), key = 'trend3' )
    year3 = col6.selectbox('Year', map_tran['Year'].unique(), key = 'year3')
    qtr_list=map_tran.loc[map_tran['Year']==year3,'Quarter'].unique()
    quarter3 = col7.selectbox('Quarter',['All']+list(map(int, qtr_list)), key = 'quarter3')

    top_state=filter_top_trans_dist(dist_tran,year3,quarter3)
    top_dist= filter_top_trans_dist(dist_tran,year3,quarter3)
    top_pin=filter_top_trans_dist(pin_tran,year3,quarter3)

    
    filtered_top_states = top_state.groupby('State')[ 'Transaction_amount' ].sum().reset_index().sort_values( 'Transaction_amount', ascending=False ).head(10)
    filtered_top_dist = top_dist.groupby('District')[ 'Transaction_amount' ].sum().reset_index().sort_values( 'Transaction_amount', ascending=False ).head(10)
    filtered_top_pin=top_pin.groupby('Pincode')['Transaction_amount'].sum().reset_index().sort_values('Transaction_amount',ascending=False).head(10)

    filtered_top_pin['Pincode'] = filtered_top_pin['Pincode'].astype(str)
    filtered_top_pin['Pincode'] = pd.Categorical(filtered_top_pin['Pincode'], ordered=True)

    suffix2 = " quarters" if quarter3 == 'All' else "st" if quarter3 == 1 else "nd" if quarter3 == 2 else "rd" if quarter3 == 3 else "th"
    title5 = f"Top 10 states by Transaction volume {'across' if quarter3 == 'All' else 'in'} {str(quarter3).lower()}{suffix2} {'' if quarter3 == 'All' else 'quarter'} of {year3}"
    title6 = f"Top 10 districts by Transaction volume {'across' if quarter3 == 'All' else 'in'} {str(quarter3).lower()}{suffix2} {'' if quarter3 == 'All' else 'quarter'} of {year3}"
    title7 = f"Top 10 pincode locations by Transaction volume {'across' if quarter3 == 'All' else 'in'} {str(quarter3).lower()}{suffix2} {'' if quarter3 == 'All' else 'quarter'} of {year3}"




    if trend == 'Top 10 States by Transaction Volume':
        df=filtered_top_states
        x=df['State']
        title = title5
        ex_label='Top 10 states detailed view'
        

    elif trend == 'Top 10 Districts by Transaction Volume':
        df=filtered_top_dist
        x=df['District']
        title=title6
        ex_label='Top 10 districts detailed view'
        
        

    elif  trend == 'Top 10 Pincodes by Transaction Volume':
        df=filtered_top_pin
        df['Pincode']=pd.Categorical(df['Pincode'])
        x=df['Pincode']
        title=title7
        ex_label='Top 10 pincodes detailed view'
    
    
    df['Transaction_amount']=df['Transaction_amount']/10000000
    st.plotly_chart(
        create_plotly_charts(
            df,
            'Bar',
            'Transaction_amount',
            x,
            widthv=900,
            heightv=500,
            grid=False,
            color='Transaction_amount',
            color_continuous_scale='curl',
            orientation='h',
        ).update_xaxes(title_text='', showgrid=False,tickformat=",.2f ",ticksuffix=' Cr',tickprefix='₹')
        .update_yaxes(title_text='', showgrid=False)
                    .update_traces(texttemplate="₹%{x:,.2f} Cr",hovertemplate='<br>Transaction Amount: ₹%{x:,.2f} Cr')

        .update_layout(yaxis_type='category',xaxis={'categoryorder': 'total descending'},yaxis={'categoryorder': 'total ascending'},title={ 'text': title, 'x': 0.4, 'xanchor': 'center', 'y': 0.94, 'yanchor': 'bottom' }
),
        use_container_width=True
    )
    expander11=st.expander(label=ex_label)
    expander11.dataframe(df.reset_index(drop = True))

if selected =='Comparison':
    st.markdown("<h1 style='text-align: center; font-size: 38px; color:white; font-weight: 700;font-family:PhonePeSans;'>Comparitive Analysis </h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    trans_df1 = trans_df2 =tbls['agg_tran']
    user_df = tbls['agg_user']
    
    st.markdown("<h3 style='color: white;'>Regionwise Transaction amount comparison</h3>", unsafe_allow_html=True)


    title ='Regionwise Transaction amount in Trillions'

    trans_df1['Transaction_amount']=trans_df1['Transaction_amount']
    cat_fig=px.bar(trans_df1,x='Year',y='Transaction_amount',color='Region',barmode='group',text='State',facet_col='Region',facet_col_wrap=2,range_y=[0, trans_df1['Transaction_amount'].max() * 9],)

    cat_fig.update_yaxes(showgrid=False ,tickformat="",tickprefix='₹')
    
    cat_fig.update_traces(hovertemplate='<b>%{text}</b><br>Transaction Amount: %{y} <br>Year : %{x:.0f} ')

    

    cat_fig.update_layout(showlegend=False,
    yaxis_title='Transaction Amount',
    xaxis_title='Year',width=400,height=600) 
    

  
    st.plotly_chart(cat_fig,use_container_width=True)



    trans_df1['Transaction_amt']=round(trans_df1['Transaction_amount']/1e12,2)
    ab=create_plotly_charts(trans_df1,'Treemap',['Region','Year'],'Transaction_amt' ,color='Transaction_amount',color_continuous_scale='curl',hover_data={'Transaction_amt': True,'Transaction_amount':True,})
    ab.update_layout( height=500,title = {"text": title ,'x': 0.45, 'xanchor': 'center','y': 0.847,'yanchor': 'bottom','font':dict(color='#ffffff')},).update_traces(marker=dict(cornerradius=11),root_color="red",hovertemplate='<b>%{label}</b><br>Transaction Amount: %{customdata[0]:,.2f} Trillions.')
    ab.update_coloraxes(showscale=False) 

    st.plotly_chart(ab,use_container_width=True)

    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.markdown("<h3 style='color: white;'>Transaction count by Transaction type</h3>", unsafe_allow_html=True)


    filtered_df,qtr_opts,state_opts,year_opts=filter_list(trans_df1, suff=10,multi_st=True)
  
    suffix10 = " quarters" if qtr_opts == 'All' else "st" if qtr_opts == 1 else "nd" if qtr_opts == 2 else "rd" if qtr_opts == 3 else "th"

    title10 = f"Transaction details comparison of the selected states for {str(qtr_opts).lower()}{suffix10} {'' if qtr_opts == 'All' else 'quarter'} of {year_opts}"
    try:
        if len(state_opts) ==1:
            state_str = ''.join(state_opts)
            title10 = f"Transaction details of {state_str} for {str(qtr_opts).lower()}{suffix10} {'' if qtr_opts == 'All' else 'quarter'} of {year_opts}"
        elif len(state_opts)==0:
            st.info('Please select state from the dropdown to explore. 🔍') 
    except TypeError:
        pass
    
    fig2 = px.bar(
                  filtered_df, x="Transaction_type", y="Transaction_count", 
                  color="State",
                  color_discrete_sequence=px.colors.qualitative.Plotly,
                  barmode='group',
                  title=title10,
                  labels=dict(Transaction_count='Transaction Count', Transaction_type='Transaction Type'),
                  hover_data={'State':True,'Transaction_count':True,'Transaction_amount':True,'Quarter': True}
                  )

    fig2.update_layout(
                       width=900, height=550,
                       title={
                              'x': 0.5,
                              'xanchor': 'center',
                              'y': 0.9,
                              'yanchor': 'top'
                              }
                       )
    if len(state_opts)!=0:
        fig2.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')),hovertemplate='<b>%{customdata[0]}</b><br>Transaction Count: %{y:,.2f} <br>Transaction Amount: ₹%{customdata[3]:,.2f}')
        st.plotly_chart(fig2)


    add_vertical_space(2)

    st.markdown("<hr style='border: 2px solid #5f1f9c;'>", unsafe_allow_html=True)

    st.markdown("<h3 style='color: white;'>Transaction amount  by Region, year, and  Quarterwise comparison</h3>", unsafe_allow_html=True)
    

    col8,col9,col10 = st.columns([3, 2,4])
    region_list=trans_df2['Region'].unique()
    year_list = trans_df2['Year'].unique()

    reg_opts=col8.selectbox('Region',region_list,key='reg_opts')
    year_opt=col9.selectbox('Year',year_list,key='year_opt')

    fildf=trans_df2[(trans_df2['Region']==reg_opts) &( trans_df2['Year']==year_opt)]

    fildf['Quarter']= 'Quarter '+ fildf['Quarter'].astype(str)
    fildf['Transaction_amount']=fildf['Transaction_amount']/1e9
    
    fig=create_plotly_charts( fildf,'Pie','Quarter','Transaction_amount',title=f'Transaction amount Comparison of {reg_opts} for the year {year_opt}',
        grid=False,hole=0.35,color_discrete_sequence=px.colors.sequential.Magma)
    fig.update_traces(visible=True,textfont=dict(size=15, color='#FFFFFF'),textposition='inside', textinfo='percent+label')
    fig.update_layout(width=850, height=550,legend_font=dict(size=13),legend_title_text='Quarter',title={ 'x': 0.45, 'xanchor': 'center', 'y': 0.9, 'yanchor': 'top' })
    st.plotly_chart(fig, use_container_width=True)


    


