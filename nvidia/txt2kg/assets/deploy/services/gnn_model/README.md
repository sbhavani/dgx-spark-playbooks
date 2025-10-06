# GNN Model Service

This service provides a REST API for serving predictions from a Graph Neural Network (GNN) model trained to enhance RAG (Retrieval Augmented Generation) performance. It allows comparing GNN-based knowledge graph retrieval with traditional RAG approaches.

## Overview

The service exposes a simple API to:
- Load a pre-trained GNN model that combines graph structures with language models
- Process queries by incorporating graph-structured knowledge
- Return predictions that leverage both text and graph relationships

## Getting Started

### Prerequisites

- Docker and Docker Compose
- The trained model file (created using `train_export.py`)

### Running the Service

The service is included in the main docker-compose configuration. Simply run:

```bash
docker-compose up -d
```

This will start the GNN model service along with other services in the system.

## Training the Model

Before using the service, you need to train the GNN model:

```bash
# Create the models directory if it doesn't exist
mkdir -p models

# Run the training script
python deploy/services/gnn_model/train_export.py --output_dir models
```

This will create the `tech-qa-model.pt` file in the models directory, which the service will load.

## API Endpoints

### Health Check

```
GET /health
```

Returns the health status of the service.

### Prediction

```
POST /predict
```

Request body:
```json
{
  "question": "Your question here",
  "context": "Retrieved context information"
}
```

Response:
```json
{
  "question": "Your question here",
  "answer": "The generated answer"
}
```

## Using the Client Example

A simple client script is provided to test the service:

```bash
python deploy/services/gnn_model/client_example.py --question "What is the capital of France?" --context "France is a country in Western Europe. Its capital is Paris, which is known for the Eiffel Tower."
```

This script also includes a placeholder for comparing the GNN-based approach with a traditional RAG approach.

## Architecture

The GNN model service uses:
- A Graph Attention Network (GAT) to process graph structured data
- A Language Model (LLM) to generate answers
- A combined architecture (GRetriever) that leverages both components

## Limitations

- The current implementation requires graph construction to be handled separately
- The `create_graph_from_text` function in the service is a placeholder that needs implementation based on your specific graph construction approach 