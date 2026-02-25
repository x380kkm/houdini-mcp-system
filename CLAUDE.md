# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Houdini HDA (Digital Asset) documentation system that combines:
1. **Houdini MCP** - Remote control of Houdini via Model Context Protocol
2. **RAG System** - Retrieval-Augmented Generation for Houdini documentation queries
3. **HDA Documentation Generator** - Automated documentation generation for HDA files

## Architecture

### Three Main Components

1. **houdini_mcp_380kkm/** - MCP server for remote Houdini control
   - Located in `core/houdini_mcp/`
   - Provides tools for node creation, parameter manipulation, rendering, etc.
   - Communicates with Houdini via hrpyc (port 18811 by default)

2. **houdini_rag/** - RAG system for Houdini documentation
   - Scrapes and indexes Houdini official documentation
   - Uses ChromaDB for vector storage
   - Supports OpenAI-compatible APIs for embeddings and LLM queries

3. **Root-level scripts** - HDA documentation workflow
   - `extract_hda_nodes.py` - Extracts node structure from HDA files
   - `generate_hda_doc.py` - Generates documentation using RAG (serial)
   - `generate_hda_doc_parallel.py` - Parallel version with threading (6-8x faster)

### Data Flow

```
HDA File → extract_hda_nodes.py → hda_nodes_list.json
                                         ↓
                                   generate_hda_doc.py
                                         ↓
                                   (queries RAG system)
                                         ↓
                                   hda_docs/timestamp/
                                   ├── HDA_Complete_Documentation.md
                                   ├── VEX_Code_Documentation.md
                                   ├── Node_Types_Documentation.md
                                   └── *.json
```

## Common Commands

### Setup

```bash
# Install Houdini MCP
cd houdini_mcp_380kkm/core
pip install -e .

# Install RAG dependencies
cd ../../houdini_rag
pip install -r requirements.txt

# Configure API key
cp config.example.yaml config.yaml
# Edit config.yaml with your API key
```

### Start Houdini MCP Server

In Houdini Python Shell:
```python
import hrpyc
hrpyc.start_server(port=18811)
```

### Build Vector Database (First Time)

```bash
cd houdini_rag

# Scrape documentation
python cli.py scrape --max-pages 500

# Build index
python cli.py index
```

### Generate HDA Documentation

```bash
# Step 1: Extract nodes from HDA
python extract_hda_nodes.py path/to/your.hda [depth]
# depth: 0=top level only, 1=first child level, -1=all levels (default)

# Step 2: Generate documentation (serial)
python generate_hda_doc.py hda_nodes_list.json

# Step 2 (alternative): Generate with parallel processing
python generate_hda_doc_parallel.py hda_nodes_list.json 10  # 10 threads
```

### RAG System Usage

```bash
cd houdini_rag

# Single query
python cli.py query "How do I create a mountain?"

# Interactive mode
python cli.py query -i

# Similarity search
python cli.py search "heightfield" --top-k 5
```

## Key Implementation Details

### VEX Code Handling

- VEX code is extracted from `attribwrangle` nodes
- VEX explanations use **direct LLM calls** (not RAG queries)
- This avoids embedding API issues with small code snippets
- See `generate_hda_doc.py` line ~125: `rag.llm.invoke(prompt).content`

### Node Type Queries

- Node type documentation uses **RAG queries**
- Queries all node types (no limit)
- Format: "What is the {node_type} node in Houdini?"
- See `generate_hda_doc.py` line ~78

### Parallel Processing

- `generate_hda_doc_parallel.py` uses ThreadPoolExecutor
- Default: 5 workers, configurable via command line
- Thread-safe progress tracking with locks
- Significantly faster for large HDAs (6-8x speedup)

### Configuration

- **API keys**: Store in `houdini_rag/config.yaml` (gitignored)
- **Template**: `config.example.yaml` is tracked in git
- **MCP connection**: Default localhost:18811
- **Vector DB**: Stored in `houdini_rag/data/chroma/`

## Important Files

### Configuration
- `houdini_rag/config.yaml` - API keys and model settings (gitignored)
- `houdini_rag/config.example.yaml` - Template for config

### Core Scripts
- `extract_hda_nodes.py` - HDA node extraction via MCP
- `generate_hda_doc.py` - Serial documentation generation
- `generate_hda_doc_parallel.py` - Parallel documentation generation

### RAG System
- `houdini_rag/rag_engine.py` - Core RAG implementation
- `houdini_rag/scraper.py` - Documentation scraper
- `houdini_rag/indexer.py` - Vector index builder
- `houdini_rag/cli.py` - Command-line interface

### Output
- `hda_nodes_list.json` - Extracted node structure
- `hda_docs/YYYYMMDD_HHMMSS/` - Generated documentation

## Testing

```bash
# RAG system tests
cd houdini_rag
python test_units.py
python test_integration.py

# MCP tests
cd houdini_mcp_380kkm
pytest tests/
```

## Notes

- The system requires a running Houdini instance with hrpyc server
- Vector database must be built before generating documentation
- API keys are never committed (see .gitignore)
- Generated documentation is gitignored (in `hda_docs/`)
- The `blog/` directory contains learning tutorials (not part of the main workflow)
