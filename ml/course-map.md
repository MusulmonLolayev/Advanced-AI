# Advanced AI - Machine Learning Course Plan

This is the working course plan for the authored material in `ml/`.
It reflects the current lecture and assignment sequence, not the older textbook-first outline.

## Course goal

By the end of this block, students should be able to:

- explain the geometry behind nearest-neighbor methods, PCA, clustering, and density-based outlier screening;
- implement the core computational steps of `k-NN`, `PCA`, `k-means`, and `DBSCAN` with NumPy;
- interpret when a method is based on distance, projection, density, or optimization;
- compare clustering methods with supervised tree-based methods at a practical level;
- know where classical linear models and neural-network training will be introduced later.

## Current lecture sequence

1. **Lecture 1 - Introduction to Machine Learning and k-NN**
   - classification, regression, retrieval, anomaly scoring
   - distance, scaling, and the nearest-neighbor rule
2. **Lecture 2 - PCA**
   - linear projection, variance maximization, reconstruction
   - dimensionality reduction and visualization
3. **Lecture 3 - k-Means Clustering**
   - clustering objective, alternating minimization, centroid updates
   - scaling, initialization, and failure modes
4. **Lecture 4 - DBSCAN**
   - epsilon neighborhoods, MinPts, core/border/noise points
   - density reachability, density connectivity, outlier screening
5. **Lecture 5 - Decision Trees**
   - impurity, splits, tree growth, interpretability
6. **Lecture 6 - Random Forests**
   - bagging, feature subsampling, variance reduction
7. **Lecture 7 - Boosting**
   - weak learners, additive modeling, sequential correction
8. **Lecture 8 - High-Dimensional Visualization**
   - `t-SNE` as a visualization tool
   - contrast with PCA and cluster inspection

## Planned extensions

The following topics can be added after the main block depending on pacing:

- hierarchical clustering
- Gaussian mixture models and EM
- anomaly detection beyond DBSCAN
- linear models and optimization, moved to the NN section

## Assignment sequence

1. **Lab 1 - k-NN**
2. **Lab 2 - PCA**
3. **Lab 3 - k-Means**
4. **Lab 4 - DBSCAN**

## Notes

- Keep the notation consistent across lectures and assignments.
- Prefer short derivations followed by numerical examples and graphics.
- Use the course split to introduce supervised tree methods before the NN block.
