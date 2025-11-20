# PostgreSQL-Only Architecture Summary

## ✅ System Now Uses PostgreSQL Only

The system has been converted to use **PostgreSQL as the single database** for all data storage:

### PostgreSQL Tables

1. **users** - User accounts (from User Service)
2. **watchlist** - User stock watchlists (from User Service)
3. **alerts** - Triggered alerts (from Alert Service)
4. **alert_rules** - User-defined alert rules (from Alert Service)
5. **stock_history** - Historical stock price data (from Stock Processor Service)

### What Was Removed

- ❌ **MongoDB** - No longer needed
- ✅ **Redis** - Still used for caching and rate limiting
- ✅ **RabbitMQ** - Still used for message queuing

### Benefits

✅ **Simpler Architecture** - One database instead of two  
✅ **ACID Transactions** - Full relational database guarantees  
✅ **Easier Deployment** - Fewer services to manage  
✅ **Lower Resource Usage** - One database engine instead of two  
✅ **Relational Integrity** - Foreign keys and constraints  

### Services Updated

- **Stock Processor Service** - Now uses PostgreSQL with SQLAlchemy ORM
- **Docker Compose** - Removed MongoDB service and volume
- **Configuration** - Updated environment variables

### Docker Compose Services (9 Total)

1. **postgres** - PostgreSQL 15 (ALL data)
2. **redis** - Redis 7 (caching)
3. **rabbitmq** - RabbitMQ 3.12 (message queue)
4. **stock-fetcher** - Stock Fetcher Service
5. **stock-processor** - Stock Processor Service (uses PostgreSQL now)
6. **alert-service** - Alert Service
7. **user-service** - User & Watchlist Service
8. **api-gateway** - API Gateway
9. **frontend** - React Frontend

### To Run

```bash
cd "c:\Users\GS\Desktop\Research Paper\SD"
docker-compose up -d
```

Now only **9 services** instead of 10!
