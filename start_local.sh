#!/bin/bash

echo "========================================"
echo "Learning Coach - Local Development"
echo "========================================"
echo ""

echo "Starting Backend Server..."
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
cd ..

echo "Waiting for backend to start..."
sleep 3

echo ""
echo "Starting Frontend Server..."
python -m http.server 3000 &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Servers are running!"
echo "========================================"
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend:   http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

