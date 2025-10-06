# Unified GPU Graph Visualization Service

## 🚀 Overview

The unified service combines **PyGraphistry Cloud** and **Local GPU (cuGraph)** processing into a single FastAPI service, giving you maximum flexibility for graph visualization.

## ⚡ Processing Modes

| Mode | Description | Requirements |
|------|-------------|--------------|
| **PyGraphistry Cloud** | Interactive GPU embeds in browser | API credentials |
| **Local GPU (cuGraph)** | Full GPU processing on your hardware | NVIDIA GPU + cuGraph |
| **Local CPU** | NetworkX fallback processing | None |

## 🛠️ Quick Setup

### 1. Set Environment Variables (Optional)
```bash
# For PyGraphistry Cloud features
export GRAPHISTRY_PERSONAL_KEY="your_personal_key"
export GRAPHISTRY_SECRET_KEY="your_secret_key"
```

### 2. Run the Service

#### Option A: Direct Python
```bash
cd services
python unified_gpu_service.py
```

#### Option B: Using Startup Script
```bash
cd services
./start_gpu_services.sh
```

#### Option C: Docker (NVIDIA PyG Container)
```bash
cd services
docker build -t unified-gpu-viz .
docker run --gpus all -p 8080:8080 \
  -e GRAPHISTRY_PERSONAL_KEY="your_key" \
  -e GRAPHISTRY_SECRET_KEY="your_secret" \
  unified-gpu-viz
```

## 📡 API Usage

### Process Graph with Mode Selection

```bash
curl -X POST http://localhost:8080/api/visualize \
  -H "Content-Type: application/json" \
  -d '{
    "graph_data": {
      "nodes": [{"id": "1", "name": "Node 1"}, {"id": "2", "name": "Node 2"}],
      "links": [{"source": "1", "target": "2", "name": "edge_1_2"}]
    },
    "processing_mode": "local_gpu",
    "layout_algorithm": "force_atlas2",
    "clustering_algorithm": "leiden",
    "compute_centrality": true
  }'
```

### Check Available Capabilities

```bash
curl http://localhost:8080/api/capabilities
```

Response:
```json
{
  "processing_modes": {
    "pygraphistry_cloud": {"available": true, "description": "..."},
    "local_gpu": {"available": true, "description": "..."},
    "local_cpu": {"available": true, "description": "..."}
  },
  "has_rapids": true,
  "gpu_available": true
}
```

## 🎯 Frontend Integration

### React Component Usage

```tsx
import { UnifiedGPUViewer } from '@/components/unified-gpu-viewer'

function MyApp() {
  const graphData = {
    nodes: [...],
    links: [...]
  }

  return (
    <UnifiedGPUViewer 
      graphData={graphData}
      onError={(error) => console.error(error)}
    />
  )
}
```

### Mode-Specific Processing

```javascript
// PyGraphistry Cloud mode
const response = await fetch('/api/unified-gpu/visualize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    graph_data: { nodes, links },
    processing_mode: 'pygraphistry_cloud',
    layout_type: 'force',
    clustering: true,
    gpu_acceleration: true
  })
})

// Local GPU mode  
const response = await fetch('/api/unified-gpu/visualize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    graph_data: { nodes, links },
    processing_mode: 'local_gpu',
    layout_algorithm: 'force_atlas2',
    clustering_algorithm: 'leiden',
    compute_centrality: true
  })
})
```

## 🔧 Configuration Options

### PyGraphistry Cloud Mode
- `layout_type`: "force", "circular", "hierarchical"
- `gpu_acceleration`: true/false
- `clustering`: true/false

### Local GPU Mode  
- `layout_algorithm`: "force_atlas2", "spectral", "fruchterman_reingold"
- `clustering_algorithm`: "leiden", "louvain", "spectral"
- `compute_centrality`: true/false

### Local CPU Mode
- Basic processing with NetworkX fallback
- No additional configuration needed

## 📊 Response Format

```json
{
  "processed_nodes": [...],
  "processed_edges": [...],
  "processing_mode": "local_gpu",
  "embed_url": "https://hub.graphistry.com/...", // Only for cloud mode
  "layout_positions": {...}, // Only for local GPU mode
  "clusters": {...},
  "centrality": {...},
  "stats": {
    "node_count": 1000,
    "edge_count": 5000,
    "gpu_accelerated": true,
    "layout_computed": true,
    "clusters_computed": true
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🚀 Benefits of Unified Approach

### ✅ Advantages
- **Single service** - One port, one deployment
- **Mode switching** - Choose best processing per graph
- **Fallback handling** - Graceful degradation if GPU unavailable  
- **Consistent API** - Same interface for all modes
- **Better testing** - Easy comparison between modes

### 🎯 Use Cases
- **PyGraphistry Cloud**: Sharing visualizations, demos, production embeds
- **Local GPU**: Private data, large-scale processing, custom algorithms
- **Local CPU**: Development, testing, small graphs

## 🐛 Troubleshooting

### GPU Not Detected
```bash
# Check GPU availability
nvidia-smi

# Check RAPIDS installation
python -c "import cudf, cugraph; print('RAPIDS OK')"
```

### PyGraphistry Credentials
```bash
# Verify credentials are set
echo $GRAPHISTRY_PERSONAL_KEY
echo $GRAPHISTRY_SECRET_KEY

# Test connection
python -c "import graphistry; graphistry.register(personal_key_id='$GRAPHISTRY_PERSONAL_KEY', personal_key_secret='$GRAPHISTRY_SECRET_KEY'); print('PyGraphistry OK')"
```

### Service Health
```bash
curl http://localhost:8080/api/health
```

## 📈 Performance Tips

1. **Large graphs (>100k nodes)**: Use `local_gpu` mode
2. **Sharing/demos**: Use `pygraphistry_cloud` mode  
3. **Development**: Use `local_cpu` mode for speed
4. **Mixed workloads**: Switch modes dynamically based on graph size 