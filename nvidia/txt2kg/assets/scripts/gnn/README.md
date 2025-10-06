# TXT2KG Pipeline with ArangoDB Integration

This project provides a two-stage pipeline for knowledge graph-based question answering:

1. **Data Preprocessing** (`preprocess_data.py`): Extracts knowledge graph triples from either ArangoDB or using TXT2KG, and prepares the dataset.
2. **Model Training & Testing** (`train_test_gnn.py`): Trains and evaluates a GNN-based retriever model on the preprocessed dataset.

## Prerequisites

- Python 3.8+
- ArangoDB running (can be set up using the provided docker-compose.yml)
- PyTorch and PyTorch Geometric installed
- All dependencies listed in requirements.txt

## Installation

1. Install the required dependencies:

```bash
pip install -r scripts/requirements.txt
```

2. Ensure ArangoDB is running. You can use the docker-compose file:

```bash
docker-compose up -d arangodb arangodb-init
```

## Usage

### Stage 1: Data Preprocessing

Run the preprocessing script to prepare the dataset:

```bash
python scripts/preprocess_data.py --use_arango --output_dir ./output
```

#### Loading data from ArangoDB

Use the `--use_arango` flag to load triples from ArangoDB instead of generating them with TXT2KG:

```bash
python scripts/preprocess_data.py --use_arango
```

The script will connect to ArangoDB using the default settings from docker-compose.yml:
- URL: http://localhost:8529
- Database: txt2kg
- No auth (username and password are empty)

#### Custom ArangoDB Connection

You can specify custom ArangoDB connection parameters:

```bash
python scripts/preprocess_data.py --use_arango --arango_url "http://localhost:8529" --arango_db "your_db" --arango_user "username" --arango_password "password"
```

#### Using TXT2KG (original behavior)

If you don't pass the `--use_arango` flag, the script will use the original TXT2KG approach:

```bash
python scripts/preprocess_data.py --NV_NIM_KEY "your-nvidia-api-key"
```

### Stage 2: Model Training & Testing

After preprocessing the data, train and test the model:

```bash
python scripts/train_test_gnn.py --output_dir ./output
```

#### Training Options

You can customize training with options:

```bash
python scripts/train_test_gnn.py --output_dir ./output --gnn_hidden_channels 2048 --num_gnn_layers 6 --epochs 5 --batch_size 2
```

#### Evaluation Only

To evaluate a previously trained model without retraining:

```bash
python scripts/train_test_gnn.py --output_dir ./output --eval_only
```

## Expected Data Format in ArangoDB

The script expects ArangoDB to have:

1. A document collection named `entities` containing nodes with a `name` property
2. An edge collection named `relationships` where:
   - Edges have a `type` property (the predicate/relationship type)
   - Edges connect from and to entities in the `entities` collection

## How It Works

### Data Preprocessing (`preprocess_data.py`)
1. Connects to ArangoDB and queries all triples in the format "subject predicate object" (or generates them with TXT2KG)
2. Creates a knowledge graph from these triples
3. Prepares the dataset with training, validation, and test splits

### Model Training & Testing (`train_test_gnn.py`)
1. Loads the preprocessed dataset
2. Initializes a GNN model (GAT architecture) and an LLM for generation
3. Trains the model on the training set, validating on the validation set
4. Evaluates the trained model on the test set using the LLMJudge for scoring

## Limitations

- The script assumes that your ArangoDB instance contains data in the format described above
- You need to have both question-answer pairs and corpus documents available
- Make sure your ArangoDB contains knowledge graph triples relevant to your corpus
- Large LLM models require significant GPU memory for training 