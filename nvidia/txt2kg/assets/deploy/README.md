# Deployment Configuration

This directory contains all deployment-related configuration for the txt2kg project.

## Structure

- **compose/**: Docker Compose files for local development and testing
  - `docker-compose.yml`: Main Docker Compose configuration
  - `docker-compose.gnn.yml`: Docker Compose configuration for GNN components
  - `docker-compose.neo4j.yml`: Docker Compose configuration for Neo4j

- **docker/**: Docker-related files
  - Dockerfile
  - Initialization scripts for services

- **services/**: Containerized services
  - **gnn_model/**: Graph Neural Network model service
  - **sentence-transformers/**: Sentence transformer service for embeddings

## Usage

To start the default services:

```bash
docker-compose -f deploy/compose/docker-compose.yml up
```

To include GNN components:

```bash
docker-compose -f deploy/compose/docker-compose.yml -f deploy/compose/docker-compose.gnn.yml up
```

To include Neo4j:

```bash
docker-compose -f deploy/compose/docker-compose.yml -f deploy/compose/docker-compose.neo4j.yml up
```