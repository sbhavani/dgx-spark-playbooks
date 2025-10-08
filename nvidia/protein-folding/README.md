# Use Open Fold

> Use OpenFold with TensorRT optimization

## Table of Contents

- [Overview](#overview)
- [Access through terminal](#access-through-terminal)
  - [Step 7. Option B - Run locally with demo script](#step-7-option-b-run-locally-with-demo-script)
  - [Using a custom FASTA file](#using-a-custom-fasta-file)

---

## Overview

## What you'll accomplish

You'll set up a GPU-accelerated protein folding workflow on NVIDIA Spark devices using OpenFold
with TensorRT optimization and MMseqs2-GPU. After completing this walkthrough, you'll be able to
fold proteins in under 60 seconds using either NVIDIA's cloud UI or running locally on your
RTX Pro 6000 or DGX Spark workstation.

## What to know before starting

- Installing Python packages via pip
- Using Docker and the NVIDIA Container Toolkit for GPU workflows
- Running basic Linux commands and setting environment variables
- Understanding FASTA files and basics of protein structure workflows
- Working with CUDA-enabled applications

## Prerequisites

- NVIDIA GPU (RTX Pro 6000 or DGX Spark recommended)
  ```bash
  nvidia-smi  # Should show GPU with CUDA ≥12.9
  ```
- NVIDIA drivers and CUDA toolkit installed
  ```bash
  nvcc --version  # Should show CUDA 12.9 or higher
  ```
- Docker with NVIDIA Container Toolkit
  ```bash
  docker run --rm --gpus all nvidia/cuda:12.9.0-base-ubuntu22.04 nvidia-smi
  ```
- Python 3.8+ environment
  ```bash
  python3 --version  # Should show 3.8 or higher
  ```
- Sufficient disk space for databases (>3TB recommended)
  ```bash
  df -h  # Check available space
  ```

## Ancillary files

- OpenFold parameters (`finetuning_ptm_2.pt`) — pre-trained model weights for structure prediction
- PDB70 database — template structures for homology modeling
- UniRef90 database — sequence database for MSA generation
- MGnify database — metagenomic sequences for MSA generation
- Uniclust30 database — clustered UniProt sequences for MSA generation
- BFD database — large sequence database for MSA generation
- MMCIF files — template structure files in mmCIF format
- py3Dmol package — Python library for 3D protein visualization

## Time & risk

**Duration:** Initial setup takes 2-4 hours (mainly downloading databases). Each protein fold takes
<60 seconds on GPU vs hours on CPU.

**Risks:**
- Database downloads may fail due to network interruptions
- Insufficient disk space for full databases
- GPU memory limitations for very large proteins (>2000 residues)

**Rollback:** All operations are read-only after setup. Remove downloaded databases and output
directories to clean up.

## Access through terminal

## Step 1. Verify GPU and CUDA installation

Confirm your system has the required GPU and CUDA version for running OpenFold with TensorRT
optimization.

```bash
nvidia-smi
```

Expected output should show an NVIDIA GPU with CUDA capability ≥12.9. For DGX Spark or RTX Pro
6000, you should see the appropriate GPU model listed.

```bash
nvcc --version
```

This should display CUDA compilation tools, release 12.9 or higher.

## Step 2. Set up Python environment

Create a Python virtual environment and install the required packages for protein folding and
visualization.

```bash
python3 -m venv openfold_env
source openfold_env/bin/activate
pip install --upgrade pip
```

Install the py3Dmol visualization package:

```bash
pip install py3Dmol
```

## Step 3. Download OpenFold and databases

Download the OpenFold repository and required databases. This step requires significant disk
space and network bandwidth.

> TODO: Add specific download URLs for OpenFold repository from official GitHub

```bash
## Clone OpenFold repository
git clone https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets/-/blob/main
cd ${MODEL}/assets
pip install -e .
```

Download the model parameters:

> TODO: Add direct download URL for finetuning_ptm_2.pt

```bash
mkdir -p openfold_params
wget -O openfold_params/finetuning_ptm_2.pt <PARAM_DOWNLOAD_URL>
```

## Step 4. Download sequence databases

Download all required databases for MSA generation. Each database serves a specific purpose in
the folding pipeline.

> TODO: Add specific download URLs for each database from official sources

```bash
## Create database directory
mkdir -p databases
cd databases

## Download PDB70 (for template structures)
wget <PDB70_DOWNLOAD_URL>
tar -xzf pdb70.tar.gz

## Download UniRef90 (for MSA)
wget <UNIREF90_DOWNLOAD_URL>
tar -xzf uniref90.tar.gz

## Download MGnify (metagenomic sequences)
wget <MGNIFY_DOWNLOAD_URL>
tar -xzf mgnify.tar.gz

## Download Uniclust30 (clustered sequences)
wget <UNICLUST30_DOWNLOAD_URL>
tar -xzf uniclust30.tar.gz

## Download BFD (large sequence database)
wget <BFD_DOWNLOAD_URL>
tar -xzf bfd.tar.gz

## Download MMCIF files (structure templates)
wget <MMCIF_DOWNLOAD_URL>
tar -xzf mmcif.tar.gz

cd ..
```

## Step 5. Configure environment variables

Set up environment variables pointing to your downloaded databases and parameters.

```bash
export OF_PARAM_PATH="$(pwd)/openfold_params/finetuning_ptm_2.pt"
export OF_DB_PDB70="$(pwd)/databases/pdb70"
export OF_DB_UNIREF90="$(pwd)/databases/uniref90"
export OF_DB_MGNIFY="$(pwd)/databases/mgnify"
export OF_DB_UNICLUST30="$(pwd)/databases/uniclust30"
export OF_DB_BFD="$(pwd)/databases/bfd"
export OF_DB_MMCIF="$(pwd)/databases/pdb_mmcif/mmcif_files"
export OF_DB_OBSOLETE="$(pwd)/databases/pdb_mmcif/obsolete.dat"
export OF_DEVICE="cuda:0"
export OF_OUTDIR="openfold_out"
export OF_JOB="demo"
```

## Step 6. Option A - Use NVIDIA Build Portal (Cloud UI)

For quick testing without local setup, use NVIDIA's online demo interface.

1. Navigate to the OpenFold2 page on NVIDIA Build Portal
   > TODO: Add specific URL for NVIDIA Build Portal OpenFold2 demo

2. Paste your protein sequence in FASTA format

3. Click "Run" to execute the folding pipeline

4. View results in the integrated Mol* or py3Dmol viewer

### Step 7. Option B - Run locally with demo script

Create and run the OpenFold demo script for local execution on your DGX Spark or RTX Pro 6000.

Create the demo script file:

```bash
cat > openfold_demo.py << 'EOF'
#!/usr/bin/env python3
"""
Single-file OpenFold runner + py3Dmol viewer.
"""
import os, subprocess as sp, glob, sys, tempfile, textwrap

## Paths (edit for your system)
PARAM = os.getenv("OF_PARAM_PATH", "/path/to/openfold_params/finetuning_ptm_2.pt")
PDB70 = os.getenv("OF_DB_PDB70", "/path/to/pdb70")
UNIREF90 = os.getenv("OF_DB_UNIREF90", "/path/to/uniref90")
MGNIFY = os.getenv("OF_DB_MGNIFY", "/path/to/mgnify")
UNICLUST30 = os.getenv("OF_DB_UNICLUST30", "/path/to/uniclust30")
BFD = os.getenv("OF_DB_BFD", "/path/to/bfd")
MMCIF = os.getenv("OF_DB_MMCIF", "/path/to/pdb_mmcif/mmcif_files")
OBSOLETE = os.getenv("OF_DB_OBSOLETE", "/path/to/pdb_mmcif/obsolete.dat")
DEVICE = os.getenv("OF_DEVICE", "cuda:0")
OUTDIR = os.getenv("OF_OUTDIR", "openfold_out")
JOB = os.getenv("OF_JOB", "demo")

SEQ = """>demo
MGSDKIHHHHHHENLYFQGAMASMTGGQQMGRGSMAAAAKKVVAGAAAAGGQAGD"""

def ensure_py3dmol():
    try:
        import py3Dmol
    except ImportError:
        sp.check_call([sys.executable, "-m", "pip", "install", "py3Dmol"])

def run_openfold(fasta_path):
    cmd = [
        sys.executable, "openfold/run_pretrained_openfold.py",
        "--fasta_path", fasta_path,
        "--job_name", JOB,
        "--output_dir", OUTDIR,
        "--model_device", DEVICE,
        "--param_path", PARAM,
        "--pdb70_database_path", PDB70,
        "--uniref90_database_path", UNIREF90,
        "--mgnify_database_path", MGNIFY,
        "--uniclust30_database_path", UNICLUST30,
        "--bfd_database_path", BFD,
        "--template_mmcif_dir", MMCIF,
        "--obsolete_pdbs_path", OBSOLETE,
        "--skip_relaxation"
    ]
    sp.check_call(cmd)

def visualize():
    import py3Dmol
    pdb = open(f"{OUTDIR}/{JOB}/ranked_0.pdb").read()
    view = py3Dmol.view(width=800, height=520)
    view.addModel(pdb, "pdb")
    view.setStyle({"cartoon": {"arrows": True}})
    view.zoomTo()
    open(f"{OUTDIR}/{JOB}_view.html", "w").write(view._make_html())
    print(f"Viewer written to {OUTDIR}/{JOB}_view.html")

def main():
    ensure_py3dmol()
    with tempfile.TemporaryDirectory() as td:
        fasta_path = os.path.join(td, f"{JOB}.fasta")
        open(fasta_path, "w").write(textwrap.dedent(SEQ).strip() + "\n")
        run_openfold(fasta_path)
        visualize()

if __name__ == "__main__":
    main()
EOF
```

Make the script executable and run it:

```bash
chmod +x openfold_demo.py
python openfold_demo.py
```

## Step 8. Validate the output

Check that the folding completed successfully and view the generated structure.

```bash
## Verify PDB file was created
ls -la openfold_out/demo/ranked_0.pdb
```

The file should exist and be non-empty (typically >10KB for a small protein).

```bash
## Check the HTML viewer was generated
ls -la openfold_out/demo_view.html
```

Open the HTML file in a web browser to visualize the folded protein structure:

```bash
## On Linux with GUI
xdg-open openfold_out/demo_view.html

## Or copy the full path and open in browser manually
realpath openfold_out/demo_view.html
```

## Step 9. Run with custom sequences

To fold your own protein sequences, modify the demo script or create a new FASTA file.

### Using a custom FASTA file

```bash
## Create your FASTA file
cat > my_protein.fasta << 'EOF'
>my_protein
MTEYKLVVVGAGGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGETCLLDILDTAGQEEYSAMRDQYMRTGEGFLCVFAINNTKSFEDIHQYREQIKRVKDSDDVPMVLVGNKCDLPARTVETRQAQDLARSYGIPYIETSAKTRQGVEDAFYTLVREIRQHKLRKLNPPDESGPGCMNCKCVIS
EOF

## Run OpenFold directly
python openfold/run_pretrained_openfold.py \
    --fasta_path my_protein.fasta \
    --job_name my_protein \
    --output_dir openfold_out \
    --model_device cuda:0 \
    --param_path $OF_PARAM_PATH \
    --pdb70_database_path $OF_DB_PDB70 \
    --uniref90_database_path $OF_DB_UNIREF90 \
    --mgnify_database_path $OF_DB_MGNIFY \
    --uniclust30_database_path $OF_DB_UNICLUST30 \
    --bfd_database_path $OF_DB_BFD \
    --template_mmcif_dir $OF_DB_MMCIF \
    --obsolete_pdbs_path $OF_DB_OBSOLETE \
    --skip_relaxation
```

## Step 10. Troubleshooting common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| CUDA out of memory error | Protein too large for GPU | Reduce max_template_date or use smaller sequence |
| Database file not found | Incomplete download or wrong path | Verify all databases downloaded and paths in env vars |
| ImportError: No module named 'openfold' | OpenFold not installed | Run `pip install -e .` in openfold directory |
| nvidia-smi command not found | NVIDIA drivers not installed | Install NVIDIA drivers for your GPU |
| Folding takes hours instead of minutes | Running on CPU instead of GPU | Check OF_DEVICE="cuda:0" and GPU availability |
| py3Dmol viewer shows blank page | JavaScript blocked or path issue | Use absolute path to HTML file or check browser console |

## Step 11. Cleanup and rollback

Remove generated outputs and optionally remove downloaded databases.

```bash
## Remove output files only (safe)
rm -rf openfold_out/

## Remove virtual environment (reversible)
deactivate
rm -rf openfold_env/
```

> **Warning:** The following will delete downloaded databases (>3TB). Only run if you need to
> free disk space and are willing to re-download.

```bash
## Remove all databases (requires re-download)
rm -rf databases/

## Remove OpenFold repository
rm -rf openfold/
```

## Step 12. Next steps

Test the installation with a well-known protein structure to verify accuracy:

```bash
## Test with ubiquitin (PDB: 1UBQ)
cat > test_ubiquitin.fasta << 'EOF'
>1UBQ
MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG
EOF

python openfold/run_pretrained_openfold.py \
    --fasta_path test_ubiquitin.fasta \
    --job_name ubiquitin_test \
    --output_dir openfold_out \
    --model_device cuda:0 \
    --param_path $OF_PARAM_PATH \
    --pdb70_database_path $OF_DB_PDB70 \
    --uniref90_database_path $OF_DB_UNIREF90 \
    --mgnify_database_path $OF_DB_MGNIFY \
    --uniclust30_database_path $OF_DB_UNICLUST30 \
    --bfd_database_path $OF_DB_BFD \
    --template_mmcif_dir $OF_DB_MMCIF \
    --obsolete_pdbs_path $OF_DB_OBSOLETE \
    --skip_relaxation
```

For production use, consider:
- Enabling structure relaxation for higher accuracy (remove `--skip_relaxation`)
- Setting up batch processing for multiple sequences
- Integrating with drug discovery pipelines
- Scaling to full proteomes using DGX Spark clusters
