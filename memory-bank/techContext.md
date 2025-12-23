# Technical Context: IPSep-CoLa

## Technology Stack

### Primary Languages

#### Python 3.10+

**Purpose**: Main development language for orchestration, data processing, and algorithm implementation

**Package Manager**: Rye (modern Python project management)

- Installation: <https://rye-up.com/guide/installation/>
- Setup: `rye sync`

**Key Libraries**:

- `networkx>=3.2.1`: Graph data structures and algorithms
- `numpy>=1.26.4`: Numerical computing, array operations
- `scipy>=1.16.0`: Scientific computing, optimization
- `matplotlib>=3.8.3`: Plotting and visualization
- `pyqt5>=5.15.11`: GUI support (if needed)
- `egraph>=0.3.1`: Custom Rust-based graph library (PyO3 bindings)

**Development Tools**:

- `ruff>=0.12.3`: Fast Python linter and formatter
- `snakeviz>=2.2.0`: Profiling visualization tool

#### Rust

**Purpose**: High-performance graph algorithms and layout computations

**Location**: `egraph-rs/` subdirectory

**Build System**: Cargo (Rust's package manager)

- Workspace with multiple crates
- PyO3 for Python bindings
- wasm-bindgen for WebAssembly bindings

**Key Crates**:

- `algorithm/`: Graph algorithms (shortest paths, connected components)
- `layout/`: Layout algorithms (SGD, MDS, stress majorization, Kamada-Kawai)
- `drawing/`: Drawing in various geometric spaces (Euclidean, spherical, hyperbolic, torus)
- `quality-metrics/`: Layout quality evaluation
- `python/`: PyO3 Python bindings
- `wasm/`: WebAssembly bindings

#### JavaScript/Node.js

**Purpose**: WebCoLa integration and visualization rendering

**Package Manager**: npm

**Key Files**:

- `js/src/render.js`: Canvas-based graph rendering to PNG
- WebCoLa library integration for constraint-based layouts

**Dependencies** (from `js/package.json`):

- Canvas libraries for rendering
- WebCoLa for layout computation

## Development Environment

### Setup Requirements

1. **Python Environment**

   ```bash
   # Install Rye
   curl -sSf https://rye-up.com/get | bash
   
   # Sync dependencies
   rye sync
   ```

2. **Rust Environment**

   ```bash
   # Install Rust (rustup)
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   
   # Build egraph-rs
   cd egraph-rs
   cargo build --release
   ```

3. **Node.js Environment**

   ```bash
   # Install Node.js (version specified in .nvmrc)
   cd egraph-rs
   nvm install
   nvm use
   
   # Install dependencies
   npm install
   
   # For js/ directory
   cd ../js
   npm install
   ```

### Python Version Management

**Specified Version**: Python 3.10+ (see `.python-version`)

**Rye Configuration**: `pyproject.toml`

```toml
[project]
requires-python = ">= 3.10"
```

### Project Structure Conventions

```
IPSep-CoLa/
├── pyproject.toml          # Python project configuration
├── .python-version         # Python version specification
├── requirements*.lock      # Locked dependencies
├── src/                    # Python source code
├── scripts/                # Processing scripts
├── egraph-rs/             # Rust library (separate workspace)
│   ├── Cargo.toml         # Rust workspace configuration
│   └── crates/            # Individual Rust crates
└── js/                    # JavaScript visualization
    └── package.json       # Node.js dependencies
```

## Technical Constraints

### Performance Constraints

1. **Graph Size Limits**
   - Maximum tested: 2000 nodes
   - Distance matrix: O(n²) memory for n nodes
   - Floyd-Warshall: O(n³) time complexity
   - Practical limit: ~5000 nodes before memory/time issues

2. **Iteration Limits**
   - SGD iterations: Typically 100-500
   - Convergence criteria: Stress change threshold or max iterations
   - Constraint projection: Per-iteration overhead

3. **Parallelization**
   - GNU Parallel used for experiment-level parallelization
   - Individual layout computations are sequential
   - Rust library supports internal parallelization (where applicable)

### Memory Constraints

1. **Distance Matrix Storage**
   - Full matrix: n×n floating-point values
   - For n=2000: ~32MB per graph (double precision)
   - Sparse alternatives available for large graphs

2. **Multiple Trial Storage**
   - 20 samples × 10 trials = 200 layouts per node size
   - JSON storage: ~1-10MB per layout (depending on size)

### Cross-Platform Considerations

**Primary Development Environment**: Linux (Ubuntu/Debian-based)

- Shell scripts use bash
- File paths use Unix conventions
- GNU Parallel required

**Potential Portability Issues**:

- Shell scripts may need adaptation for Windows
- File path separators
- Parallel execution tools

## Dependencies Deep Dive

### Python Dependencies (from pyproject.toml)

```toml
dependencies = [
    "numpy>=1.26.4",        # Array operations, linear algebra
    "networkx>=3.2.1",      # Graph data structures
    "scipy>=1.16.0",        # Optimization, sparse matrices
    "matplotlib>=3.8.3",    # Plotting, visualization
    "pyqt5>=5.15.11",       # GUI support
    "maturin>=1.7.0",       # Rust-Python bridge builder
    "pip>=24.2",            # Package installer
    "ruff>=0.12.3",         # Linter/formatter
    "egraph>=0.3.1",        # Custom Rust library
]

dev-dependencies = [
    "snakeviz>=2.2.0"       # Profiling visualization
]
```

### Critical Dependency Relationships

```
networkx → Graph representation
    ↓
numpy → Numerical operations on graphs
    ↓
scipy → Optimization algorithms
    ↓
matplotlib → Result visualization

egraph (Rust) → High-performance layout
    ↑
maturin → Builds Rust-Python bindings
```

### Rust Dependencies (key crates)

From `egraph-rs/Cargo.toml`:

- Graph data structures
- Numerical linear algebra
- Random number generation (for reproducibility)
- PyO3 (Python bindings)
- wasm-bindgen (WebAssembly bindings)

## Tool Usage Patterns

### Graph Generation

**Tool**: Python scripts in `src/data/generator/`, `src/script/generator/`

**Pattern**:

```bash
python src/script/generator/networkx_watts_strogatz.py \
    --nodes 1000 \
    --neighbor 2 \
    --rewiring 0.3 \
    --output data/graph/example.json
```

**Output Format**: NetworkX graph serialized to JSON

### Constraint Application

**Tools**: Python scripts in `src/data/`

**Pattern**:

```bash
# Add layer constraints
python src/data/add_layer_constraint.py \
    data/graph/input.json

# Add rectangle shapes
python src/data/add_rect_overlap_shape.py \
    data/graph/input.json \
    --width 100 \
    --height 100

# Convert to fixed layers
python src/data/gap_layer_to_fixed_layer.py \
    data/graph/constrained.json
```

**Side Effect**: Modifies JSON files in-place or creates new versions

### Layout Computation

**Tools**: Scripts in `scripts/`

**Patterns**:

```bash
# FullSGD
python scripts/draw.py \
    --dest data/drawing/sgd/ \
    [--overlap-removal] \
    [--space euclidean|torus|hyperbolic] \
    data/graph/*.json

# WebCoLa
python scripts/draw_webcola.py \
    --dest data/drawing/webcola/ \
    [--overlap-removal] \
    data/graph/*.json

# UNICON
python scripts/draw_unicon.py \
    --dest data/drawing/unicon/ \
    data/graph/*.json
```

**Options**:

- `--overlap-removal`: Enable overlap removal constraints
- `--space`: Geometric space for drawing (FullSGD only)
- `--dest`: Output directory for layout positions

### Parallel Execution

**Tool**: GNU Parallel

**Pattern**:

```bash
# Parallel layout computation
parallel --bar \
    'python scripts/draw.py \
        --dest=data/drawing/sgd/{1} \
        data/graph/{1}/*.json' \
    ::: $(seq -f '%04.0f' 100 100 2000)

# Multi-parameter parallelization
parallel --bar \
    'python scripts/draw.py \
        --dest=data/drawing/{1}/{2} \
        data/graph/{2}/*.json' \
    ::: sgd webcola unicon \
    ::: overlap cluster layered
```

**Benefits**:

- Automatic job scheduling
- Progress bars (`--bar`)
- Error handling
- Parallel file processing

### Metrics Calculation

**Tools**: Evaluation scripts

**Pattern**:

```bash
# Calculate stress
python scripts/calc_stress.py \
    data/graph/metadata.csv \
    result/stress/output.csv

# Calculate violations
python scripts/calc_violation.py \
    data/graph/metadata.csv \
    result/violation/output.csv
```

**Input**: Metadata CSV linking graphs to layouts
**Output**: Metrics CSV with columns: n, method, run, value

### Visualization

**Tool**: Box plot generator

**Pattern**:

```bash
python scripts/create_boxplot.py \
    result/stress/data.csv \
    result/stress/plot.png \
    [--title "Stress Comparison"]
```

**Output**: PNG box plot comparing methods across node sizes

### Rendering to PNG

**Tool**: Node.js rendering script

**Pattern**:

```bash
node js/src/render.js \
    --graphFile=data/graph/input.json \
    --drawingFile=data/drawing/layout.json \
    --output=result/plot/output.png
```

**Requirements**: Node.js with canvas support

## Build and Deployment

### Building egraph-rs

```bash
cd egraph-rs

# Build all crates
cargo build --release

# Build Python bindings
cd crates/python
maturin develop --release

# Build WebAssembly
cd ../wasm
wasm-pack build
```

### Python Package Installation

```bash
# Development mode (editable)
rye sync

# Or using pip
pip install -e .
```

### Running Tests

```bash
# Python tests
python -m pytest tests/

# Rust tests
cd egraph-rs
cargo test
```

## Configuration Files

### Python Configuration

**pyproject.toml**: Project metadata and dependencies

```toml
[tool.rye]
managed = true
dev-dependencies = ["snakeviz>=2.2.0"]

[tool.hatch.metadata]
allow-direct-references = true
```

**requirements*.lock**: Locked dependency versions for reproducibility

### Rust Configuration

**Cargo.toml** (workspace level): Workspace members and shared settings

**Individual crate Cargo.toml**: Per-crate dependencies and configuration

### JavaScript Configuration

**package.json**: Node.js dependencies and scripts

**.nvmrc**: Node.js version specification

**.prettierrc.json**: Code formatting rules

### Git Configuration

**.gitignore**: Excludes build artifacts, data files, results

- Python: `__pycache__/`, `*.pyc`, `.ruff_cache/`
- Rust: `target/`, `Cargo.lock` (for libraries)
- Node: `node_modules/`
- Data: `data/`, `result/` (typically)

## Development Workflow

### Typical Development Cycle

1. **Setup**

   ```bash
   rye sync
   cd egraph-rs && cargo build --release
   cd ../js && npm install
   ```

2. **Graph Generation**

   ```bash
   python src/script/generator/networkx_watts_strogatz.py
   ```

3. **Add Constraints**

   ```bash
   python src/data/add_layer_constraint.py data/graph/*.json
   ```

4. **Compute Layouts**

   ```bash
   parallel --bar 'python scripts/draw.py {}' ::: data/graph/*.json
   ```

5. **Evaluate**

   ```bash
   python scripts/calc_stress.py ...
   python scripts/create_boxplot.py ...
   ```

### Debugging Techniques

1. **Python Profiling**

   ```bash
   python -m cProfile -o main.prof scripts/draw.py ...
   snakeviz main.prof
   ```

2. **Rust Debugging**

   ```bash
   RUST_BACKTRACE=1 cargo run
   ```

3. **Logging**
   - Python: Standard `logging` module
   - Rust: `log` and `env_logger` crates

## Performance Optimization Notes

### Python Optimizations

- Use NumPy vectorized operations
- Avoid Python loops for numerical computation
- Delegate heavy computation to Rust

### Rust Optimizations

- Release builds (`--release`) for 10-100x speedup
- Profile-guided optimization available
- SIMD operations where applicable

### Data Format Optimizations

- Binary formats considered for large datasets
- JSON chosen for human readability and debugging
- Compression for storage (if needed)

## Known Technical Limitations

1. **JSON Size**: Large graphs produce large JSON files
2. **Memory**: Full distance matrices limit scalability
3. **Subprocess Overhead**: Python-Node.js communication has overhead
4. **Reproducibility**: Random seeds not consistently controlled
5. **Platform**: Primary support for Linux, limited Windows testing

## Future Technical Considerations

1. **Sparse Distance Matrices**: For larger graphs
2. **Distributed Computing**: For massive parallelization
3. **Binary Formats**: For performance-critical paths
4. **WebAssembly**: Browser-based visualization
5. **GPU Acceleration**: For layout computation
