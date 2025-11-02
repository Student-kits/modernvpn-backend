# Deployment Guide

## Local Development

1. Copy `.env.example` to `.env` and fill in the variables
2. Build and run locally for development:
   ```bash
   docker-compose up --build
   ```
3. Create initial admin/user via `/users/create`
4. Use `/vpn/assign` to generate client configuration

## Production Deployment

### Security Considerations
- Use HTTPS (nginx reverse proxy)
- Use proper secret management (HashiCorp Vault)
- Run database migrations with Alembic
- Configure proper firewall rules
- Use strong JWT secrets
- Rotate WireGuard keys regularly

### Monitoring
- Connect Prometheus to `/metrics` endpoint
- Import Grafana dashboard for visualization
- Set up log aggregation
- Monitor VPN server health

### Infrastructure
- Use Terraform for infrastructure as code
- Configure cloud-init for server provisioning
- Set up automated backups
- Implement disaster recovery procedures

## API Endpoints

- `GET /health` - Health check
- `POST /auth/login` - User authentication
- `POST /users/create` - Create new user
- `GET /users/me` - Get current user
- `POST /vpn/assign` - Assign VPN configuration
- `GET /vpn/servers` - List available servers
- `POST /ads/event` - Track ad events
- `GET /admin/stats` - Admin statistics

## Database Schema

- `users` - User accounts and authentication
- `vpn_configs` - VPN configurations per user
- `ad_events` - Ad tracking and analytics

## Scripts

- `scripts/rotate_keys.sh` - WireGuard key rotation
