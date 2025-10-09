# 🚀 Backend Startup Guide

## Starting the Backend

### Basic Command

```bash
python app.py
```

### If Port 8080 is in Use (Alternative Port)

```bash
python -c "from app import app; app.run(debug=True, host='0.0.0.0', port=9000)"
```

Or kill the process using port 8080:

```bash
# Check what's using port 8080
lsof -ti:8080

# Kill the process
kill -9 $(lsof -ti:8080)

# Or kill any Python app.py process
pkill -f "python app.py"
```

### Background Mode

```bash
nohup python app.py > app.log 2>&1 &
```

## Checking if Backend is Running

### Check Port Status

```bash
lsof -ti:8080
```

### Check Running Processes

```bash
ps aux | grep "python app.py" | grep -v grep
```

### Test the API

```bash
# Health check
curl http://localhost:8080/health

# Root endpoint
curl http://localhost:8080/
```

## Stopping the Backend

### Kill by Port

```bash
kill -9 $(lsof -ti:8080)
```

### Kill by Process Name

```bash
pkill -f "python app.py"
```

## Quick Start Sequence

1. **Install dependencies** (first time only):

   ```bash
   pip install -r requirements.txt
   # or
   pip install flask flask-cors google-generativeai python-dotenv sentence-transformers
   ```

2. **Set up environment** (create `.env` file):

   ```
   GEMINI_API_KEY=your_api_key_here
   ```


3. **Start the server**:

   ```bash
   python app.py
   ```

4. **Verify it's running**:
   ```bash
   curl http://localhost:8080/health
   ```

## Server Details

- **Default URL**: `http://localhost:8080`
- **Default Port**: `8080`
- **Debug Mode**: Enabled (auto-reload on code changes)
- **CORS**: Enabled for all origins

## Common Issues

### Issue: "Address already in use"

**Solution**: Port 8080 is taken

```bash
# Option 1: Kill the process
kill -9 $(lsof -ti:8080)

# Option 2: Use different port (edit app.py line 482)
# Change: app.run(debug=True, host='0.0.0.0', port=8080)
# To:     app.run(debug=True, host='0.0.0.0', port=9000)
```

### Issue: Import errors

**Solution**: Update dependencies

```bash
pip install --upgrade sentence-transformers huggingface_hub
```

## API Endpoints

Once running, visit `http://localhost:8080/` for full API documentation.

**Main Endpoints:**

- `GET /` - API overview
- `GET /health` - Health check
- `POST /ask` - Ask questions
- `POST /teach` - Teaching modes
- `POST /quiz` - Generate quizzes
- `POST /study-plan` - Get study plans

---

**Quick Command Reference:**

```bash
# Start
python app.py

# Stop
pkill -f "python app.py"

# Restart
pkill -f "python app.py" && python app.py

# Check status
lsof -ti:8080
```
