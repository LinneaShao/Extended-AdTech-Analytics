"""
Data processing utilities for AdTech campaign data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

def process_csv_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Process and validate CSV data for campaign analytics.
    
    Expected columns: date, campaign, channel, impressions, clicks, cost, conversions
    """
    try:
        # Validate required columns
        required_cols = ['date', 'channel', 'clicks', 'conversions']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Clean and convert data types
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce')
        df['conversions'] = pd.to_numeric(df['conversions'], errors='coerce')
        
        # Handle impressions for CTR calculation if available
        if 'impressions' in df.columns:
            df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce')
            df = df[df['impressions'] > 0]  # Avoid division by zero
            df['ctr'] = (df['clicks'] / df['impressions']) * 100
        
        # Remove rows with invalid data
        df = df.dropna(subset=['clicks', 'conversions'])
        df = df[df['clicks'] > 0]  # Avoid division by zero
        
        # Calculate conversion rate
        df['conversion_rate'] = (df['conversions'] / df['clicks']) * 100
        
        # Convert to records for database insertion
        records = df.to_dict('records')
        
        logger.info(f"Processed {len(records)} records successfully")
        return records
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise

def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform data quality checks on campaign data.
    """
    quality_report = {
        'total_rows': len(df),
        'null_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'date_range': {
            'start': df['date'].min().isoformat() if not df.empty else None,
            'end': df['date'].max().isoformat() if not df.empty else None
        },
        'channels': df['channel'].unique().tolist() if 'channel' in df.columns else [],
        'avg_conversion_rate': df['conversion_rate'].mean() if 'conversion_rate' in df.columns else None
    }
    
    return quality_report

def aggregate_by_channel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate campaign data by channel.
    """
    if df.empty:
        return df
    
    aggregated = df.groupby('channel').agg({
        'clicks': 'sum',
        'conversions': 'sum',
        'conversion_rate': 'mean'
    }).reset_index()
    
    # Recalculate conversion rate based on totals
    aggregated['conversion_rate'] = (aggregated['conversions'] / aggregated['clicks']) * 100
    
    return aggregated

def aggregate_by_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate campaign data by date.
    """
    if df.empty:
        return df
    
    aggregated = df.groupby('date').agg({
        'clicks': 'sum',
        'conversions': 'sum',
        'conversion_rate': 'mean'
    }).reset_index()
    
    aggregated['conversion_rate'] = (aggregated['conversions'] / aggregated['clicks']) * 100
    
    return aggregated
