#!/usr/bin/env python
# coding: utf-8
from turtle import color
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

def style_negative(x, props=''):
    try:
        return props if x<0 else None
    except:
        pass

def style_positive(x, props=''):
    try:
        return props if x>0 else None
    except:
        pass

def convert_country(s):
    if s == 'US':
        return 'United States'
    if s == 'IN':
        return 'India'
    else:
        return 'Other'
   
@st.cache
def load_data():
    """ Loads in 4 dataframes and does light feature engineering"""
    df_agg = pd.read_csv('Aggregated_Metrics_By_Video.csv').iloc[1:,:]
    df_agg.columns = ['Video','Video title','Video publish time','Comments added','Shares','Dislikes','Likes',
                      'Subscribers lost','Subscribers gained','RPM(USD)','CPM(USD)','Average % viewed','Average view duration',
                      'Views','Watch time (hours)','Subscribers','Your estimated revenue (USD)','Impressions','Impressions ctr(%)']
    df_agg['Video publish time'] = pd.to_datetime(df_agg['Video publish time'])
    df_agg['Average view duration'] = df_agg['Average view duration'].apply(lambda x: datetime.strptime(x,'%H:%M:%S'))
    df_agg['Avg_duration_sec'] = df_agg['Average view duration'].apply(lambda x: x.second + x.minute*60 + x.hour*3600)
    df_agg['Engagement_ratio'] =  (df_agg['Comments added'] + df_agg['Shares'] +df_agg['Dislikes'] + df_agg['Likes']) /df_agg.Views
    df_agg['Views / sub gained'] = df_agg['Views'] / df_agg['Subscribers gained']
    df_agg.sort_values('Video publish time', ascending = False, inplace = True)    
    df_agg_sub = pd.read_csv('Aggregated_Metrics_By_Country_And_Subscriber_Status.csv')
    df_comments = pd.read_csv('Aggregated_Metrics_By_Video.csv')
    df_time = pd.read_csv('Video_Performance_Over_Time.csv')
    df_time['Date'] = pd.to_datetime(df_time['Date'])
    return df_agg, df_agg_sub, df_comments, df_time 

df_agg, df_agg_sub, df_comments, df_time = load_data()

add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video',('Aggregate Metrics','Individual Video Analysis'))

df_agg_diff = df_agg.copy()
start_date = df_agg_diff['Video publish time'].max() - pd.DateOffset(months =12)

med_agg = df_agg_diff[df_agg_diff['Video publish time'] >= start_date].median()
numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))
df_agg_diff.iloc[:,numeric_cols] = (df_agg_diff.iloc[:,numeric_cols] - med_agg).div(med_agg)

date_12mo = df_agg['Video publish time'].max() - pd.DateOffset(months = 12)
df_time_diff = pd.merge(df_time, df_agg.loc[:,['Video','Video publish time']], left_on = 'External Video ID', right_on = 'Video')
df_time_diff['Days published'] = (df_time_diff['Date'] - df_time_diff['Video publish time']).dt.days
df_time_diff_yr = df_time_diff[df_time_diff['Video publish time'] >= date_12mo]

views_days = pd.pivot_table(df_time_diff, index = 'Days published', values = 'Views', aggfunc = [np.mean, np.median, lambda x : np.percentile(x,80), lambda x : np.percentile(x,20)]).reset_index()
views_days.columns = ['days_published','mean_views','median_views','80pct_views','20pct_views']
views_days = views_days[views_days['days_published'].between(0,30)]
views_cumulative = views_days.loc[:, ['days_published','median_views','80pct_views','20pct_views']]
views_cumulative.loc[:,['median_views','80pct_views','20pct_views']] = views_cumulative.loc[:,['median_views','80pct_views','20pct_views']].cumsum()



if add_sidebar == 'Aggregate Metrics':
    st.write('Agg')
    df_agg_metrics = df_agg[['Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed',
                             'Avg_duration_sec', 'Engagement_ratio','Views / sub gained']]
    metrics_date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months = 12)
    metrics_date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months = 6)
    med_metrics_12mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metrics_date_12mo].median()
    med_metrics_6mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metrics_date_6mo].median() 
    
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]
    count = 0
    for i in med_metrics_12mo.index:
        with columns[count]:
            delta = (med_metrics_6mo[i] - med_metrics_12mo[i])/med_metrics_12mo[i]
            st.metric(i, round(med_metrics_6mo[i],1), "{:.2%}".format(delta))
            count+=1
            if count >= 5:
                count = 0
    df_agg_diff['Publish_date'] = df_agg_diff['Video publish time'].apply(lambda x: x.date())
    df_agg_diff_final = df_agg_diff.loc[:,['Video title','Publish_date','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed',
                             'Avg_duration_sec', 'Engagement_ratio','Views / sub gained']]
    
    df_agg_diff_final_numlist = df_agg_diff_final.median().index.tolist()
    df_pct = {}
    for i in df_agg_diff_final_numlist:
        df_pct[i] = "{:.1%}".format
    st.dataframe(df_agg_diff_final.style.applymap(style_negative, props = "color:red;").applymap(style_positive, props = "color:green;").format(df_pct))

if add_sidebar == 'Individual Video Analysis':
    videos = tuple(df_agg['Video title'])
    video_select = st.selectbox('Video Title', videos)
    
    agg_filtered = df_agg[df_agg['Video title'] == video_select]
    agg_sub_filtered = df_agg_sub[df_agg_sub['Video Title'] == video_select]
    agg_sub_filtered['Country'] = agg_sub_filtered['Country Code'].apply(convert_country)
    agg_sub_filtered.sort_values('Is Subscribed', inplace=True)

    fig = px.bar(agg_sub_filtered, 'Views','Is Subscribed', color = 'Country', orientation = 'h' )
    st.plotly_chart(fig)

    agg_time_filtered = df_time_diff[df_time_diff['Video Title'] == video_select]
    first_30 = agg_time_filtered[agg_time_filtered['Days published'].between(0,30)].sort_values('Days published')

    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(x = views_cumulative['days_published'], y = views_cumulative['20pct_views'], mode = 'lines', name = '20th percentile', line = dict(color = 'purple', dash = 'dash')))
    fig2.add_trace(go.Scatter(x = views_cumulative['days_published'], y = views_cumulative['80pct_views'], mode = 'lines', name = '80th percentile', line = dict(color = 'royalblue', dash = 'dash')))
    fig2.add_trace(go.Scatter(x = views_cumulative['days_published'], y = views_cumulative['median_views'], mode = 'lines', name = '50th percentile', line = dict(color = 'white', dash = 'dash')))
    fig2.add_trace(go.Scatter(x = first_30['Days published'], y = first_30['Views'].cumsum(), mode = 'lines', name = 'Current Video', line = dict(color = 'firebrick', width = 8 )))
    fig2.update_layout(title='View comparison first 30 days',
                   xaxis_title='Days Since Published',
                   yaxis_title='Cumulative views')
    st.plotly_chart(fig2)