# Product Context: IPSep-CoLa

## Why This Project Exists

Graph visualization is a fundamental problem in computer science, data analysis, and network science. While unconstrained graph layout algorithms are well-studied, real-world applications often require layouts that satisfy additional constraints such as:

- Maintaining hierarchical relationships
- Preventing node overlaps
- Preserving spatial relationships
- Aligning nodes according to specific rules

This project exists to **systematically evaluate and compare** constrained graph layout algorithms under controlled experimental conditions.

## Problems It Solves

### 1. Lack of Comprehensive Evaluation

**Problem**: Limited comparative studies exist for constrained graph layout algorithms under diverse constraint scenarios.

**Solution**: Provides a rigorous experimental framework comparing three algorithms (FullSGD, WebCoLa, UNICON) across three constraint types with standardized metrics.

### 2. Algorithm Performance Under Constraints

**Problem**: It's unclear how different algorithms balance stress minimization (layout quality) with constraint satisfaction.

**Solution**: Measures both Scale Normalized Stress (SNS) and constraint violation amounts, revealing the trade-offs each algorithm makes.

### 3. Scalability Assessment

**Problem**: Performance characteristics at different graph sizes are often unreported.

**Solution**: Tests graphs from 100 to 2000 nodes (20 size levels × 20 samples × 10 trials) to understand how algorithms scale.

### 4. Reproducible Research

**Problem**: Graph layout research often lacks reproducible experimental setups.

**Solution**: Provides automated workflows, documented parameters, and standardized evaluation metrics.

## How It Should Work

### User Workflows

#### Experiment Workflow

1. **Graph Generation**: Generate Watts-Strogatz graphs with specified parameters
2. **Constraint Application**: Apply one of three constraint types to the graphs
3. **Layout Computation**: Run all three algorithms on the constrained graphs
4. **Evaluation**: Calculate stress and violation metrics
5. **Visualization**: Generate box plots for comparative analysis

#### Typical Command Flow

```bash
# Generate graphs
python src/script/generator/networkx_watts_strogatz.py

# Apply constraints (varies by experiment type)
python src/data/add_layer_constraint.py  # For layered constraints
python src/data/add_rect_overlap_shape.py  # For overlap removal

# Run layouts
python scripts/draw.py                     # FullSGD
python scripts/draw_webcola.py             # WebCoLa
python scripts/draw_unicon.py              # UNICON

# Calculate metrics
python scripts/calc_stress.py              # Stress calculation
python scripts/calc_violation.py           # Violation calculation

# Visualize results
python scripts/create_boxplot.py           # Generate box plots
```

### Three Experiment Types

#### Experiment 1: Gap Constraints

**Purpose**: Evaluate basic constraint handling with random directional gaps

**Process**:

- Generate Watts-Strogatz graphs
- Randomly orient edges
- Add y-axis gap constraints (gap = 100) to each directed edge
- Measure: How well algorithms maintain directional spacing

**Expected Behavior**: Algorithms should create layouts with consistent vertical spacing between connected nodes while minimizing stress.

#### Experiment 2: Fixed Layer Constraints

**Purpose**: Test strict hierarchical layout preservation

**Process**:

- Generate Watts-Strogatz graphs
- Create DAG through cycle removal
- Assign layer numbers via longest path algorithm
- Add bidirectional gap constraints (equality constraints)
- Measure: How well algorithms preserve exact layer positions

**Expected Behavior**: Nodes in the same layer should align perfectly, with proportional spacing between layers.

#### Experiment 3: Rectangle Overlap Removal

**Purpose**: Assess large-scale geometric constraint handling

**Process**:

- Generate Watts-Strogatz graphs
- Assign 100×100 rectangle shapes to all nodes
- Apply non-overlap constraints to all node pairs
- Measure: How well algorithms prevent overlaps while preserving structure

**Expected Behavior**: No rectangles should overlap, with minimal distortion to the underlying graph structure.

## User Experience Goals

### For Researchers

- **Easy Replication**: Clear documentation and automated scripts for reproducing experiments
- **Flexible Parameters**: Ability to modify graph sizes, constraint types, and algorithm parameters
- **Comprehensive Results**: Both quantitative metrics (CSV) and visual analysis (box plots)

### For Algorithm Developers

- **Fair Comparison**: Identical graphs and constraints for all algorithms
- **Clear Metrics**: Well-defined stress and violation measurements
- **Performance Insights**: Understanding of scalability and trade-offs

### For Graph Visualization Practitioners

- **Real-World Constraints**: Tests reflect common layout requirements (hierarchies, overlaps)
- **Practical Insights**: Which algorithm works best for which constraint type
- **Visual Validation**: PNG outputs for qualitative assessment

## Expected Outcomes

### Quantitative Results

- **Stress Values**: Lower is better (better preserves graph distances)
- **Violation Values**: Lower is better (better satisfies constraints)
- **Scalability**: Performance trends across node counts

### Qualitative Insights

- Trade-off patterns between stress and constraint satisfaction
- Algorithm strengths and weaknesses per constraint type
- Visual quality assessment from rendered layouts

### Research Contributions

- Systematic comparison of three algorithms across multiple scenarios
- Identification of optimal algorithm-constraint pairings
- Scalability analysis for constrained graph layout
- Open-source experimental framework for future research

## Key Performance Indicators

1. **Completeness**: All 20 graphs × 20 node sizes × 3 algorithms × 10 trials = 12,000 layouts generated
2. **Accuracy**: Stress calculations match theoretical expectations
3. **Constraint Satisfaction**: Measurable violation reduction
4. **Reproducibility**: Consistent results across multiple runs
5. **Visualization Quality**: Clear, interpretable box plots showing statistical distributions

## Success Metrics

- ✓ All experiments complete without errors
- ✓ Results show clear algorithmic differences
- ✓ Visualizations clearly communicate findings
- ✓ Documentation enables independent replication
- ✓ Code is maintainable and extensible
