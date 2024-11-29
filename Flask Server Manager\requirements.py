#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SetupServerManager:
    def __init__(self):
        self.root_dir = Path("server-manager")
        self.required_commands = {
            "node": "16.0.0",
            "npm": "6.0.0",
        }
        self.directories = [
            "app/static/js/components",
            "app/static/js/store",
            "app/static/js/api", 
            "app/static/js/utils",
            "app/static/js/tests",
            "deployment/kubernetes",
            "docs"
        ]
        
    def check_requirements(self):
        """Check if required commands are available and meet version requirements"""
        logger.info("Checking system requirements...")
        
        missing = []
        for cmd, min_version in self.required_commands.items():
            try:
                version = subprocess.check_output([cmd, "--version"], 
                                               stderr=subprocess.PIPE).decode().strip()
                logger.info(f"✓ {cmd} version: {version}")
            except FileNotFoundError:
                missing.append(cmd)
                logger.error(f"✗ {cmd} not found")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error checking {cmd}: {e}")
                missing.append(cmd)
                
        if missing:
            logger.error("\nMissing required dependencies:")
            for cmd in missing:
                logger.error(f"- {cmd}")
            logger.error("\nPlease install missing dependencies and try again")
            return False
            
        logger.info("All system requirements met!")
        return True

    def create_directory_structure(self):
        """Create the project directory structure"""
        logger.info("Creating directory structure...")
        
        try:
            if self.root_dir.exists():
                logger.warning(f"Directory {self.root_dir} already exists!")
                if input("Would you like to remove it? (y/n): ").lower() == 'y':
                    shutil.rmtree(self.root_dir)
                else:
                    return False
                    
            self.root_dir.mkdir()
            os.chdir(self.root_dir)
            
            for directory in self.directories:
                Path(directory).mkdir(parents=True)
                logger.info(f"✓ Created {directory}")
            return True
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            return False

    def create_env_file(self):
        """Create .env file with default configuration"""
        logger.info("Creating .env file...")
        
        try:
            env_contents = """# Database
DATABASE_URL=postgresql://user:password@localhost:5432/server_manager

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=change-this-in-production

# Server
PORT=3000
NODE_ENV=development
"""
            
            with open(".env", "w") as f:
                f.write(env_contents)
            logger.info("✓ Created .env file")
            return True
        except Exception as e:
            logger.error(f"Error creating .env file: {e}")
            return False

    def initialize_npm(self):
        """Initialize npm and install dependencies"""
        logger.info("Initializing npm project...")
        
        try:
            subprocess.run(["npm", "init", "-y"], check=True, 
                         stderr=subprocess.PIPE)
            
            logger.info("Installing dependencies...")
            dependencies = [
                "vue@next",
                "vuex@next", 
                "vue-router@4",
                "axios",
                "chart.js",
                "ws"
            ]
            
            dev_dependencies = [
                "jest",
                "@vue/test-utils",
                "cypress",
                "@vue/cli-service",
                "eslint",
                "prettier"
            ]
            
            subprocess.run(["npm", "install", *dependencies], check=True, 
                         stderr=subprocess.PIPE)
            subprocess.run(["npm", "install", "--save-dev", *dev_dependencies], 
                         check=True, stderr=subprocess.PIPE)
            
            logger.info("✓ Installed npm dependencies")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error during npm initialization: {e}")
            logger.error(f"Error output: {e.stderr.decode()}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during npm initialization: {e}")
            return False

    def create_docker_files(self):
        """Create Dockerfile and docker-compose.yml"""
        logger.info("Creating Docker configuration...")
        
        try:
            dockerfile_contents = """FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
"""
            
            docker_compose_contents = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: server_manager
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  redis:
    image: redis:6
    ports:
      - "6379:6379"
"""
            
            with open("Dockerfile", "w") as f:
                f.write(dockerfile_contents)
                
            with open("docker-compose.yml", "w") as f:
                f.write(docker_compose_contents)
                
            logger.info("✓ Created Docker configuration files")
            return True
        except Exception as e:
            logger.error(f"Error creating Docker files: {e}")
            return False

    def setup(self):
        """Run the complete setup process"""
        logger.info("Starting Server Manager setup...\n")
        
        steps = [
            (self.check_requirements, "Checking requirements"),
            (self.create_directory_structure, "Creating directory structure"),
            (self.create_env_file, "Creating .env file"),
            (self.initialize_npm, "Initializing npm"),
            (self.create_docker_files, "Creating Docker files")
        ]
        
        for step_func, step_name in steps:
            logger.info(f"\nExecuting: {step_name}")
            try:
                if not step_func():
                    logger.error(f"Failed at: {step_name}")
                    return False
            except Exception as e:
                logger.error(f"Error during {step_name}: {e}")
                return False
        
        logger.info("\nSetup complete! Next steps:")
        logger.info("1. Review and update .env configuration")
        logger.info("2. Start the development environment:")
        logger.info("   docker-compose up")
        logger.info("3. Access the application at http://localhost:3000")
        return True

if __name__ == "__main__":
    try:
        setup = SetupServerManager()
        if not setup.setup():
            sys.exit(1)
    except KeyboardInterrupt:
        logger.error("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nUnexpected error during setup: {e}")
        sys.exit(1)