# DGX Spark Playbooks

A collection of tutorials and guides for NVIDIA DGX Spark devices. This repository contains the source content for playbooks published to the API catalog, along with comprehensive tools for creating, validating, and publishing new playbooks.

## 🎯 **Quick Start: Creating a New Playbook**

```bash
# 1. Copy the template
cp -r nvidia/a-template-project nvidia/my-awesome-tool

# 2. Fill out the template files (replace all {placeholders})
# - Edit metadata.yaml, overview.md, instructions.md, troubleshooting.md

# 2.5 (Optional) Add your source code if any
# - Add all source code and assets to nvidia/my-awesome-tool/assets folder

# 3. Commit and request review - CI/CD will handle the rest!
```

## 📚 **What Are DGX Spark Playbooks?**

DGX Spark playbooks are interactive, step-by-step tutorials that help users accomplish specific tasks on their NVIDIA DGX Spark devices. Each playbook includes:

- **Guided instructions** with code examples and verification steps
- **Prerequisites and setup** requirements 
- **Troubleshooting guides** for common issues
- **DGX Spark-specific optimizations** and best practices

Examples: Installing ComfyUI, setting up PyTorch training, configuring multi-node networking, etc.

## 🚀 **Step-by-Step: Creating Your First Playbook**

### **Step 1: Plan Your Playbook**

Before coding, define:
- **What will users accomplish?** (specific, measurable outcome)
- **What do they need to know?** (prerequisite skills/knowledge)
- **What hardware/software is required?** (DGX Spark specs, dependencies)
- **How long will it take?** (including downloads, setup time)
- **What could go wrong?** (common failure points and solutions)

### **Step 2: Copy and Customize the Template**

```bash
# Choose a descriptive name (lowercase, hyphens for spaces)
export PLAYBOOK_NAME="my-awesome-tool"

# Copy template
cp -r nvidia/a-template-project nvidia/$PLAYBOOK_NAME
cd nvidia/$PLAYBOOK_NAME

# Start with metadata.yaml - this defines the structure
# Replace ALL {placeholders} with your actual content
```

### **Step 3: Fill Out Each File**

#### **`metadata.yaml` - Project Configuration**
```yaml
catalog_name: nvidia/my-awesome-tool    # Must match directory
name: my-awesome-tool                   # Same as directory name
displayName: My Awesome Tool            # Human-readable name
short_description: Install and configure My Awesome Tool for AI workflows
publisher: nvidia                       # Always "nvidia"
labels:                                 # For search/categorization
- DGX
- Spark  
- YourTechnology
duration: 30 MIN                        # Realistic time estimate
```

#### **`overview.md` - Introduction & Prerequisites**
Required sections:
- **Basic idea** - What the tool does and why it's useful
- **What you'll accomplish** - Specific learning objectives  
- **What to know before starting** - Required skills/knowledge
- **Prerequisites** - Hardware and software requirements
- **Time & risk** - Duration, complexity, rollback plan

#### **`instructions.md` - Step-by-Step Tutorial**
Structure as numbered steps:
```markdown
# Step 1. Verify system prerequisites
# Step 2. Install dependencies  
# Step 3. Configure the application
# Step 4. Start and verify
# Step 5. Optional - Advanced configuration
```

#### **`troubleshooting.md` - Common Issues**
Use table format for quick scanning:
```markdown
| Symptom | Cause | Fix |
|---------|-------|-----|
| Specific error message | Root cause | Exact solution steps |
```

### **Step 4: Validate Your Work**

```bash
# Run the linter to check quality and completeness
./lint_playbooks.sh nvidia/$PLAYBOOK_NAME

# Fix any issues reported:
# - E### = Errors (must fix)
# - W### = Warnings (should fix)  
# - I### = Info (nice to have)
# - C### = Convention (style)
```
