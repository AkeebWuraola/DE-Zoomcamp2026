# Docker for Data Engineering - Complete Guide

## Table of Contents
- [Introduction to Docker](#introduction-to-docker)
- [Docker Basics](#docker-basics)
- [Setting Up PostgreSQL with Docker](#setting-up-postgresql-with-docker)
- [Docker Networking](#docker-networking)
- [pgAdmin Setup](#pgadmin-setup)
- [Python Integration with Docker](#python-integration-with-docker)
- [Docker Compose](#docker-compose)
- [Common Issues and Solutions](#common-issues-and-solutions)

---

## Introduction to Docker

Docker is a containerization platform that allows us to isolate software in a similar way to virtual machines but in a much leaner way. It provides isolated containers where you can run applications in a containerized environment.

### Key Concepts

**Docker Image**: A snapshot of a container that we can define to run our software or data pipelines. By exporting Docker images to cloud providers such as Amazon Web Services or Google Cloud Platform, we can run our containers there.

**Dockerfile**: A file where you specify your installations for building your Docker container and creating an image.

**Docker Compose**: A tool for running multiple Docker containers together.

---

## Docker Basics

### Testing Your Docker Setup

Run an Ubuntu container to test your Docker installation:

```bash
docker run -it ubuntu bash
```

To exit Docker: `Ctrl+D`

### Building Docker Images

The `docker build` command builds an image from a Dockerfile:

```bash
docker build -t test:pandas .
```

- `test` is the image name
- `.` means Docker should build an image in the current directory
- Docker will look for a Dockerfile and use it to build the image

### Managing Containers

Stop a container:
```bash
docker stop <container_id_or_name>
```

Kill a container:
```bash
docker kill <container_id_or_name>
```

List running containers:
```bash
docker ps
```

Remove a stopped container:
```bash
docker rm <container_name>
```

---

## Setting Up PostgreSQL with Docker

### Basic PostgreSQL Setup

#### Method 1: Direct Docker Run

```bash
docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:18
```

**Alternative with full path:**
```bash
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v /home/user/data-engineering-zoomcamp-test/week_1_basics_n_setup/2_docker_sql/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:13
```

**Command Breakdown:**
- Creates and runs a PostgreSQL database container
- `--rm`: Automatically removes the container when it stops
- `-e`: Sets environment variables
- `-v`: Mounts a volume for data persistence
- `-p`: Maps port 5432 from container to host

#### Method 2: Using Docker Compose (Recommended)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:18
    container_name: ny_taxi_postgres
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: ny_taxi
    volumes:
      - ./ny_taxi_postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

Run the service:
```bash
docker-compose up
```

Stop the service:
```bash
docker-compose down
```

#### Method 3: Custom Dockerfile

If you need custom configurations or initialization scripts:

```dockerfile
FROM postgres:18

ENV POSTGRES_USER=root
ENV POSTGRES_PASSWORD=root
ENV POSTGRES_DB=ny_taxi

# Optional: Add initialization scripts
# COPY init.sql /docker-entrypoint-initdb.d/
```

Build and run:
```bash
# Build the image
docker build -t my-postgres .

# Run the container
docker run -it --rm \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  my-postgres
```

### Connecting to PostgreSQL with pgcli

Install pgcli:
```bash
uv add --dev pgcli
```

Connect to PostgreSQL:
```bash
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi
```

**Alternative connection method (recommended):**
```bash
uv run pgcli postgresql://root:root@localhost:5432/ny_taxi
```

Format: `postgresql://username:password@host:port/database`

### Basic PostgreSQL Commands

Inside PostgreSQL:

```sql
-- List all tables and schemas
\dt

-- Create a sample table
CREATE TABLE test(id INTEGER, name VARCHAR(50));

-- Insert data
INSERT INTO test VALUES(1, 'Hello Docker');

-- Query data
SELECT * FROM test;

-- Quit PostgreSQL
\q
```

---

## Docker Networking

When running multiple containers that need to communicate (e.g., PostgreSQL and pgAdmin), you must connect them using a Docker network.

### Creating a Network

```bash
docker network create pg-network
```

### Running Containers in a Network

**PostgreSQL Container:**
```bash
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v /home/user/data-engineering-zoomcamp/01-docker-terraform/2_docker_sql/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network=pg-network \
  --name pg-database \
  postgres:13
```

**Note:** The `--name` parameter serves as the hostname for container-to-container communication.

---

## pgAdmin Setup

### Pull and Run pgAdmin

Pull the image:
```bash
docker pull dpage/pgadmin4
```

Run pgAdmin (interactive mode):
```bash
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  dpage/pgadmin4
```

Run pgAdmin (detached mode):
```bash
docker run -p 8080:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@admin.com \
  -e PGADMIN_DEFAULT_PASSWORD=root \
  -d \
  dpage/pgadmin4
```

### Running pgAdmin in a Network

To connect pgAdmin to PostgreSQL, both must be in the same network:

```bash
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4
```

Visit `localhost:8080` to access pgAdmin.

### Connecting pgAdmin to PostgreSQL

When setting up the server in pgAdmin:
- **Hostname**: Use the container name from the PostgreSQL container (e.g., `pg-database`)
- **Port**: 5432
- **Username**: root
- **Password**: root
- **Database**: ny_taxi

---

## Python Integration with Docker

### Setting Up Jupyter

Install Jupyter:
```bash
uv add --dev jupyter
```

Run Jupyter:
```bash
uv run jupyter notebook
```

### Converting Notebooks to Python Scripts

In the directory where your notebook exists:

```bash
jupyter nbconvert --to script your_notebook.ipynb
```

With output directory:
```bash
jupyter nbconvert --to script --output-dir=your_output_directory your_notebook.ipynb
```

Example:
```bash
jupyter nbconvert --to script upload-data.ipynb
```

### Running a Python Data Ingestion Script

Once you have a Python script with all necessary database connection parameters:

```bash
URL="https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-01.parquet"

python ingest_data.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table_name=green_tripdata \
  --url=${URL}
```

### Dockerizing the Ingestion Script

Create a Dockerfile with your parameters, then build the image:

```bash
docker build -t taxi_ingest:v001 .
```

Run the dockerized ingestion:

```bash
URL="https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-01.parquet"

docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
  --user=root \
  --password=root \
  --host=pg-database \
  --port=5432 \
  --db=ny_taxi \
  --table_name=green_tripdata \
  --url=${URL}
```

**Important:** If you make changes to your Python file after building the Docker image, you must rebuild the image.

### Running Python in Docker

To run Python interactively in a container:

```bash
docker run -it --entrypoint bash python:3.9
```

---

## Docker Compose

When using `docker-compose.yaml`, you don't need to manually create a network. Docker Compose handles networking automatically.

### Basic Commands

Start services:
```bash
docker-compose up
```

Start services in detached mode (returns terminal):
```bash
docker-compose up -d
```

Stop and remove services:
```bash
docker-compose down
```

### Important Notes

- Ensure no conflicting containers are running before executing `docker-compose up`
- Always use detached mode (`-d`) when you need the terminal back

---

## Common Issues and Solutions

### Issue: Unable to Enter Password in PostgreSQL

**Symptom:** Cannot enter password when prompted.

**Solution:** Use the alternative connection string method:
```bash
uv run pgcli postgresql://root:root@localhost:5432/ny_taxi
```

### Issue: Keyring Warning

**Symptom:**
```
Load your password from keyring returned: No recommended backend was available.
```

**Solutions:**
1. Prepare keyring as described at: https://keyring.readthedocs.io/en/stable/
2. Uninstall keyring: `pip uninstall keyring`
3. Disable keyring in configuration: add `keyring = False` to `[main]`

### Issue: Permission Denied on PostgreSQL Data Directory

**Symptom:**
```
connection failed: could not open file "global/pg_filenode.map": Permission denied
```

**Solution:** Set proper ownership for the data directory:
```bash
sudo chown -R 999:999 /path/to/ny_taxi_postgres_data
```

The `999:999` represents the user and group IDs for the PostgreSQL user inside the container. Adjust if needed.

**Alternative for current user:**
```bash
sudo chown -R user:username .
```

### Issue: Docker Image Pull Error

**Symptom:**
```
Unable to find image '8080:80' locally
docker: Error response from daemon: pull access denied for 8080
```

**Solution:** This is a syntax error. Ensure `-e` is not followed directly by `-p`. Check your command syntax:

**Incorrect:**
```bash
docker run -it -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" -e PGADMIN_DEFAULT_PASSWORD="root" -e -p 8080:80 ...
```

**Correct:**
```bash
docker run -it -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" -e PGADMIN_DEFAULT_PASSWORD="root" -p 8080:80 ...
```

### Issue: Container Name Already in Use

**Symptom:**
```
docker: Error response from daemon: Conflict. The container name "/pgadmin" is already in use
```

**Solution:** Stop and remove the existing container:
```bash
docker stop pgadmin
docker rm pgadmin
```

Then run your command again.

### Issue: CSRF Token Missing in pgAdmin

**Symptom:**
```
ERROR pgadmin: 400 Bad Request: The CSRF session token is missing.
```

**Solution:** Add the following environment variables to the pgAdmin service in your `docker-compose.yml`:

```yaml
environment:
  - PGADMIN_DEFAULT_EMAIL=admin@admin.com
  - PGADMIN_DEFAULT_PASSWORD=root
  - PGADMIN_CONFIG_WTF_CSRF_CHECK_DEFAULT=False
  - PGADMIN_CONFIG_WTF_CSRF_ENABLED=False
```

---

## Best Practices

1. **Always specify full paths** when mounting volumes to avoid confusion
2. **Use Docker Compose** for multi-container setups instead of manual networking
3. **Rebuild Docker images** after making changes to your application code
4. **Use descriptive container names** to make networking and debugging easier
5. **Run containers in detached mode** (`-d`) when you don't need to see logs in real-time
6. **Clean up stopped containers** regularly to free up resources
7. **Use environment variables** for sensitive information like passwords
8. **Document your setup** including port mappings and volume mounts

---

## Quick Reference

### Essential Docker Commands

```bash
# Build image
docker build -t <image_name>:<tag> .

# Run container
docker run -it <image_name>

# List running containers
docker ps

# Stop container
docker stop <container_id>

# Remove container
docker rm <container_id>

# Create network
docker network create <network_name>

# Docker Compose
docker-compose up
docker-compose up -d
docker-compose down
```

### PostgreSQL Connection Strings

```bash
# pgcli
uv run pgcli postgresql://username:password@host:port/database

# Python (SQLAlchemy)
postgresql://username:password@host:port/database
```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [pgAdmin Docker Hub](https://hub.docker.com/r/dpage/pgadmin4/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

*Last Updated: January 2026*