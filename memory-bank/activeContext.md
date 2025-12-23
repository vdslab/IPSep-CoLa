# Active Context: IPSep-CoLa

## Current Work Focus

**Status**: Analysis and Comparison Phase - Stress Reduction Evaluation

The project is in the analysis phase, focusing on comparing layout algorithms and evaluating stress reduction performance between different methods (primarily WebCoLa vs FullSGD/proposed method).

**Current Activities**:

- Stress reduction rate analysis
- Multi-metric comparative visualization (reduction rate, absolute reduction, final stress values)
- Scale-normalized Stress (SNS) metric implementation

## Recent Changes

### December 23, 2025: Shell Script Refactoring and Reorganization

**Major Updates**:

1. **EVALUATION Results Directory Structure** (December 23, 2025)
   - Changed result storage from file-based to directory-based organization
   - Structure: `result/stress/$EVALUATION/`, `result/violation/$EVALUATION/`, `result/ratio/$EVALUATION/`
   - Allows easy separation of different evaluation metrics (SNS, Stress, etc.)
   - File names simplified by removing EVALUATION suffix (handled by directory)

2. **Shell Script Library Refactoring** (December 23, 2025)
   - Created modular library structure in `shell_scripts/lib/`:
     - `config.sh` - Configuration and constants management
     - `utils.sh` - Utility functions (logging, directory creation, etc.)
     - `drawing.sh` - Graph drawing and plotting (responsibility separation)
     - `calculation.sh` - Stress and violation calculations
     - `visualization.sh` - Box plot generation (DRY principle)
   - Main script reduced from ~230 lines to ~100 lines
   - Implemented DRY principle: eliminated duplicate Box plot code
   - Centralized `result_prefix` generation in config.sh
   - Each library file is independently reusable
   - Comprehensive documentation added to all functions

3. **Enhanced run_experiment.sh Interface**
   - Added optional 6th parameter for EVALUATION metric (default: "SNS")
   - Usage: `./run_experiment.sh TYPE START END STEP VIOLATION_TYPE [EVALUATION]`
   - Improved help message with clear examples
   - Better error handling and validation

4. **Updated runall.sh**
   - Adapted to new run_experiment.sh interface
   - Explicitly specifies EVALUATION parameter
   - Enabled all three experiment types (gap, layered, overlap)
   - Added descriptive comments and progress messages

### December 2025: Stress Comparison and Reduction Analysis (Earlier)

**Major Updates**:

1. **Scale-Normalized Stress Implementation** (Commit: d3fe05c)
   - Changed from "Normalized Stress" to "Scale-normalized Stress" based on paper requirements
   - Extracted normalized stress function into separate module for reuse
   - Updated all stress calculation scripts to use SNS

2. **Stress Reduction Rate Calculation** (Commits: 26f90be, 710d2e5, aa4c740)
   - Added `scripts/compare_stress_ratio.py`: Compares two methods and calculates reduction rates
   - Computes: `reduction_rate = (baseline_stress - proposed_stress) / baseline_stress`
   - Outputs: graph_size_n, baseline_name, baseline_stress, proposed_name, proposed_stress, reduction_rate
   - Enables quantitative comparison of algorithm improvements

3. **Multi-Metric Visualization** (Current)
   - Added `scripts/ratio_boxplot.py`: Generates three separate plots
     - **Reduction Rate**: Percentage improvement over baseline
     - **Reduction Amount**: Absolute stress reduction (baseline - proposed)
     - **Final Value**: Final stress values of proposed method
   - Uses Seaborn-based box plots for statistical visualization
   - Automatically saves three output files with suffixes: `_rate`, `_abs`, `_final`

4. **Constraint Projection Order Experiments** (Commit: b1fae69)
   - Added experiments to test different projection orders
   - Investigating impact of constraint application sequence on layout quality

5. **Computation-Rendering Separation** (Commit: a52aa62)
   - Separated layout computation from visualization rendering
   - Improves modularity and allows independent optimization

6. **Post-processing vs During-Layout Processing** (Commit: edfa479)
   - Added flexibility for constraint handling timing
   - Can now apply constraints during layout or as post-processing

### Memory Bank Update (December 23, 2025)

Comprehensive Memory Bank review and update to reflect current project state.

## Next Steps

### Immediate Focus

1. **Complete Current Analysis**
   - Run stress reduction analysis across all experiment types
   - Generate comparative visualizations for all three metrics (rate, amount, final)
   - Document findings and insights

2. **Results Interpretation**
   - Analyze reduction rate patterns across graph sizes
   - Identify algorithm strengths/weaknesses
   - Correlate with constraint types

3. **Publication Preparation**
   - Finalize figures for conference paper
   - Ensure all metrics use Scale-normalized Stress (SNS)
   - Verify reproducibility of results

### Potential Next Tasks

1. **Further Experiments**
   - Projection order optimization
   - Parameter sensitivity analysis
   - Constraint combination effects

2. **Code Refinement**
   - Performance optimization for large graphs
   - Additional constraint types (if needed)
   - Enhanced error handling

3. **Documentation**
   - Document stress reduction methodology
   - Create analysis workflow guide
   - Update experiment results documentation

## Active Decisions and Considerations

None at this time. Waiting for first task assignment.

## Important Patterns and Preferences

Based on project structure, documentation, and recent work:

### Code Organization

- Maintain separation between graph generation, layout computation, and evaluation
- Use JSON for cross-language data exchange
- Keep scripts modular and reusable

### Experiment Workflow

- Always use parallel execution (GNU Parallel) for batch processing
- Document experiment parameters clearly
- Store results in organized directory structure: `result/{metric}/{experiment}/`

### Development Practices

- Use Rye for Python dependency management
- Build Rust code in release mode for performance
- Follow existing naming conventions for new files
- Run linter (ruff) before committing

### File Naming Conventions

- Graph files: `node_n={size}_{sample_id}.json`
- Drawing files: Mirror graph file structure in `data/drawing/{method}/`
- Result files: `{experiment_type}-{size_range}.csv`
- Comparison files: `{baseline}_vs_{proposed}_ratio.csv`
- Visualization outputs: Base name with metric suffixes (`_rate.png`, `_abs.png`, `_final.png`)

### Performance Considerations

- For graphs > 1000 nodes, consider sparse methods
- Monitor memory usage during distance matrix computation
- Use Rust implementations for compute-intensive operations
- Leverage parallelization at experiment level

## Learnings and Project Insights

### From Recent Work

1. **Stress Metrics Evolution**
   - Discovered that "Normalized Stress" terminology was not aligned with paper
   - Switched to "Scale-normalized Stress (SNS)" for consistency with research literature
   - SNS formula: `sum((ideal - actual)^2) / sum(ideal^2)`
   - Critical for fair comparison across different graph sizes

2. **Multi-Metric Evaluation Importance**
   - Single metrics can be misleading
   - Three complementary views provide fuller picture:
     - **Reduction Rate**: Relative improvement (percentage)
     - **Reduction Amount**: Absolute improvement (raw values)
     - **Final Value**: Actual achieved stress (end result)
   - Different metrics reveal different aspects of algorithm performance

3. **Projection Order Matters**
   - Constraint projection order can affect final layout quality
   - Investigating optimal ordering strategies
   - Trade-offs between different constraint priorities

4. **Separation of Concerns Benefits**
   - Separating computation from visualization improves workflow
   - Allows independent optimization of each stage
   - Facilitates debugging and partial re-runs

### From Documentation Review

1. **Three-Tier Experiment Design**
   - Gap constraints test basic directional spacing
   - Layered constraints test strict hierarchical preservation
   - Overlap removal tests geometric constraint handling
   - Each provides different algorithmic challenges

2. **Multi-Language Architecture**
   - Python for orchestration and data processing
   - Rust for performance-critical computations
   - JavaScript for WebCoLa integration and visualization
   - Clean interfaces between languages via JSON

3. **Scalability Boundaries**
   - Tested up to 2000 nodes
   - Practical limits around 5000 nodes due to O(n³) algorithms
   - Sparse methods available for larger graphs

4. **Evaluation Methodology**
   - Scale Normalized Stress (SNS) for layout quality
   - Constraint violation for constraint satisfaction
   - Statistical analysis with 20 samples × 10 trials
   - Box plots for comparative visualization

5. **Automation Strategy**
   - Shell scripts for end-to-end workflows
   - GNU Parallel for embarrassingly parallel tasks
   - Modular scripts for flexibility
   - Clear separation of concerns

## Current Environment State

- **Working Directory**: `/home/iharuki/school/itohal/IPSep-CoLa`
- **Git Repository**: origin at <git@github.com>:vdslab/IPSep-CoLa.git
- **Latest Commit**: b1fae6967149b89a2d071e606810d874432e5de4
- **Python Version**: 3.10+ (managed by Rye)
- **Development Tools**: ruff, snakeviz available

## Notes for Future Work

### When Starting New Experiments

1. Check existing data to avoid duplication
2. Ensure all dependencies are installed and up-to-date
3. Review experiment settings in `docs/experiment_settings.md`
4. Use appropriate shell scripts from `shell_scripts/` directory
5. Monitor disk space for large result sets

### When Modifying Code

1. Review relevant files in `systemPatterns.md` first
2. Understand the data flow through the pipeline
3. Test changes on small graphs before large-scale runs
4. Update documentation if behavior changes
5. Consider cross-language implications

### When Analyzing Results

1. Verify all trials completed successfully
2. Check for outliers or anomalies
3. Compare with expected theoretical behavior
4. Document findings for future reference
5. Consider statistical significance

## Open Questions

None currently - awaiting task assignment to identify relevant questions.

## Context for AI Assistant (Cline)

When resuming work after a session reset:

1. **Always read ALL Memory Bank files** before starting work
2. **Key files to understand**:
   - `projectbrief.md`: What this project is about
   - `systemPatterns.md`: How the system is structured
   - `activeContext.md`: What's currently happening (this file)
   - `progress.md`: What's been accomplished

3. **Critical paths to understand**:
   - Graph generation → Constraint application → Layout → Evaluation
   - Python-Rust integration via PyO3
   - Python-Node.js integration via subprocess

4. **Common workflows**:
   - Use shell scripts in `shell_scripts/` for standard experiments
   - Use `scripts/` for individual processing steps
   - Results go to `result/` directory

5. **When in doubt**:
   - Check `docs/experiment_settings.md` for detailed procedures
   - Review existing shell scripts for examples
   - Look at `systemPatterns.md` for architectural guidance
