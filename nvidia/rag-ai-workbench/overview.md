# Basic idea

This walkthrough demonstrates how to set up and run an agentic retrieval-augmented generation (RAG)
project using NVIDIA AI Workbench. You'll use AI Workbench to clone and run a pre-built agentic RAG
application that intelligently routes queries, evaluates responses for relevancy and hallucination, and
iterates through evaluation and generation cycles. The project uses a Gradio web interface and can work
with both NVIDIA-hosted API endpoints or self-hosted models.

# What you'll accomplish

You'll have a fully functional agentic RAG application running in NVIDIA AI Workbench with a web
interface where you can submit queries and receive intelligent responses. The system will demonstrate
advanced RAG capabilities including query routing, response evaluation, and iterative refinement,
giving you hands-on experience with both AI Workbench's development environment and sophisticated RAG
architectures.

# What to know before starting

- Basic familiarity with retrieval-augmented generation (RAG) concepts
- Understanding of API keys and how to generate them
- Comfort working with web applications and browser interfaces
- Basic understanding of containerized development environments

# Prerequisites

- DGX Spark system with NVIDIA AI Workbench installed or ready to install
- Free NVIDIA API key: Generate at [NGC API Keys](https://org.ngc.nvidia.com/setup/api-keys)
- Free Tavily API key: Generate at [Tavily](https://tavily.com/)
- Internet connection for cloning repositories and accessing APIs
- Web browser for accessing the Gradio interface

# Verification commands

- Verify the NVIDIA AI Workbench application exists on your DGX Spark system
- Verify your API keys are valid and up-to-date


# Time & risk

* **Estimated time:** 30-45 minutes (including AI Workbench installation if needed)
* **Risk level:** Low - Uses pre-built containers and established APIs
* **Rollback:** Simply delete the cloned project from AI Workbench to remove all components. No system changes are made outside the AI Workbench environment.
