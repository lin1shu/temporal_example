# Temporal Server Setup

## Location
The Temporal server files are located at:
```
/Users/yishu/code/temporal-server
```

## Starting the Temporal Server
To start the Temporal server:

1. Navigate to the Temporal server directory:
   ```bash
   cd /Users/yishu/code/temporal-server
   ```

2. Start the server using Docker Compose:
   ```bash
   docker-compose up -d
   ```

   This will start all necessary containers:
   - temporal (main server)
   - temporal-ui (web interface)
   - temporal-postgresql (database)
   - temporal-elasticsearch (for advanced visibility)
   - temporal-admin-tools (CLI tools)

3. Wait a few moments for all services to initialize.

4. Access the Temporal Web UI at:
   ```
   http://localhost:8080
   ```

5. The Temporal server will be available at `localhost:7233` for your applications to connect to.

## Shutting Down the Temporal Server
To shut down the Temporal server:

1. Navigate to the Temporal server directory:
   ```bash
   cd /Users/yishu/code/temporal-server
   ```

2. Stop and remove all containers:
   ```bash
   docker-compose down
   ```

## Using the Temporal CLI (tctl)
You can use the Temporal CLI to interact with the server:

1. Create an alias for convenience:
   ```bash
   alias tctl="docker exec temporal-admin-tools tctl"
   ```

2. Example command to register a new namespace:
   ```bash
   tctl --ns test-namespace namespace register -rd 1
   ```

## Troubleshooting
If you see connection errors like "Connection refused" when trying to connect to the Temporal server:

1. Check if the server is running:
   ```bash
   docker ps | grep temporal
   ```

2. If no containers are running, start the server as described above.

3. Make sure your application is connecting to the correct address (`localhost:7233`). 