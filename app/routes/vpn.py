from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User, VPNConfig
from app.routes.auth import get_current_user
from app.utils import random_token
import subprocess
import ipaddress
import os
from typing import List, Dict

router = APIRouter(prefix='/vpn')

# Mock server data - in production, this would come from a database or cloud provider API
MOCK_SERVERS = [
    {
        "id": "us-east-1",
        "region": "US East (Virginia)",
        "ip": "198.51.100.10",
        "country": "US",
        "city": "Virginia",
        "load": 15,
        "status": "online",
        "ping": 45
    },
    {
        "id": "eu-west-1",
        "region": "EU West (Frankfurt)",
        "ip": "203.0.113.25",
        "country": "DE",
        "city": "Frankfurt",
        "load": 32,
        "status": "online",
        "ping": 78
    },
    {
        "id": "asia-south-1",
        "region": "Asia South (Mumbai)",
        "ip": "192.0.2.150",
        "country": "IN",
        "city": "Mumbai",
        "load": 8,
        "status": "online",
        "ping": 23
    },
    {
        "id": "eu-north-1",
        "region": "EU North (Stockholm)",
        "ip": "198.51.100.75",
        "country": "SE",
        "city": "Stockholm",
        "load": 42,
        "status": "online",
        "ping": 89
    },
    {
        "id": "us-west-1",
        "region": "US West (California)",
        "ip": "203.0.113.200",
        "country": "US",
        "city": "California",
        "load": 67,
        "status": "maintenance",
        "ping": 95
    }
]

def generate_wireguard_keys():
    """Generate WireGuard private and public key pair"""
    try:
        # Generate private key
        private_key = subprocess.run(
            ['wg', 'genkey'], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        
        # Generate public key from private key
        public_key = subprocess.run(
            ['wg', 'pubkey'], 
            input=private_key, 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        
        return private_key, public_key
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback for environments without wg command
        return f"demo_private_key_{random_token(8)}", f"demo_public_key_{random_token(8)}"

def allocate_client_ip(server_id: str, user_id: int) -> str:
    """Allocate IP address for client based on server and user"""
    # Simple IP allocation based on user ID and server
    # In production, maintain a proper IP pool per server
    base_networks = {
        "us-east-1": "10.1.0.0/24",
        "eu-west-1": "10.2.0.0/24", 
        "asia-south-1": "10.3.0.0/24",
        "eu-north-1": "10.4.0.0/24",
        "us-west-1": "10.5.0.0/24"
    }
    
    network = base_networks.get(server_id, "10.9.0.0/24")
    network_obj = ipaddress.IPv4Network(network)
    
    # Calculate client IP based on user ID (avoid network and broadcast)
    client_ip_int = int(network_obj.network_address) + 2 + (user_id % 250)
    client_ip = str(ipaddress.IPv4Address(client_ip_int))
    
    return f"{client_ip}/32"

@router.get('/servers')
async def list_servers(current_user: User = Depends(get_current_user)):
    """List available VPN servers"""
    try:
        # Filter out servers in maintenance
        active_servers = [s for s in MOCK_SERVERS if s['status'] == 'online']
        
        # Sort by load (lowest first)
        active_servers.sort(key=lambda x: x['load'])
        
        return {
            "servers": active_servers,
            "total": len(active_servers),
            "regions": list(set(s['country'] for s in active_servers))
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch servers"
        )

@router.post('/assign')
async def assign_vpn(
    assignment_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Assign VPN configuration to user for specific server"""
    try:
        server_id = assignment_data.get('serverId')
        if not server_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Server ID required"
            )
        
        # Find the server
        server = next((s for s in MOCK_SERVERS if s['id'] == server_id), None)
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Server not found"
            )
        
        if server['status'] != 'online':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Server is not available"
            )
        
        # Check if user already has a config for this server
        result = await db.execute(
            select(VPNConfig).filter(
                VPNConfig.user_id == current_user.id,
                VPNConfig.server_id == server_id
            )
        )
        existing_config = result.scalars().first()
        
        if existing_config:
            # Return existing configuration
            client_config = generate_client_config(
                existing_config.private_key,
                existing_config.ip_address,
                server
            )
            return {
                "success": True,
                "message": "Using existing VPN configuration",
                "server": server,
                "config": client_config,
                "config_id": existing_config.id
            }
        
        # Generate new WireGuard keys
        private_key, public_key = generate_wireguard_keys()
        
        # Allocate IP address
        client_ip = allocate_client_ip(server_id, current_user.id)
        
        # Store configuration in database
        vpn_config = VPNConfig(
            user_id=current_user.id,
            server_id=server_id,
            private_key=private_key,
            public_key=public_key,
            ip_address=client_ip
        )
        
        db.add(vpn_config)
        await db.commit()
        await db.refresh(vpn_config)
        
        # Generate client configuration
        client_config = generate_client_config(private_key, client_ip, server)
        
        return {
            "success": True,
            "message": "VPN configuration created successfully",
            "server": server,
            "config": client_config,
            "config_id": vpn_config.id,
            "instructions": {
                "download": "Save this config as a .conf file",
                "import": "Import into your WireGuard client",
                "connect": "Enable the VPN connection"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign VPN configuration"
        )

@router.get('/configs')
async def get_user_configs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all VPN configurations for current user"""
    try:
        result = await db.execute(
            select(VPNConfig).filter(VPNConfig.user_id == current_user.id)
        )
        configs = result.scalars().all()
        
        config_list = []
        for config in configs:
            server = next((s for s in MOCK_SERVERS if s['id'] == config.server_id), None)
            config_list.append({
                "id": config.id,
                "server_id": config.server_id,
                "server_name": server['region'] if server else "Unknown",
                "ip_address": config.ip_address,
                "created_at": config.created_at,
                "status": "active"
            })
        
        return {
            "configs": config_list,
            "total": len(config_list)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch configurations"
        )

@router.delete('/configs/{config_id}')
async def delete_config(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a VPN configuration"""
    try:
        result = await db.execute(
            select(VPNConfig).filter(
                VPNConfig.id == config_id,
                VPNConfig.user_id == current_user.id
            )
        )
        config = result.scalars().first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuration not found"
            )
        
        await db.delete(config)
        await db.commit()
        
        return {
            "success": True,
            "message": "VPN configuration deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete configuration"
        )

def generate_client_config(private_key: str, client_ip: str, server: dict) -> str:
    """Generate WireGuard client configuration file"""
    # Mock server public key (in production, each server would have its own)
    server_public_key = f"server_pub_key_{server['id']}"
    
    config = f"""[Interface]
PrivateKey = {private_key}
Address = {client_ip}
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = {server_public_key}
Endpoint = {server['ip']}:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25

# Server: {server['region']}
# Location: {server['city']}, {server['country']}
# Generated for ModernVPN
"""
    
    return config