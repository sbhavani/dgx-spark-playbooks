# CUDA-X Data Science Playbook
# Base image with RAPIDS, cuDF, cuML already included
FROM nvcr.io/nvidia/pyg:25.09-py3

# Set environment variables
ENV JUPYTER_PORT=8888

# Set working directory
WORKDIR /workspace

# Copy the playbook files
COPY assets/ /workspace/assets/
COPY README.md /workspace/

# Install any additional dependencies needed
RUN pip uninstall -y umap && \
    pip install --no-cache-dir jupyter notebook umap-learn hdbscan

# Create a startup script
RUN echo '#!/bin/bash' > /start-jupyter.sh && \
    echo 'cd /workspace/assets' >> /start-jupyter.sh && \
    echo 'jupyter notebook --ip=0.0.0.0 --port=${JUPYTER_PORT} --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password=""' >> /start-jupyter.sh && \
    chmod +x /start-jupyter.sh

# Expose Jupyter port
EXPOSE ${JUPYTER_PORT}

# Set the default command
CMD ["/start-jupyter.sh"]
