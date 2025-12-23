# System Patterns: IPSep-CoLa

## System Architecture

The IPSep-CoLa project follows a modular pipeline architecture with three main processing layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA GENERATION LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  Graph Generators → Constraint Appliers → Distance Matrices │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    LAYOUT COMPUTATION LAYER                  │
├─────────────────────────────────────────────────────────────┤
│  FullSGD (Python/Rust) │ WebCoLa (JS) │ UNICON (Python)   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    EVALUATION LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  Stress Calculator → Violation Calculator → Visualizer       │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Graph Generation Module (`src/data/generator/`, `src/script/generator/`)

**Purpose**: Generate test graphs with controlled properties

**Key Files**:

- `networkx_watts_strogatz.py`: Watts-Strogatz model implementation
- `networkx_scale_free.py`: Scale-free network generation
- `generate_overlap_graphs.py`: Graphs for overlap removal experiments

**Pattern**: Factory pattern for different graph types

**Data Flow**:

```python
Parameters (n, k, p) → Graph Generator → NetworkX Graph → JSON Format
```

**Key Decision**: Use NetworkX as the standard graph representation for interoperability

### 2. Constraint Application Module (`src/data/`)

**Purpose**: Apply various constraint types to graphs

**Key Files**:

- `add_layer_constraint.py`: Creates hierarchical layer constraints
- `add_rect_overlap_shape.py`: Adds rectangle shapes for overlap removal
- `gap_layer_to_fixed_layer.py`: Converts gap constraints to bidirectional fixed constraints

**Pattern**: Decorator pattern - constraints are added to existing graph objects

**Constraint Format**:

```python
# Gap constraint
{
    "type": "constraint",
    "axis": "y",
    "left": node_id,
    "right": node_id,
    "gap": 100
}

# Circle constraint
{
    "type": "circle",
    "nodes": [node_ids],
    "r": radius,
    "center": center_node_id
}

# Rectangle shape
{
    "id": node_id,
    "shape": {
        "type": "rect",
        "width": 100,
        "height": 100
    }
}
```

**Key Decision**: JSON-based constraint representation for cross-language compatibility

### 3. Layout Algorithm Implementations

#### 3.1 FullSGD (`src/sgd/`)

**Architecture**: Python orchestration + Rust performance library

**Key Files**:

- `full.py`: Main full-distance SGD implementation
- `sparse.py`: Sparse SGD using pivot nodes
- `projection/`: Constraint projection implementations
  - `circle_constraints.py`: Circular constraint projection
  - `align_constraints.py`: Alignment constraint projection
  - `distance_constraints.py`: Distance constraint projection

**Pattern**: Strategy pattern for different projection methods

**Critical Path**:

```python
Initialize positions → 
For each iteration:
    Calculate stress gradient →
    Apply gradient descent step →
    Project to satisfy constraints →
    Check convergence
```

**Integration with Rust**:

```python
from egraph import FullSgd  # PyO3 bindings

layout = FullSgd()
positions = layout.run(graph, distance_matrix, constraints)
```

#### 3.2 WebCoLa Integration (`scripts/draw_webcola.py`)

**Architecture**: Python wrapper around Node.js execution

**Pattern**: Adapter pattern - Python interfaces with JavaScript library

**Execution Flow**:

```python
Graph (JSON) → 
Node.js WebCoLa script → 
Layout positions (JSON) →
Python evaluation
```

**Key Decision**: Use subprocess to invoke Node.js for WebCoLa execution

#### 3.3 UNICON (`src/sgd/uniocon.py`)

**Architecture**: Python implementation of UNICON algorithm

**Pattern**: Template method pattern for stress majorization

### 4. Distance Matrix Computation

**Implementation**: Floyd-Warshall algorithm in NetworkX

**Key Pattern**: Compute once, use many times (caching)

```python
# Compute all-pairs shortest paths
distances = dict(nx.all_pairs_shortest_path_length(graph))

# Convert to distance matrix with edge length scaling
distance_matrix = [[distances[i][j] * edge_length 
                    for j in nodes] 
                   for i in nodes]
```

**Storage**: Stored as 2D arrays in graph JSON for reuse

### 5. Evaluation Module (`scripts/`)

**Key Files**:

- `calc_stress.py`: Stress metric computation (SNS)
- `calc_violation.py`: Constraint violation measurement
- `create_boxplot.py`: Statistical visualization
- `compare_stress_ratio.py`: Comparative stress analysis (NEW - December 2025)
- `ratio_boxplot.py`: Multi-metric visualization (NEW - December 2025)

**Pattern**: Pipeline pattern for metrics calculation

**Stress Calculation (Scale-normalized Stress - SNS)**:

```python
def scale_normalized_stress(positions, distance_matrix):
    actual_distances = compute_euclidean_distances(positions)
    numerator = sum((ideal - actual)^2 for all pairs)
    denominator = sum(ideal^2 for all pairs)
    return numerator / denominator
```

**Note**: Terminology updated from "Normalized Stress" to "Scale-normalized Stress (SNS)" in December 2025 to align with research literature.

**Comparative Analysis (NEW - December 2025)**:

```python
# scripts/compare_stress_ratio.py
def compare_methods(baseline_data, proposed_data):
    for baseline, proposed in zip(baseline_data, proposed_data):
        reduction_rate = (baseline - proposed) / baseline
        yield {
            'baseline_stress': baseline,
            'proposed_stress': proposed,
            'reduction_rate': reduction_rate
        }
```

**Multi-Metric Visualization (NEW - December 2025)**:

```python
# scripts/ratio_boxplot.py
def generate_three_plots(data):
    # 1. Reduction Rate (percentage)
    rates = [(b - p) / b for b, p in data]
    
    # 2. Reduction Amount (absolute)
    amounts = [b - p for b, p in data]
    
    # 3. Final Values (achieved stress)
    finals = [p for b, p in data]
    
    # Generate separate plots for each metric
    save_plot(rates, 'rate')
    save_plot(amounts, 'abs')
    save_plot(finals, 'final')
```

**Violation Calculation**:

```python
def calculate_violation(positions, constraints):
    violations = []
    for constraint in constraints:
        violation = max(0, compute_violation(constraint, positions))
        violations.append(violation)
    return mean(violations)
```

### 6. Visualization Module (`js/src/`)

**Purpose**: Render graph layouts to PNG

**Key Files**:

- `render.js`: Node.js script for canvas rendering
- Uses HTML5 Canvas API for drawing

**Pattern**: Renderer pattern with pluggable drawing backends

**Rendering Pipeline**:

```javascript
Load graph + layout → 
Create canvas →
Draw nodes (circles/rectangles) →
Draw edges →
Export to PNG
```

## Critical Implementation Paths

### Path 1: Experiment Execution Pipeline

```
Shell Script (shell_scripts/) →
├─ Graph Generation (src/script/generator/) →
├─ Constraint Application (src/data/) →
├─ Parallel Layout Computation (GNU Parallel) →
│  ├─ FullSGD (scripts/draw.py)
│  ├─ WebCoLa (scripts/draw_webcola.py)
│  └─ UNICON (scripts/draw_unicon.py)
├─ Metrics Calculation (scripts/calc_*.py) →
└─ Visualization (scripts/create_boxplot.py)
```

### Path 2: FullSGD Constraint Projection

```
SGD Iteration →
├─ Compute stress gradient
├─ Update positions
└─ Project to constraints:
    ├─ Parse constraint types
    ├─ Apply projection for each type:
    │  ├─ Circle: Project to circular boundary
    │  ├─ Align: Force collinear positions
    │  └─ Distance: Maintain distance bounds
    └─ Return feasible positions
```

### Path 3: WebCoLa Execution Bridge

```
Python Script →
├─ Convert graph to WebCoLa JSON format
├─ Write temporary files
├─ Spawn Node.js process:
│  ├─ Load WebCoLa library
│  ├─ Configure constraints
│  ├─ Run layout optimization
│  └─ Write results to JSON
├─ Read results back to Python
└─ Clean up temporary files
```

### Path 4: Comparative Analysis Pipeline (NEW - December 2025)

```
Individual Stress CSVs (per method) →
├─ Load baseline method data
├─ Load proposed method data
└─ scripts/compare_stress_ratio.py →
    ├─ Align data by graph size
    ├─ Calculate reduction metrics:
    │  ├─ Reduction Rate: (baseline - proposed) / baseline
    │  ├─ Reduction Amount: baseline - proposed
    │  └─ Final Value: proposed
    └─ Output comparison CSV →
        └─ scripts/ratio_boxplot.py →
            ├─ Generate Reduction Rate plot (_rate.png)
            ├─ Generate Reduction Amount plot (_abs.png)
            └─ Generate Final Value plot (_final.png)
```

**Usage Example**:

```bash
# Step 1: Compare two methods
python scripts/compare_stress_ratio.py \
    result/stress/all_methods.csv \
    result/ratio/webcola_vs_sgd.csv \
    --methods webcola sgd

# Step 2: Generate three visualizations
python scripts/ratio_boxplot.py \
    result/ratio/webcola_vs_sgd.csv \
    result/ratio/comparison.png \
    --xlabel "Number of Nodes" \
    --title "WebCoLa vs FullSGD Comparison"

# Output files:
# - comparison_rate.png (reduction rate %)
# - comparison_abs.png (absolute reduction)
# - comparison_final.png (final stress values)
```

## Key Technical Decisions

### 1. Multi-Language Architecture

**Decision**: Use Python (orchestration), Rust (performance), JavaScript (WebCoLa)

**Rationale**:

- Python: Excellent for scripting, data processing, scientific computing
- Rust: High performance for compute-intensive graph algorithms
- JavaScript: Required for WebCoLa library integration

**Trade-off**: Complexity of multi-language coordination vs. leveraging best tools

### 2. JSON as Data Exchange Format

**Decision**: Use JSON for all graph and constraint data

**Rationale**:

- Language-agnostic
- Human-readable
- Well-supported across Python, Rust, JavaScript

**Trade-off**: Some performance overhead vs. universal compatibility

### 3. NetworkX as Graph Foundation

**Decision**: Use NetworkX as the core graph data structure

**Rationale**:

- Rich graph algorithms library
- Easy manipulation and analysis
- Excellent documentation

**Trade-off**: Python performance vs. ease of use

### 4. Parallel Execution with GNU Parallel

**Decision**: Use GNU Parallel for experiment parallelization

**Rationale**:

- Simple parallelization without code changes
- Robust error handling
- Progress monitoring

**Example**:

```bash
parallel --bar 'python scripts/draw.py {1} {2}' \
    ::: graph_files \
    ::: algorithms
```

### 5. Separation of Concerns

**Decision**: Separate generation, layout, and evaluation into distinct stages

**Rationale**:

- Modularity and maintainability
- Easier to debug and modify
- Reusable components

**Structure**:

- Generators produce graphs
- Layout algorithms operate on graphs
- Evaluators consume layouts

## Component Relationships

### Dependency Graph

```
egraph-rs (Rust library)
    ↓ (PyO3 bindings)
src/sgd/ (Python SGD implementations)
    ↓
scripts/draw.py (Layout execution)
    ↓
scripts/calc_stress.py (Evaluation)
    ↓
scripts/create_boxplot.py (Visualization)
```

### Data Flow

```
Graph Generators
    ↓ (JSON files)
Constraint Appliers
    ↓ (Modified JSON)
Layout Algorithms
    ↓ (Position JSON)
Metric Calculators
    ↓ (CSV results)
Box Plot Generator
    ↓ (PNG images)
```

## Design Patterns in Use

1. **Factory Pattern**: Graph generators create different graph types
2. **Decorator Pattern**: Constraints are added to graphs
3. **Strategy Pattern**: Different layout algorithms implement common interface
4. **Adapter Pattern**: WebCoLa JavaScript integration
5. **Template Method**: Base algorithm with customizable projection steps
6. **Pipeline Pattern**: Sequential data processing stages
7. **Builder Pattern**: Gradual construction of complex constraint sets

## Integration Points

### Python ↔ Rust

- **Mechanism**: PyO3 bindings in `egraph-rs/crates/python/`
- **Data Transfer**: NumPy arrays for positions, Python lists for graphs
- **Error Handling**: Rust errors converted to Python exceptions

### Python ↔ Node.js

- **Mechanism**: Subprocess execution with JSON file exchange
- **Data Transfer**: Temporary JSON files
- **Error Handling**: Process return codes and stderr capture

### File System Integration

- **Input**: `data/graph/` directory
- **Output**: `data/drawing/` for layouts, `result/` for metrics
- **Pattern**: Organized by experiment type and method

## Performance Characteristics

### Bottlenecks

1. **Distance Matrix Computation**: O(n³) Floyd-Warshall
2. **Layout Iteration**: Multiple gradient computations per iteration
3. **Constraint Projection**: Per-constraint operations each iteration

### Optimizations

1. **Rust Implementation**: Critical loops in Rust for 10-100x speedup
2. **Parallel Execution**: GNU Parallel for embarrassingly parallel tasks
3. **Sparse Methods**: Pivot-based approximations for large graphs
4. **Caching**: Distance matrices computed once and reused

## Error Handling Strategy

1. **Graph Generation**: Retry logic for ensuring connectivity
2. **Layout Computation**: Graceful degradation with default parameters
3. **File I/O**: Robust path handling and existence checks
4. **Cross-Process**: Capture and propagate errors from subprocesses
5. **Validation**: Input validation at each pipeline stage
