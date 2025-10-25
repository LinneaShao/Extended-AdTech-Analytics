"""
Database operations for AdTech campaign data storage and retrieval.
"""

from sqlalchemy import create_engine, Column, Integer, String, Date, Float, text
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = 'postgresql://vivian@localhost:5432/adtech_db'

Base = declarative_base()

class AdData(Base):
    """Campaign data model"""
    __tablename__ = 'ad_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    channel = Column(String(50), nullable=False)
    campaign = Column(String(100), nullable=True)
    impressions = Column(Integer, nullable=True)
    clicks = Column(Integer, nullable=False)
    conversions = Column(Integer, nullable=False)
    cost = Column(Float, nullable=True)
    ctr = Column(Float, nullable=True)  # Click-through rate
    conversion_rate = Column(Float, nullable=False)

# Initialize database connection
try:
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    logger.info("Database connection established")
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    raise

def save_data(records: List[Dict[str, Any]]) -> int:
    """
    Save processed campaign data to database.
    """
    session = SessionLocal()
    try:
        saved_count = 0
        for record in records:
            ad_record = AdData(
                date=record['date'],
                channel=record['channel'],
                campaign=record.get('campaign'),
                impressions=int(record['impressions']) if record.get('impressions') else None,
                clicks=int(record['clicks']),
                conversions=int(record['conversions']),
                cost=float(record['cost']) if record.get('cost') else None,
                ctr=float(record['ctr']) if record.get('ctr') else None,
                conversion_rate=float(record['conversion_rate'])
            )
            session.add(ad_record)
            saved_count += 1
        
        session.commit()
        logger.info(f"Saved {saved_count} records to database")
        return saved_count
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error saving data: {e}")
        raise
    finally:
        session.close()

def get_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    channel: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve campaign statistics with optional filters.
    """
    session = SessionLocal()
    try:
        query = session.query(AdData)
        
        # Apply filters
        if start_date:
            query = query.filter(AdData.date >= start_date)
        if end_date:
            query = query.filter(AdData.date <= end_date)
        if channel:
            query = query.filter(AdData.channel == channel)
        
        results = query.all()
        
        # Convert to dictionaries
        data = []
        for record in results:
            data.append({
                'id': record.id,
                'date': record.date.isoformat(),
                'channel': record.channel,
                'clicks': record.clicks,
                'conversions': record.conversions,
                'conversion_rate': round(record.conversion_rate, 2)
            })
        
        # Calculate summary statistics
        total_clicks = sum(r['clicks'] for r in data)
        total_conversions = sum(r['conversions'] for r in data)
        avg_conversion_rate = total_conversions / total_clicks * 100 if total_clicks > 0 else 0
        
        return {
            'data': data,
            'summary': {
                'total_records': len(data),
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'avg_conversion_rate': round(avg_conversion_rate, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise
    finally:
        session.close()

def get_channel_summary() -> List[Dict[str, Any]]:
    """
    Get summary statistics grouped by channel.
    """
    session = SessionLocal()
    try:
        query = text("""
            SELECT 
                channel,
                COUNT(*) as record_count,
                SUM(clicks) as total_clicks,
                SUM(conversions) as total_conversions,
                AVG(conversion_rate) as avg_conversion_rate
            FROM ad_data 
            GROUP BY channel 
            ORDER BY total_clicks DESC
        """)
        
        result = session.execute(query)
        
        summary = []
        for row in result:
            summary.append({
                'channel': row.channel,
                'record_count': row.record_count,
                'total_clicks': row.total_clicks,
                'total_conversions': row.total_conversions,
                'avg_conversion_rate': round(row.avg_conversion_rate, 2)
            })
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting channel summary: {e}")
        raise
    finally:
        session.close()

def health_check() -> bool:
    """
    Check database connectivity.
    """
    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
