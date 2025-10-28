# Basic idea
This playbook includes two example notebooks that demonstrate the acceleration of key machine learning algorithms and core pandas operations using CUDA-X Data Science libraries:

- **NVIDIA cuDF:** Accelerates operations for data preparation and core data processing of 8GB of strings data, with no code changes.
- **NVIDIA cuML:** Accelerates popular, compute intensive machine learning algorithms in sci-kit learn (LinearSVC), UMAP, and HDBSCAN, with no code changes.

CUDA-X Data Science (formally RAPIDS) is an open-source library collection that accelerates the data science and data processing ecosystem. These libraries accelerate popular Python tools like scikit-learn and pandas with zero code changes. On DGX Spark, these libraries maximize performance at your desk with your existing code.

# What you'll accomplish
You will accelerate popular machine learning algorithms and data analytics operations GPU. You will understand how to accelerate popular Python tools, and the value of running data science workflows on your DGX Spark. 

# Prerequisites
- Familiarity with pandas, scikit-learn, machine learning algorithms, such as support vector machine, clustering, and dimensionality reduction algorithms.
- Install conda
- Generate a Kaggle API key

# Time & risk
* **Duration:** 20-30 minutes setup time and 2-3 minutes to run each notebook. 
* **Risks:** 
* Data download slowness or failure due to network issues
* Kaggle API generation failure requiring retries
* **Rollback:** No permanent system changes made during normal usage.
