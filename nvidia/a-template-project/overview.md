# Basic idea

<!-- 
OVERVIEW TEMPLATE: This file introduces your playbook and sets expectations.
Replace all placeholder text in {} with your actual content.
Remove these comment blocks when you're done.

PURPOSE: Help users understand what they'll accomplish and if this playbook is right for them.
-->

{Brief description of what your tool/technology does and why it's useful.}

{Explain how it works at a high level - 2-3 sentences maximum.}

{Optional: Include any key benefits or unique features.}

# What you'll accomplish

<!-- 
LEARNING OBJECTIVES: Be specific about what users will achieve.
Use action verbs: install, configure, deploy, create, etc.
-->

You'll {main objective - what the user will have working at the end}.

{Optional: List 2-3 secondary objectives or capabilities they'll gain.}

# What to know before starting

<!-- 
PREREQUISITES: List required knowledge/experience.
Be honest about skill level needed - helps users self-select.
Order from most to least important.
-->

- {Required skill 1 - e.g., Experience with Linux command line}
- {Required skill 2 - e.g., Basic understanding of Docker containers}  
- {Required skill 3 - e.g., Familiarity with Python package management}
- {Optional skill - e.g., Knowledge of machine learning concepts (helpful but not required)}

# Prerequisites
<!-- List specific hardware and software needs -->
- Minimum {X}GB GPU memory {explain why - e.g., "for model inference"}
- At least {X}GB available storage space {explain what it's for - e.g., "for model downloads"}
- {Any other hardware requirements}

- {Software 1}: `{command to check if installed}`
- {Software 2}: `{command to check if installed}`
- {Network access requirement - e.g., "Network access to download models from Hugging Face"}
- {Port access requirement - e.g., "Web browser access to `<SPARK_IP>:8080` port"}

# Ancillary files

<!-- 
SUPPORTING FILES: List important files users will encounter or need.
Link to source code when possible.
-->

All required assets can be found [in the {Tool Name} repository](${GITLAB_ASSET_BASEURL}/${MODEL}/).

- `{filename}` - {Description of what this file does}
- `{filename}` - {Description of what this file does}

# Time & risk

<!-- 
EXPECTATIONS: Help users plan their time and understand potential issues.
Be realistic about time estimates.
-->

* **Estimated time:** {XX} minutes or {XX} hours {include what takes the most time - e.g., "(including model download)"}
* **Risk level:** {Low/Medium/High}
  * {Risk factor 1 - e.g., "Large downloads may fail due to network issues"}  
  * {Risk factor 2 - e.g., "Port X must be accessible for web interface functionality"}
* **Rollback:** {How to undo changes if something goes wrong - e.g., "Virtual environment can be deleted to remove all installed packages. Downloaded models can be removed manually from the models directory."}
