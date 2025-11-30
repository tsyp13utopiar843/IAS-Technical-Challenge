# 🚀 Quick Start - Docker Compose

## Start Everything with ONE Command!

```bash
docker-compose up
```

That's it! All services will start:
- ✅ MQTT Broker (Mosquitto)
- ✅ Orchestrator (port 8000)
- ✅ Planner (port 8011)
- ✅ PM Agent (port 8001)
- ✅ Energy Agent (port 8002)
- ✅ Cyber Agent (port 8003)
- ✅ Safety Agent (port 8004)
- ✅ PPE Agent (port 8005)
- ✅ Publisher (data simulator)

## Common Commands

```bash
# Start in background (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f orchestrator

# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Stop and remove volumes
docker-compose down -v
```

## Then Start Frontend Separately

```bash
cd Frontend
pnpm dev
# Frontend runs on http://localhost:3000
```

## Verify Everything is Running

```bash
# Check service health
curl http://localhost:8000/system-state
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
```

## Production Deployment

See **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** for:
- Railway backend deployment
- Vercel frontend deployment
- Production environment configuration

---

**Note**: First run will take a few minutes to build Docker images. Subsequent runs are much faster!
