import click
from flask.cli import with_appcontext
from app import db
from app.models import User, Server
import os
import sys

@click.group()
def cli():
    """Flask Server Manager CLI tools"""
    pass

@cli.command()
@click.option('--username', prompt=True)
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--role', default='user')
@with_appcontext
def create_user(username, email, password, role):
    """Create a new user"""
    try:
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"User {username} created successfully")
    except Exception as e:
        click.echo(f"Error creating user: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--name', prompt=True)
@click.option('--host', prompt=True)
@click.option('--port', prompt=True, type=int)
@click.option('--owner-email', prompt=True)
@with_appcontext
def create_server(name, host, port, owner_email):
    """Create a new server"""
    try:
        owner = User.query.filter_by(email=owner_email).first()
        if not owner:
            click.echo("Owner not found", err=True)
            sys.exit(1)
            
        server = Server(
            name=name,
            host=host,
            port=port,
            owner_id=owner.id
        )
        db.session.add(server)
        db.session.commit()
        click.echo(f"Server {name} created successfully")
    except Exception as e:
        click.echo(f"Error creating server: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@with_appcontext
def list_servers():
    """List all servers"""
    servers = Server.query.all()
    if not servers:
        click.echo("No servers found")
        return
        
    for server in servers:
        click.echo(f"ID: {server.id}")
        click.echo(f"Name: {server.name}")
        click.echo(f"Host: {server.host}")
        click.echo(f"Port: {server.port}")
        click.echo(f"Status: {server.status}")
        click.echo("---")

@cli.command()
@click.argument('server_id', type=int)
@with_appcontext
def server_status(server_id):
    """Get server status"""
    server = Server.query.get(server_id)
    if not server:
        click.echo("Server not found", err=True)
        sys.exit(1)
        
    click.echo(f"Server: {server.name}")
    click.echo(f"Status: {server.status}")
    click.echo(f"Last Active: {server.last_active}")

@cli.command()
@click.option('--days', default=7, help='Number of days of logs to keep')
@with_appcontext
def cleanup_logs(days):
    """Clean up old logs"""
    from datetime import datetime, timedelta
    from app.models import ServerLog, ActivityLog
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    try:
        # Clean up server logs
        deleted_server_logs = ServerLog.query.filter(
            ServerLog.timestamp < cutoff
        ).delete()
        
        # Clean up activity logs
        deleted_activity_logs = ActivityLog.query.filter(
            ActivityLog.timestamp < cutoff
        ).delete()
        
        db.session.commit()
        
        click.echo(f"Deleted {deleted_server_logs} server logs")
        click.echo(f"Deleted {deleted_activity_logs} activity logs")
    except Exception as e:
        click.echo(f"Error cleaning up logs: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()