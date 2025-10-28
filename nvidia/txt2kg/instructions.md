# Step 1. Clone the repository

In a terminal, clone the txt2kg repository and navigate to the project directory.

```bash
git clone ${GITLAB_REPO_BASEURL}
cd dgx-spark-playbook/${MODEL}/assets
```

# Step 2. Start the txt2kg services

Use the provided start script to launch all required services. This will set up Ollama, ArangoDB, and the Next.js frontend:

```bash
./start.sh
```

The script will automatically:
- Check for GPU availability
- Start Docker Compose services
- Set up ArangoDB database
- Launch the web interface

# Step 3. Pull an Ollama model (optional)

Download a language model for knowledge extraction. The default model loaded is Llama 3.1 8B:

```bash
docker exec ollama-compose ollama pull <model-name>
```

Browse available models at [https://ollama.com/search](https://ollama.com/search)

> [!NOTE]
> The unified memory architecture enables running larger models like 70B parameters, which produce significantly more accurate knowledge triples.

# Step 4. Access the web interface

Open your browser and navigate to:

```
http://localhost:3001
```

You can also access individual services:
- **ArangoDB Web Interface**: http://localhost:8529 
- **Ollama API**: http://localhost:11434

# Step 5. Upload documents and build knowledge graphs

### 5.1. Document Upload
- Use the web interface to upload text documents (markdown, text, CSV supported)
- Documents are automatically chunked and processed for triple extraction

### 5.2. Knowledge Graph Generation
- The system extracts subject-predicate-object triples using Ollama
- Triples are stored in ArangoDB for relationship querying

### 5.3. Interactive Visualization
- View your knowledge graph in 2D or 3D with GPU-accelerated rendering
- Explore nodes and relationships interactively

### 5.4. Graph-based Queries
- Ask questions about your documents using the query interface
- Graph traversal enhances context with entity relationships from ArangoDB
- LLM generates responses using the enriched graph context

> **Future Enhancement**: GraphRAG capabilities with vector-based KNN search for entity retrieval are planned.

# Step 6. Cleanup and rollback

Stop all services and optionally remove containers:

```bash
# Stop services
docker compose down

# Remove containers and volumes (optional)
docker compose down -v

# Remove downloaded models (optional)
docker exec ollama-compose ollama rm llama3.1:8b
```

# Step 7. Next steps

- Experiment with different Ollama models for varied extraction quality
- Customize triple extraction prompts for domain-specific knowledge
- Explore advanced graph querying and visualization features
