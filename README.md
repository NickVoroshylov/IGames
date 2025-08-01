# IGame

This project is a simple **Game Retrieval Service** that allows users to access and manage game data through a backend API. It comes with pre-configured user roles and provides a starting point for building a more comprehensive game management system.

---

## Features

- Pre-created user accounts with **Admin** and **Editor** roles
- REST API for game data retrieval and management
- Dockerized for easy deployment
- Makefile for convenient command shortcuts
- Environment configuration through `.env` file

---

## Default Users

Upon the first launch, two user accounts are created automatically:

| Role   | Username | Password |
|--------|----------|----------|
| Admin  | admin    | admin    |
| Editor | editor   | editor   |

These accounts allow immediate access for administration and content editing.

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your machine
- [Docker Compose](https://docs.docker.com/compose/install/) (usually bundled with Docker Desktop)
- Optional: `make` utility (commonly available on Linux/macOS, can be installed on Windows via WSL or other tools)

---

### Step 1: Environment Configuration

The project uses environment variables for configuration. These are stored in a `.env` file.

1. Copy the provided example file:

   ```bash
   cp example.env .env
   ```

2. The defaults should work for local development.

---

### Step 2: Build and Run the Service

You can choose one of two methods to run the service:

#### Option A: Using Docker Compose

Build the Docker images and start the containers with:

```bash
docker-compose up --build
```

This command will:

- Build the backend service image  
- Apply all migrations and seed the database  
- Start the application along with any dependencies (e.g., database)

To stop the service, press `Ctrl + C` and optionally run:

```bash
docker-compose down
```

to remove containers and networks.

#### Option B: Using Makefile

If you have `make` installed, you can use the predefined shortcuts for faster workflows.

Common commands:

- `make build` — build all necessary Docker images without starting containers
- `make up` — build images if needed and start containers (similar to `docker-compose up --build`)
- `make stop` — stop and remove containers
- Other commands may be defined in the Makefile to simplify testing, linting, or other tasks

Check the Makefile content for more available commands.

---

### Step 3: Accessing the Service

Once the service is running, you can:

- Access API endpoints according to the project's API documentation
- Log in using the default users:
  - Admin: `admin` / `admin`
  - Editor: `editor` / `editor`

Use these credentials to authenticate and explore the application features.

---

## Development and Contribution

This project is a starting template and can be extended or improved in several ways.

### Areas for Improvement

1. **Improve Project Structure**  
   Refactor codebase to follow best practices for scalability and maintainability. Separate modules and services more clearly, organize folders logically.

2. **Expand Test Coverage**  
   Add comprehensive unit and integration tests to cover untested parts of the code to ensure stability and catch regressions early.

3. **Add Caching Mechanism**  
   Implement caching layers (e.g., Redis, in-memory caches) to improve performance for frequent queries and reduce database load.

4. **Optimize Database Queries and Fix Bugs**  
   Review and optimize all database interactions for efficiency. Identify and resolve small bugs and edge cases to improve reliability.

5. **Add Logging and Monitoring**  
   Implement a logging system and integrate application performance monitoring tools as needed to track errors and system health.

---

## Troubleshooting

- Ensure Docker and Docker Compose are installed and running properly.
- Verify `.env` file is correctly named and variables are properly set.
- If ports are occupied, modify the `.env` or Docker Compose file to use different ports.
- Check container logs for errors using:

  ```bash
  docker-compose logs -f
  ```
