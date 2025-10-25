# AdTech Analytics Platform

A comprehensive advertising technology analytics platform for processing campaign data, tracking CTR (Click-Through Rate), conversion rates, and providing real-time visualization with multi-user query support.

## Features

- **Campaign Data Processing**: Upload and process CSV files containing campaign data with CTR calculation
- **Multi-User Support**: Authentication system supporting admin, analyst, manager, and user roles
- **Real-time Analytics**: Interactive dashboard with filtering and visualization capabilities
- **Performance Metrics**: Track impressions, clicks, conversions, CTR, and conversion rates
- **Multi-language Interface**: Support for English, French, and Chinese languages
- **Data Export**: Export analytics data to CSV format
- **Secure API**: JWT-based authentication for secure data access
- **Dual Application Architecture**: FastAPI backend + Streamlit dashboard

## Technology Stack

- **Backend**: FastAPI with PostgreSQL database and SQLAlchemy 2.x
- **Frontend**: Streamlit dashboard with Plotly interactive charts  
- **Data Processing**: Pandas for data manipulation, validation, and CTR calculation
- **Authentication**: JWT tokens for secure multi-user API access
- **Caching**: In-memory cache for improved query performance
- **Database**: PostgreSQL with trust authentication

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database (running and accessible)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/LinneaShao/Extended-AdTech-Analytics.git
cd Extended-AdTech-Analytics
```

2. Set up virtual environment:
```bash
python -m venv env311
source env311/bin/activate  # On Windows: env311\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file with:
ADMIN_PASSWORD=admin123
USER_PASSWORD=user123
```

5. Start the platform:
```bash
chmod +x start_services.sh
./start_services.sh
```

### Manual Startup

If you prefer to start services manually:

```bash
# Terminal 1 - API Backend
source env311/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Dashboard
source env311/bin/activate
streamlit run dashboard.py --server.port 8501
```

## Usage

### Access Points

- **API Backend**: http://localhost:8000
- **Interactive Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

### Authentication

The platform supports multiple user roles:

- **admin** / admin123 - Full access
- **analyst** / analyst123 - Data analysis access
- **manager** / manager123 - Management access
- **user** / user123 - Basic access

### Data Upload

Upload CSV files with the following format:

```csv
date,campaign,channel,impressions,clicks,cost,conversions
2024-01-01,Campaign_A,Google,45230,892,234.50,23
2024-01-01,Campaign_A,Facebook,32100,567,189.75,15
```

Required columns: `date`, `channel`, `clicks`, `conversions`
Optional columns: `campaign`, `impressions`, `cost`

The system automatically calculates:
- **CTR**: (clicks / impressions) × 100
- **Conversion Rate**: (conversions / clicks) × 100

### API Endpoints

- `GET /` - API information
- `POST /auth/login` - User authentication
- `POST /data/upload` - Upload campaign data (requires auth)
- `GET /data/stats` - Retrieve statistics (requires auth)
- `GET /health` - Health check

### Dashboard Features

- **Multi-language Support**: Switch between English, French, and Chinese
- **Interactive Filtering**: Filter by date range and channel
- **Real-time Charts**: Channel performance and conversion trends
- **Data Export**: Download filtered data as CSV
- **Key Metrics**: Total clicks, conversions, and conversion rates

## Development

### Project Structure

```
Extended-AdTech-Analytics/
├── main.py              # FastAPI backend application
├── dashboard.py         # Streamlit interactive dashboard
├── database.py          # PostgreSQL operations and models
├── data_processing.py   # Campaign data processing and validation
├── cache.py            # In-memory caching system
├── auth.py             # JWT authentication utilities
├── requirements.txt    # Python dependencies
├── start_services.sh   # Service startup script
├── data/
│   └── sample.csv      # Sample campaign data
└── README.md           # Documentation
```

### Database Schema

The `ad_data` table contains:

- `id` - Primary key
- `date` - Campaign date
- `channel` - Marketing channel (Google, Facebook, etc.)
- `campaign` - Campaign name
- `impressions` - Ad impressions count
- `clicks` - Click count
- `conversions` - Conversion count
- `cost` - Campaign cost
- `ctr` - Click-through rate (calculated)
- `conversion_rate` - Conversion rate (calculated)

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - Open source project for AdTech analytics and campaign optimization.

## Support

For issues and questions, please check:
- API logs: `tail -f api.log`
- Dashboard logs: `tail -f dashboard.log`
- Database connectivity: Ensure PostgreSQL is running on localhost:5432
echo "ADMIN_PASSWORD=your_secure_password" > .env
```

5. Set up PostgreSQL database:
```sql
CREATE DATABASE adtech_db;
```

### Running the Application

1. Start the API server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. Start the dashboard (in a new terminal):
```bash
streamlit run dashboard.py --server.port 8501
```

3. Access the application:
- **API Documentation**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

## API Usage

### Authentication

```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "your_password"}'
```

### Upload Data

```bash
curl -X POST "http://localhost:8000/data/upload" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@data/sample.csv"
```

### Get Statistics

```bash
curl -X GET "http://localhost:8000/data/stats?channel=Google" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

## Data Format

Expected CSV format for campaign data:

```csv
date,campaign,channel,impressions,clicks,cost,conversions
2024-01-01,Campaign_A,Google,45230,892,234.50,23
2024-01-01,Campaign_A,Facebook,32100,567,189.75,15
```

Required columns:
- `date`: Campaign date (YYYY-MM-DD)
- `channel`: Marketing channel (Google, Facebook, etc.)
- `clicks`: Number of clicks
- `conversions`: Number of conversions

## Project Structure

```
Extended-AdTech-Analytics/
├── main.py              # FastAPI application
├── dashboard.py         # Streamlit dashboard
├── database.py          # Database operations
├── data_processing.py   # Data validation and processing
├── cache.py            # Caching utilities
├── auth.py             # Authentication functions
├── requirements.txt     # Python dependencies
├── data/               # Sample data files
└── README.md           # Project documentation
```

## Development

### Running Tests

```bash
# Test API endpoints
python -c "
import requests
response = requests.get('http://localhost:8000/health')
print(f'Health check: {response.status_code}')
"
```

### Database Schema

The application uses a simple schema with one main table:

```sql
CREATE TABLE ad_data (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    channel VARCHAR(50) NOT NULL,
    clicks INTEGER NOT NULL,
    conversions INTEGER NOT NULL,
    conversion_rate FLOAT NOT NULL
);
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

**Author**: LinneaShao  
**Email**: oceanfueler@gmail.com  
**GitHub**: [@LinneaShao](https://github.com/LinneaShao)
