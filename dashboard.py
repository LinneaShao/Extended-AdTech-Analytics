"""
AdTech Analytics Dashboard
Interactive data visualization for campaign performance analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from sqlalchemy import create_engine, text

# Multi-language support
translations = {
    'en': {
        'title': '📊 AdTech Analytics Dashboard',
        'no_data': 'No data available. Please upload some campaign data first.',
        'data_overview': 'Data Overview',
        'total_clicks': 'Total Clicks',
        'total_conversions': 'Total Conversions',
        'avg_conversion_rate': 'Average Conversion Rate',
        'channel_performance': 'Channel Performance',
        'conversion_trend': 'Conversion Rate Trend',
        'filters': 'Filters',
        'date_range': 'Date Range',
        'select_channel': 'Select Channel',
        'all_channels': 'All Channels',
        'export_data': 'Export Data',
        'download_csv': 'Download CSV',
        'clicks_by_channel': 'Clicks by Channel',
        'conversion_rate_trend': 'Conversion Rate Trend',
        'language': 'Language'
    },
    'fr': {
        'title': '📊 Tableau de Bord Analytics AdTech',
        'no_data': 'Aucune donnée disponible. Veuillez télécharger des données de campagne.',
        'data_overview': 'Aperçu des Données',
        'total_clicks': 'Total des Clics',
        'total_conversions': 'Total des Conversions',
        'avg_conversion_rate': 'Taux de Conversion Moyen',
        'channel_performance': 'Performance par Canal',
        'conversion_trend': 'Tendance du Taux de Conversion',
        'filters': 'Filtres',
        'date_range': 'Plage de Dates',
        'select_channel': 'Sélectionner un Canal',
        'all_channels': 'Tous les Canaux',
        'export_data': 'Exporter les Données',
        'download_csv': 'Télécharger CSV',
        'clicks_by_channel': 'Clics par Canal',
        'conversion_rate_trend': 'Tendance du Taux de Conversion',
        'language': 'Langue'
    },
    'zh': {
        'title': '📊 广告技术分析仪表板',
        'no_data': '暂无数据。请先上传一些活动数据。',
        'data_overview': '数据概览',
        'total_clicks': '总点击数',
        'total_conversions': '总转换数',
        'avg_conversion_rate': '平均转换率',
        'channel_performance': '渠道性能',
        'conversion_trend': '转换率趋势',
        'filters': '筛选器',
        'date_range': '日期范围',
        'select_channel': '选择渠道',
        'all_channels': '所有渠道',
        'export_data': '导出数据',
        'download_csv': '下载CSV',
        'clicks_by_channel': '按渠道分组的点击数',
        'conversion_rate_trend': '转换率趋势',
        'language': '语言'
    }
}

# Page configuration
st.set_page_config(
    page_title="AdTech Analytics",
    page_icon="📊",
    layout="wide"
)

# Database connection
@st.cache_resource
def init_connection():
    return create_engine('postgresql://vivian@localhost:5432/adtech_db')

engine = init_connection()

# Data loading
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load campaign data from database"""
    query = """
    SELECT date, channel, clicks, conversions, conversion_rate
    FROM ad_data
    ORDER BY date DESC, channel
    """
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    df['date'] = pd.to_datetime(df['date'])
    return df

def create_channel_chart(df, t):
    """Create channel performance bar chart"""
    channel_data = df.groupby('channel').agg({
        'clicks': 'sum',
        'conversions': 'sum'
    }).reset_index()
    
    channel_data['conversion_rate'] = (channel_data['conversions'] / channel_data['clicks']) * 100
    
    fig = px.bar(
        channel_data, 
        x='channel', 
        y='clicks',
        title=t['clicks_by_channel'],
        color='conversion_rate',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=400)
    return fig

def create_trend_chart(df, t):
    """Create conversion rate trend line chart"""
    daily_data = df.groupby('date').agg({
        'clicks': 'sum',
        'conversions': 'sum'
    }).reset_index()
    
    daily_data['conversion_rate'] = (daily_data['conversions'] / daily_data['clicks']) * 100
    
    fig = px.line(
        daily_data,
        x='date',
        y='conversion_rate',
        title=t['conversion_rate_trend'],
        markers=True
    )
    
    fig.update_layout(height=400)
    return fig

def export_to_csv(df):
    """Export data to CSV"""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

# Main dashboard
def main():
    # Language selector in sidebar
    st.sidebar.selectbox("🌐 Language", ["en", "fr", "zh"], key="language")
    language = st.session_state.language
    t = translations[language]
    
    st.title(t['title'])
    
    # Load data
    try:
        df = load_data()
        
        if df.empty:
            st.warning(t['no_data'])
            return
        
        # Sidebar filters
        st.sidebar.header(t['filters'])
        
        # Date range filter
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        
        date_range = st.sidebar.date_input(
            t['date_range'],
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Channel filter
        channels = [t['all_channels']] + list(df['channel'].unique())
        selected_channel = st.sidebar.selectbox(t['select_channel'], channels)
        
        # Apply filters
        filtered_df = df.copy()
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['date'].dt.date >= start_date) & 
                (filtered_df['date'].dt.date <= end_date)
            ]
        
        if selected_channel != t['all_channels']:
            filtered_df = filtered_df[filtered_df['channel'] == selected_channel]
        
        # Key metrics
        st.subheader(t['data_overview'])
        col1, col2, col3, col4 = st.columns(4)
        
        total_clicks = filtered_df['clicks'].sum()
        total_conversions = filtered_df['conversions'].sum()
        avg_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        total_records = len(filtered_df)
        
        with col1:
            st.metric(t['total_clicks'], f"{total_clicks:,}")
        
        with col2:
            st.metric(t['total_conversions'], f"{total_conversions:,}")
        
        with col3:
            st.metric(t['avg_conversion_rate'], f"{avg_conversion_rate:.2f}%")
        
        with col4:
            st.metric("Records", f"{total_records:,}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(t['channel_performance'])
            if not filtered_df.empty:
                channel_chart = create_channel_chart(filtered_df, t)
                st.plotly_chart(channel_chart, use_container_width=True)
        
        with col2:
            st.subheader(t['conversion_trend'])
            if not filtered_df.empty:
                trend_chart = create_trend_chart(filtered_df, t)
                st.plotly_chart(trend_chart, use_container_width=True)
        
        # Data table
        st.subheader("Campaign Data")
        
        # Export options
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button(t['export_data']):
                csv_data = export_to_csv(filtered_df)
                st.download_button(
                    label=t['download_csv'],
                    data=csv_data,
                    file_name=f"adtech_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        # Display data
        st.dataframe(
            filtered_df[['date', 'channel', 'clicks', 'conversions', 'conversion_rate']], 
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Make sure the database is running and accessible.")

if __name__ == "__main__":
    main()
