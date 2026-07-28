
# Research & Experimentation Notebooks

## Overview

The `notebooks` directory contains research notebooks created during the development of the Smart Vehicle Identifier project.

These notebooks document the experimentation phase, including model evaluation, dataset preparation, fine-tuning workflows, hyperparameter exploration, and performance analysis.

They are preserved as development artifacts and serve as a reference for future research and model improvements.

---

# Purpose

The notebooks were used for:

- Exploring different AI models.
- Preparing training datasets.
- Evaluating model performance.
- Experimenting with fine-tuning strategies.
- Testing preprocessing pipelines.
- Validating different training configurations.

---

# Folder Structure

```
notebooks/
│
├── Qwen3-VL-8B-Instruct_V1.ipynb
├── Qwen3-VL-8B-Instruct1_V2.ipynb
├── Qwen3-VL-8B-Instruct1_V3.ipynb
├── Qwen3-VL-8B-Instruct1_V4.ipynb
└── Qwen3-VL-8B-Instruct1_V5.ipynb
```

---

# Notebook Evolution

The notebooks represent multiple iterations of the development process.

Each version includes incremental improvements such as:

- Dataset preparation.
- Prompt optimization.
- Fine-tuning experiments.
- Hyperparameter adjustments.
- Performance evaluation.
- Training workflow refinements.

---

# Development Process

During the research phase, several fine-tuning experiments were conducted to evaluate the feasibility of adapting a Vision-Language Model for vehicle understanding.

These experiments helped the team better understand the model's capabilities, training requirements, and deployment considerations.

After evaluating the available computational resources and the overall system requirements, the final production architecture adopted a hosted inference approach while preserving these notebooks for documentation and future development.

---

# Current Project Usage

The notebooks are **not part of the production pipeline**.

They are retained for:

- Research documentation.
- Experiment reproducibility.
- Future model improvements.
- Academic reference.
- Additional fine-tuning experiments.

---

# Development Rules

- Notebooks are intended for experimentation only.
- Production code should reside outside this directory.
- New experiments should be versioned clearly.
- Significant findings should be documented before deployment.

---

# Future Work

Potential future work includes:

- Additional fine-tuning experiments.
- Larger training datasets.
- Parameter-efficient fine-tuning (PEFT).
- LoRA-based adaptation.
- Model benchmarking.
- Training optimization.
