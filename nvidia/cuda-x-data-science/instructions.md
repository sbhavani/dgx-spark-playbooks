# Step 1. Verify system requirements
- Verify the system has CUDA 13 installed using `nvcc --version` or `nvidia-smi` 
- Install conda using [these instructions](https://docs.anaconda.com/miniconda/install/)
- Create Kaggle API key using [these instructions](https://www.kaggle.com/discussions/general/74235) and place the **kaggle.json** file in the same folder as the notebook

# Step 2. Installing Data Science libraries
Use the following command to install the CUDA-X libraries (this will create a new conda environment)
  ```bash
    conda create -n rapids-test -c rapidsai-nightly -c conda-forge -c nvidia  \
    rapids=25.10 python=3.12 'cuda-version=13.0' \
    jupyter hdbscan umap-learn
  ```
# Step 3. Activate the conda environment
  ```bash
    conda activate rapids-test
  ```
# Step 4. Cloning the playbook repository
- Clone the github repository and go the assets folder place in **cuda-x-data-science** folder
  ```bash
    git clone ${GITLAB_REPO_BASEURL}
  ```
- Place the **kaggle.json** created in Step 1 in the assets folder

# Step 5. Run the notebooks
There are two notebooks in the GitHub repository. 
One runs an example of a large strings data processing workflow with pandas code on GPU.
- Run the **cudf_pandas_demo.ipynb** notebook and use `localhost:8888` in your browser to access the notebook
  ```bash
    jupyter notebook cudf_pandas_demo.ipynb
  ```
The other goes over an example of machine learning algorithms including UMAP and HDBSCAN.
- Run the **cuml_sklearn_demo.ipynb** notebook and use `localhost:8888` in your browser to access the notebook
  ```bash
    jupyter notebook cuml_sklearn_demo.ipynb
  ```
If you are remotely accessing your DGX-Spark then make sure to forward the necesary port to access the notebook in your local browser. Use the below   instruction for port fowarding
```bash
  ssh -N -L YYYY:localhost:XXXX username@remote_host 
```
- `YYYY`: The local port you want to use (e.g. 8888)
- `XXXX`: The port you specified when starting Jupyter Notebook on the remote machine (e.g. 8888)
- `-N`: Prevents SSH from executing a remote command
- `-L`: Spcifies local port forwarding
