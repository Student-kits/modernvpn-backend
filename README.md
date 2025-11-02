# ModernVPN Backend

A comprehensive FastAPI backend for ModernVPN control plane featuring WireGuard integration, user management, and ad tracking capabilities.

## Features

- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- **WireGuard Integration**: Server and client configuration management
- **User Authentication**: JWT-based authentication with bcrypt password hashing
- **Database Management**: Async SQLAlchemy with PostgreSQL
- **Ad Tracking**: Event-based advertising analytics
- **Admin Panel**: Administrative endpoints for system management
- **Docker Support**: Fully containerized with docker-compose
- **Security**: Best practices for VPN key management and rotation

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL (managed via Docker)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Student-kits/modernvpn-backend.git
   cd modernvpn-backend
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application:**
   ```bash
   docker-compose up --build
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Project Structure

```
modernvpn-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application setup
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── utils.py             # Utility functions
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── users.py         # User management
│       ├── vpn.py           # VPN configuration
│       ├── ads.py           # Ad tracking
│       └── admin.py         # Admin endpoints
├── scripts/
│   └── rotate_keys.sh       # WireGuard key rotation
├── deploy/
│   └── README.md            # Deployment guide
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### User Management
- `GET /users/me` - Get current user profile
- `POST /users/create` - Create new user account

### VPN Management
- `POST /vpn/assign` - Assign VPN configuration to user
- `GET /vpn/servers` - List available VPN servers

### Analytics
- `POST /ads/event` - Track advertising events

### Administration
- `GET /admin/stats` - System statistics
- `GET /health` - Health check endpoint

## Database Schema

### Users
- User accounts with email/password authentication
- Admin privilege management
- Account creation timestamps

### VPN Configurations
- Per-user WireGuard configurations
- Server assignments and IP allocations
- Public/private key management

### Ad Events
- Event tracking (views, clicks, conversions)
- Metadata storage for analytics
- User attribution

## Configuration

Key environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT token signing
- `HETZNER_API_TOKEN`: Hetzner Cloud API token (optional)
- `WG_BASE_DIR`: WireGuard configuration directory
- `WG_LISTEN_PORT`: WireGuard listen port
- `ADMIN_EMAIL`: Default admin email

## Development

### Local Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL:**
   ```bash
   docker-compose up db
   ```

3. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Testing

```bash
# Run tests (when implemented)
pytest

# Check code formatting
black app/
flake8 app/
```

## Security

- JWT tokens for API authentication
- Bcrypt password hashing
- WireGuard key rotation script
- Environment-based configuration
- CORS middleware for browser support

## Deployment

See `deploy/README.md` for detailed production deployment instructions including:

- HTTPS configuration with nginx
- Secret management with HashiCorp Vault
- Database migrations with Alembic
- Monitoring with Prometheus and Grafana
- Terraform infrastructure provisioning

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the deployment guide in `deploy/README.md`
- Review API documentation at `/docs` endpoint

## Roadmap

- [ ] Complete VPN server provisioning
- [ ] Implement advanced analytics
- [ ] Add rate limiting
- [ ] WebSocket support for real-time updates
- [ ] Multi-region server support
- [ ] Advanced admin dashboard
- [ ] API versioning
- [ ] Comprehensive test suite