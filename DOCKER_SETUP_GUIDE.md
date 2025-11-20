# Stock Market Live Data Monitor - Docker Compose Setup Guide

This guide provides complete instructions to run the Stock Market Live Data Monitor application using Docker Compose.

## Prerequisites

### Required Software

1. **Docker Desktop** (version 20.10 or higher)
   - Download from: https://www.docker.com/products/docker-desktop
   - Includes Docker Engine and Docker Compose
   - **Windows**: Ensure WSL 2 is enabled
   - **Mac**: Native support
   - **Linux**: Install Docker Engine + Docker Compose separately

2. **Git** (optional, for version control)
   - Download from: https://git-scm.com/downloads

### System Requirements

- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: At least 10GB free
- **CPU**: 4 cores recommended
- **OS**: Windows 10/11, macOS 10.15+, or Linux

## Project Architecture

The application consists of the following services:

### Backend Services (Python/Flask)
- **API Gateway** (Port 5000) - Main entry point for all API requests
- **User Service** (Port 5004) - User authentication and watchlist management
- **Stock Fetcher Service** (Port 5001) - Fetches real-time stock data
- **Stock Processor Service** (Port 5002) - Processes and stores stock data
- **Alert Service** (Port 5003) - Manages price alerts

### Infrastructure Services
- **PostgreSQL** (Port 5432) - Primary database for users, watchlists, and alerts
- **Redis** (Port 6379) - Caching layer for performance
- **RabbitMQ** (Ports 5672, 15672) - Message broker for inter-service communication

### Frontend
- **React App** (Port 3000) - User interface

## Quick Start

### Step 1: Verify Docker Installation

Open a terminal/command prompt and run:

```bash
docker --version
docker-compose --version
```

You should see version numbers for both commands.

### Step 2: Navigate to Project Directory

```bash
cd "c:\Users\GS\Desktop\Research Paper\SD"
```

### Step 3: Build and Start All Services

Run the following command to build and start all containers:

```bash
docker-compose up --build
```

> **Note**: The first build will take 5-10 minutes as it downloads base images and installs dependencies.

### Step 4: Wait for Services to Start

Monitor the logs. You should see messages indicating services are ready:
- PostgreSQL: `database system is ready to accept connections`
- RabbitMQ: `Server startup complete`
- Redis: `Ready to accept connections`
- Backend services: `Running on http://0.0.0.0:PORT`

### Step 5: Access the Application

Once all services are running:

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:5000
- **RabbitMQ Management UI**: http://localhost:15672 (username: `stockuser`, password: `stockpass123`)

## Detailed Commands

### Start Services in Background (Detached Mode)

```bash
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Stop Services

```bash
# Stop all services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (deletes all data)
docker-compose down -v
```

### Restart a Specific Service

```bash
docker-compose restart user-service
docker-compose restart frontend
```

### Rebuild a Specific Service

```bash
docker-compose up -d --build user-service
```

### Check Service Status

```bash
docker-compose ps
```

### Execute Commands Inside a Container

```bash
# Access PostgreSQL
docker exec -it stock-postgres psql -U stockuser -d stockdb

# Access Redis CLI
docker exec -it stock-redis redis-cli

# Access a backend service shell
docker exec -it stock-user-service /bin/sh
```

## Environment Configuration

### Default Credentials

**PostgreSQL:**
- User: `stockuser`
- Password: `stockpass123`
- Database: `stockdb`

**RabbitMQ:**
- User: `stockuser`
- Password: `stockpass123`

**JWT Secret:**
- Key: `your-secret-key-change-in-production`

> **⚠️ IMPORTANT**: Change these credentials in production!

### Customizing Environment Variables

Create a `.env` file in the project root to override default values:

```env
# Database
POSTGRES_USER=stockuser
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=stockdb

# RabbitMQ
RABBITMQ_DEFAULT_USER=stockuser
RABBITMQ_DEFAULT_PASS=your_secure_password

# JWT
JWT_SECRET_KEY=your_very_secure_secret_key

# Stock Fetcher
FETCH_INTERVAL=30
```

## Troubleshooting

### Issue: Port Already in Use

**Error**: `Bind for 0.0.0.0:5000 failed: port is already allocated`

**Solution**: Stop the service using that port or change the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "5001:5000"  # Maps host port 5001 to container port 5000
```

### Issue: Services Not Starting

**Check logs**:
```bash
docker-compose logs [service-name]
```

**Common causes**:
- Insufficient memory (increase Docker Desktop memory allocation)
- Missing dependencies (rebuild with `--build` flag)
- Database connection issues (ensure PostgreSQL is healthy)

### Issue: Database Connection Errors

**Solution**: Ensure PostgreSQL is fully started before other services:

```bash
# Check PostgreSQL health
docker exec stock-postgres pg_isready -U stockuser

# Restart dependent services
docker-compose restart user-service alert-service
```

### Issue: Frontend Can't Connect to Backend

**Check**:
1. API Gateway is running: `docker-compose ps api-gateway`
2. Network connectivity: `docker network inspect sd_stock-network`
3. Environment variables in frontend container

### Issue: RabbitMQ Connection Refused

**Solution**:
```bash
# Check RabbitMQ status
docker exec stock-rabbitmq rabbitmq-diagnostics ping

# Restart RabbitMQ
docker-compose restart rabbitmq

# Wait 10-15 seconds, then restart dependent services
docker-compose restart stock-fetcher alert-service
```

### Issue: Out of Disk Space

**Clean up Docker resources**:
```bash
# Remove unused containers, networks, images
docker system prune -a

# Remove all volumes (⚠️ deletes all data)
docker volume prune
```

## Data Persistence

Data is persisted in Docker volumes:

- `postgres-data`: PostgreSQL database files
- `redis-data`: Redis cache data
- `rabbitmq-data`: RabbitMQ message queue data

### Backup Database

```bash
# Create backup
docker exec stock-postgres pg_dump -U stockuser stockdb > backup.sql

# Restore backup
docker exec -i stock-postgres psql -U stockuser stockdb < backup.sql
```

## Development Workflow

### Making Code Changes

1. **Backend Services**: Edit Python files, then rebuild:
   ```bash
   docker-compose up -d --build user-service
   ```

2. **Frontend**: Edit React files, then rebuild:
   ```bash
   docker-compose up -d --build frontend
   ```

### Hot Reload (Development Mode)

For faster development, you can mount source code as volumes (requires modifying `docker-compose.yml`):

```yaml
user-service:
  volumes:
    - ./backend/user-service:/app
```

## Testing the Application

### 1. Register a User

```bash
curl -X POST http://localhost:5000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

### 2. Login

```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 3. Access Frontend

Open http://localhost:3000 in your browser and:
- Register a new account
- Login
- Add stocks to watchlist
- Set price alerts
- View real-time stock data

## Production Deployment

### Security Checklist

- [ ] Change all default passwords
- [ ] Use strong JWT secret key
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up proper logging
- [ ] Enable database backups
- [ ] Use environment-specific configurations
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerts

### Recommended Changes for Production

1. **Use environment files**: Store secrets in `.env` files (not committed to Git)
2. **Enable SSL**: Use reverse proxy (Nginx/Traefik) with SSL certificates
3. **Resource limits**: Add CPU/memory limits to services
4. **Health checks**: Ensure all services have proper health checks
5. **Logging**: Configure centralized logging (ELK stack, Grafana)
6. **Monitoring**: Set up Prometheus + Grafana for metrics

## Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose Reference**: https://docs.docker.com/compose/
- **PostgreSQL Docker**: https://hub.docker.com/_/postgres
- **RabbitMQ Docker**: https://hub.docker.com/_/rabbitmq
- **Redis Docker**: https://hub.docker.com/_/redis

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Verify service health: `docker-compose ps`
3. Review this guide's troubleshooting section
4. Check Docker Desktop resources (CPU, Memory, Disk)

---

**Last Updated**: November 2025
