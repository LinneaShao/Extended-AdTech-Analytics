#!/bin/bash

# Extended AdTech Analytics - Service Startup Script
# Starts both FastAPI backend and Streamlit dashboard

set -e

echo "🚀 Starting AdTech Analytics Platform..."

# Check if virtual environment exists
if [ ! -d "env311" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python -m venv env311"
    echo "   source env311/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source env311/bin/activate

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Kill existing services
echo "🧹 Cleaning up existing services..."
pkill -f "uvicorn main:app" >/dev/null 2>&1 || true
pkill -f "streamlit run dashboard.py" >/dev/null 2>&1 || true

# Wait a moment for processes to terminate
sleep 2

# Start FastAPI backend
echo "📡 Starting FastAPI backend on port 8000..."
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > api.log 2>&1 &
API_PID=$!

# Wait for API to start
sleep 3

# Check if API is running
if ! curl -s http://localhost:8000/health >/dev/null; then
    echo "❌ Failed to start FastAPI backend"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo "✅ FastAPI backend started successfully"

# Start Streamlit dashboard
echo "📊 Starting Streamlit dashboard on port 8501..."
nohup streamlit run dashboard.py --server.port 8501 --server.headless true > dashboard.log 2>&1 &
DASHBOARD_PID=$!

# Wait for dashboard to start
sleep 5

# Check if dashboard is running
if ! curl -s http://localhost:8501 >/dev/null; then
    echo "❌ Failed to start Streamlit dashboard"
    kill $API_PID 2>/dev/null || true
    kill $DASHBOARD_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Streamlit dashboard started successfully"

echo ""
echo "🎉 AdTech Analytics Platform is running!"
echo ""
echo "📡 API Backend:    http://localhost:8000"
echo "📊 Dashboard:      http://localhost:8501"
echo "📖 API Docs:       http://localhost:8000/docs"
echo ""
echo "Process IDs:"
echo "  API:       $API_PID"
echo "  Dashboard: $DASHBOARD_PID"
echo ""
echo "To stop services:"
echo "  kill $API_PID $DASHBOARD_PID"
echo ""
echo "Logs:"
echo "  API:       tail -f api.log"
echo "  Dashboard: tail -f dashboard.log"