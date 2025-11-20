# 🚀 Quick Start Checklist

Use this checklist to get your Stock Market Monitor running in minutes!

---

## ✅ Pre-Flight Checklist

- [ ] **Docker Desktop installed and running**
  - Check: Open Docker Desktop app - whale icon should be steady
  - Verify: Run `docker --version` in terminal

- [ ] **Minimum 8GB RAM available**
  - Check: Docker Desktop → Settings → Resources

- [ ] **At least 10GB free disk space**

---

## 🎯 5-Minute Setup

### 1️⃣ Open Terminal
- **Windows**: PowerShell or Command Prompt
- **Mac/Linux**: Terminal

### 2️⃣ Navigate to Project
```bash
cd "c:\Users\GS\Desktop\Research Paper\SD"
```

### 3️⃣ Start Everything
```bash
docker-compose up --build
```

### 4️⃣ Wait for Success Messages
Look for these in the logs:
- ✅ `postgres | database system is ready`
- ✅ `redis | Ready to accept connections`
- ✅ `rabbitmq | Server startup complete`
- ✅ `api-gateway | Running on http://0.0.0.0:5000`
- ✅ `frontend | Compiled successfully!`

### 5️⃣ Open Browser
Go to: **http://localhost:3000**

---

## 🎉 You're Done!

Now you can:
1. Register a new account
2. Add stocks to watchlist
3. Set price alerts
4. View real-time data

---

## 🛠️ Common Commands

| What you want to do | Command |
|---------------------|---------|
| **Start** (first time) | `docker-compose up --build` |
| **Start** (background) | `docker-compose up -d` |
| **Stop** | `docker-compose stop` |
| **View logs** | `docker-compose logs -f` |
| **Check status** | `docker-compose ps` |
| **Restart** | `docker-compose restart` |
| **Clean up** | `docker-compose down` |

---

## 🔗 Important URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Create account |
| **API** | http://localhost:5000 | - |
| **RabbitMQ UI** | http://localhost:15672 | user: `stockuser`<br>pass: `stockpass123` |

---

## ❌ Troubleshooting

### Problem: Port already in use
```bash
# Stop the conflicting service or change port in docker-compose.yml
```

### Problem: Docker not running
```bash
# Open Docker Desktop and wait for it to start
```

### Problem: Services keep restarting
```bash
# Check logs
docker-compose logs -f

# Increase Docker memory (Settings → Resources → Memory → 4GB+)
```

### Problem: Can't connect to frontend
```bash
# Restart everything
docker-compose down
docker-compose up --build
```

---

## 📋 Service Health Check

Run this to see all services:
```bash
docker-compose ps
```

You should see **9 services** all "Up":
1. ✅ stock-postgres
2. ✅ stock-redis  
3. ✅ stock-rabbitmq
4. ✅ stock-user-service
5. ✅ stock-fetcher
6. ✅ stock-processor
7. ✅ stock-alert-service
8. ✅ stock-api-gateway
9. ✅ stock-frontend

---

## 🆘 Need More Help?

See detailed guides:
- 📖 [STEP_BY_STEP_SETUP.md](./STEP_BY_STEP_SETUP.md) - Comprehensive guide
- 📖 [DOCKER_SETUP_GUIDE.md](./DOCKER_SETUP_GUIDE.md) - Advanced configuration

---

**Ready? Let's go! 🚀**

```bash
docker-compose up --build
```
