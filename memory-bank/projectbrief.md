# Project Brief: IPSep-CoLa

## Project Overview

IPSep-CoLa is a research project focused on evaluating constrained graph layout algorithms. The project implements and compares three different layout methods (FullSGD, WebCoLa, and UNICON) under various constraint conditions to assess their performance in terms of stress minimization and constraint satisfaction.

## Core Objectives

1. **Algorithm Evaluation**: Compare the performance of FullSGD (proposed method), WebCoLa, and UNICON under different constraint scenarios
2. **Constraint Types Research**: Investigate three types of constraints:
   - Gap constraints (random directional y-axis gap constraints)
   - Fixed layer constraints (DAG-based hierarchical bidirectional constraints)
   - Rectangle overlap removal (node overlap elimination constraints)
3. **Quality Metrics**: Measure and analyze Scale Normalized Stress (SNS) and constraint violation amounts

## Technical Scope

### Graph Generation

- Uses Newman-Watts-Strogatz graph model
- Node counts: 100 to 2000 (in increments of 100)
- Parameters: k=2 (neighborhood count), p=0.3 (rewiring probability)
- 20 independent samples per node count

### Layout Algorithms

- **FullSGD**: Stochastic Gradient Descent-based constrained layout (Python/Rust)
- **WebCoLa**: Constraint-based layout library (JavaScript)
- **UNICON**: Constrained network layout method

### Technology Stack

- **Primary Language**: Python 3.10+ (managed by Rye)
- **Graph Library**: NetworkX, NumPy, SciPy
- **Visualization**: Matplotlib, custom JavaScript rendering
- **Performance Library**: egraph-rs (Rust-based graph algorithms)
- **Automation**: Shell scripts, GNU Parallel

## Project Structure

```
IPSep-CoLa/
├── src/                    # Python source code
│   ├── sgd/               # SGD layout implementation
│   ├── ipsep_cola/        # Core algorithm implementation
│   ├── data/              # Data processing and generation
│   └── util/              # Utility functions
├── egraph-rs/             # Rust graph algorithm library
├── js/                    # JavaScript visualization
├── scripts/               # Python processing scripts
├── shell_scripts/         # Experiment automation
├── data/                  # Generated graphs and datasets
└── result/                # Experiment results
```

## Key Deliverables

1. Graph generation pipeline for Watts-Strogatz graphs
2. Three types of constraint application systems
3. Layout computation for three different algorithms
4. Performance evaluation metrics (SNS, violation)
5. Statistical visualization (box plots)
6. Comparative analysis results

## Success Criteria

- Successfully generate graphs across all node sizes (100-2000)
- Apply constraints correctly for all three experiment types
- Complete layout computations for all methods with 10 trials per graph
- Calculate accurate stress and violation metrics
- Produce clear comparative visualizations

## Research Questions

1. How do different constraint types affect layout quality?
2. What is the trade-off between stress minimization and constraint satisfaction?
3. Which algorithm performs best under different constraint scenarios?
4. How does algorithm performance scale with graph size?

## Current Status

The project infrastructure is established with:

- Complete graph generation workflows
- Implemented layout algorithms
- Evaluation scripts and automation tools
- Experiment configurations documented
