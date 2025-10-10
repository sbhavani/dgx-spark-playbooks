# CUDA-X

> Accelerated data science with NVIDIA RAPIDS

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)

---

## Overview

## Basic Idea
CUDA-X Data Science (formally RAPIDS) is an open-source library collection that accelerates the data science and data processing ecosystem. Accelerate popular python tools like scikit-learn and pandas with zero code changes on DGX Spark to maximize performance at your desk. This playbook orients you with example workflows, demonstrating the acceleration of key machine learning algorithms like UMAP and HBDSCAN and core pandas operations, without changing your code.

In this playbook, we will demonstrate the acceleration of key machine learning algorithms like UMAP and HBDSCAN and core pandas operations, without changing your code.

## What to know before starting
- Familiarity with pandas, scikit learn, machine learning algorithms, such as support vector machine, clustering, and dimensionality reduction algorithms

## Prerequisites
- Install conda
- Generate a Kaggle API key

**Duration:** 20-30 minutes setup time and 2-3 minutes to run each notebook.

## Instructions

## Step 1. Verify system requirements
- Verify the system has CUDA 13 installed
- Verify the python version is greater than 3.10
- Install conda using [these instructions](https://docs.anaconda.com/miniconda/install/)
- Create Kaggle API key using [these instructions](https://www.kaggle.com/discussions/general/74235) and place the **kaggle.json** file in the same folder as the notebook

## Step 2. Installing CUDA-X libraries
- use the following command to install the CUDA-X libraries (this will create a new conda environment)
  ```bash
    conda create -n rapids-test -c rapidsai-nightly -c conda-forge -c nvidia  \
    rapids=25.10 python=3.12 'cuda-version=13.0' \
    jupyterlab hdbscan umap-learn
  ```
## Step 3. Activate the conda environment
- activate the conda environment
  ```bash
    conda activate rapids-test
  ```
## Step 4. Cloning the notebooks
- clone the github repository and go the cuda-x-data-science/assets folder
  ```bash
    ssh://git@******:12051/spark-playbooks/dgx-spark-playbook-assets.git
  ```
- place the **kaggle.json** created in Step 1 in the assets folder

## Step 5. Run the notebooks
- Both the notebooks are self explanatory
- To experience the acceleration achieved using cudf.pandas, run the cudf_pandas_demo.ipynb notebook
  ```bash
    jupyter notebook cudf_pandas_demo.ipynb
  ```
- To experience the acceleration achieved using cuml, run the cuml_sklearn_demo.ipynb notebook
  ```bash
    jupyter notebook cuml_sklearn_demo.ipynb
  ```
