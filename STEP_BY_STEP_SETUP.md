# Stock Market Monitor - Step-by-Step Setup Guide

Follow these steps exactly to get your Stock Market Live Data Monitor running with Docker Compose.

---

## 📋 Step 1: Install Prerequisites

### Install Docker Desktop

1. **Download Docker Desktop**
   - Visit: https://www.docker.com/products/docker-desktop
   - Choose your operating system (Windows/Mac/Linux)
   - Download the installer

2. **Install Docker Desktop**
   - **Windows**: 
     - Run the installer
     - Enable WSL 2 when prompted
     - Restart your computer if required
   - **Mac**: 
     - Open the .dmg file
     - Drag Docker to Applications
   - **Linux**: 
     - Follow instructions at https://docs.docker.com/engine/install/

3. **Start Docker Desktop**
   - Open Docker Desktop application
   - Wait for it to fully start (whale icon should be steady)

4. **Verify Installation**
   - Open Terminal (Mac/Linux) or PowerShell (Windows)
   - Run these commands:
   ```bash
   docker --version
   docker-compose --version
   ```
   - You should see version numbers (e.g., Docker version 24.0.x, docker-compose version 2.x.x)

---

## 📂 Step 2: Navigate to Project Directory

1. **Open Terminal/PowerShell**

2. **Navigate to the project folder**
   ```bash
   cd "c:\Users\GS\Desktop\Research Paper\SD"
   ```

3. **Verify you're in the right location**
   ```bash
   dir  # Windows
   ls   # Mac/Linux
   ```
   - You should see `docker-compose.yml` file listed

---

## 🔧 Step 3: Fix Docker Compose File (Important!)

The current `docker-compose.yml` has duplicate content. Let me know if you want me to fix it, or you can manually edit it.

**What needs to be fixed**: The file has the entire configuration duplicated (appears twice). We need to keep only one copy.

---

## 🚀 Step 4: Build and Start All Services

1. **Build and start all containers** (First time - takes 5-10 minutes)
   ```bash
   docker-compose up --build
   ```

2. **What you'll see**:
   - Docker will download base images (postgres, redis, rabbitmq, node, python)
   - Build each service (5 backend services + 1 frontend)
   - Start all containers
   - Show logs from all services

3. **Wait for these messages** (indicates services are ready):
   ```
   ✓ postgres    | database system is ready to accept connections
   ✓ redis       | Ready to accept connections
   ✓ rabbitmq    | Server startup complete
   ✓ api-gateway | Running on http://0.0.0.0:5000
   ✓ frontend    | Compiled successfully!
   ```

---

## ✅ Step 5: Verify Services Are Running

1. **Check all containers are up**
   - Open a NEW terminal/PowerShell window
   - Run:
   ```bash
   docker-compose ps
   ```

2. **You should see 8 services running**:
   - ✓ stock-postgres
   - ✓ stock-redis
   - ✓ stock-rabbitmq
   - ✓ stock-user-service
   - ✓ stock-fetcher
   - ✓ stock-processor
   - ✓ stock-alert-service
   - ✓ stock-api-gateway
   - ✓ stock-frontend

---

## 🌐 Step 6: Access the Application

Open your web browser and visit:

### Main Application
- **Frontend**: http://localhost:3000
  - This is your main user interface

### API Endpoints
- **API Gateway**: http://localhost:5000
  - Test: http://localhost:5000/health

### Admin Interfaces
- **RabbitMQ Management**: http://localhost:15672
  - Username: `stockuser`
  - Password: `stockpass123`

---

## 🧪 Step 7: Test the Application

### Register a New User

1. **Open**: http://localhost:3000
2. **Click**: "Register" or "Sign Up"
3. **Fill in**:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `password123`
4. **Click**: "Register"

### Login

1. **Use the credentials** you just created
2. **Click**: "Login"

### Add Stocks to Watchlist

1. **Search for a stock** (e.g., AAPL, GOOGL, MSFT)
2. **Click**: "Add to Watchlist"
3. **View real-time updates**

### Set Price Alerts

1. **Go to a stock detail page**
2. **Set alert**: "Notify me when price goes above/below X"
3. **Save alert**

---

## 🛑 Step 8: Stop the Application

### Option A: Stop (Keep Data)
```bash
docker-compose stop
```
- Stops all containers
- Keeps all data (database, cache)
- Quick to restart

### Option B: Stop and Remove Containers
```bash
docker-compose down
```
- Stops and removes containers
- Keeps data in volumes
- Restart requires rebuild

### Option C: Complete Cleanup (Delete Everything)
```bash
docker-compose down -v
```
- ⚠️ **WARNING**: Deletes ALL data
- Removes containers, networks, AND volumes
- Use only if you want a fresh start

---

## 🔄 Step 9: Restart the Application

### If you used `docker-compose stop`:
```bash
docker-compose start
```
- Fast restart (1-2 minutes)

### If you used `docker-compose down`:
```bash
docker-compose up -d
```
- Starts in background (detached mode)
- Takes 2-3 minutes

### View logs after starting:
```bash
docker-compose logs -f
```
- Press `Ctrl+C` to stop viewing logs (containers keep running)

---

## 🐛 Common Issues & Solutions

### Issue 1: "Port already in use"

**Error**: `Bind for 0.0.0.0:3000 failed: port is already allocated`

**Solution**:
```bash
# Find what's using the port (Windows)
netstat -ano | findstr :3000

# Find what's using the port (Mac/Linux)
lsof -i :3000

# Kill the process or change the port in docker-compose.yml
```

### Issue 2: "Cannot connect to Docker daemon"

**Solution**:
1. Open Docker Desktop
2. Wait for it to fully start
3. Try the command again

### Issue 3: Services keep restarting

**Check logs**:
```bash
docker-compose logs user-service
docker-compose logs postgres
```

**Common causes**:
- Database not ready → Wait 30 seconds and check again
- Out of memory → Increase Docker Desktop memory (Settings → Resources)

### Issue 4: Frontend shows "Cannot connect to server"

**Solution**:
```bash
# Check if API Gateway is running
docker-compose ps api-gateway

# Check API Gateway logs
docker-compose logs api-gateway

# Restart API Gateway
docker-compose restart api-gateway
```

### Issue 5: Database connection errors

**Solution**:
```bash
# Check PostgreSQL is healthy
docker exec stock-postgres pg_isready -U stockuser

# If not ready, restart it
docker-compose restart postgres

# Wait 10 seconds, then restart dependent services
docker-compose restart user-service alert-service
```

---

## 📊 Monitoring & Logs

### View All Logs (Live)
```bash
docker-compose logs -f
```

### View Specific Service Logs
```bash
docker-compose logs -f api-gateway
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f rabbitmq
```

### View Last 100 Lines
```bash
docker-compose logs --tail=100 user-service
```

### Check Service Status
```bash
docker-compose ps
```

### Check Resource Usage
```bash
docker stats
```

---

## 🗄️ Database Management

### Access PostgreSQL
```bash
docker exec -it stock-postgres psql -U stockuser -d stockdb
```

### Common SQL Commands
```sql
-- List all tables
\dt

-- View users
SELECT * FROM users;

-- View watchlists
SELECT * FROM watchlists;

-- View alerts
SELECT * FROM alerts;

-- Exit
\q
```

### Backup Database
```bash
docker exec stock-postgres pg_dump -U stockuser stockdb > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
docker exec -i stock-postgres psql -U stockuser stockdb < backup_20251120.sql
```

---

## 🔐 Default Credentials

### PostgreSQL
- **Host**: localhost
- **Port**: 5432
- **User**: stockuser
- **Password**: stockpass123
- **Database**: stockdb

### RabbitMQ
- **Host**: localhost
- **Port**: 5672 (AMQP), 15672 (Management UI)
- **User**: stockuser
- **Password**: stockpass123

### Redis
- **Host**: localhost
- **Port**: 6379
- **Password**: (none)

> ⚠️ **IMPORTANT**: Change these passwords before deploying to production!

---

## 🎯 Quick Reference Commands

| Action | Command |
|--------|---------|
| Start (first time) | `docker-compose up --build` |
| Start (background) | `docker-compose up -d` |
| Stop | `docker-compose stop` |
| Stop & remove | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Check status | `docker-compose ps` |
| Restart service | `docker-compose restart <service-name>` |
| Rebuild service | `docker-compose up -d --build <service-name>` |
| Clean everything | `docker-compose down -v` |

---

## 📞 Need Help?

1. **Check the logs first**: `docker-compose logs -f`
2. **Verify all services are running**: `docker-compose ps`
3. **Check Docker Desktop** has enough resources (Settings → Resources)
4. **Restart Docker Desktop** if things seem stuck
5. **Try a clean restart**: `docker-compose down && docker-compose up --build`

---

## ✨ Next Steps

Once everything is running:

1. ✅ Register an account
2. ✅ Add stocks to your watchlist
3. ✅ Set up price alerts
4. ✅ Explore the real-time dashboard
5. ✅ Check RabbitMQ management UI to see messages flowing
6. ✅ Monitor logs to understand the system

---

**Happy Trading! 📈**
