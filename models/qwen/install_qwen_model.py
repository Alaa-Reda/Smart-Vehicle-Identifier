"""
Download the Qwen Vision-Language model for local inference.

This script is OPTIONAL.

The Smart Vehicle Identifier project uses the online hosted Qwen model
by default. Run this script only if you plan to execute the model locally
and have sufficient hardware resources.
"""

from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="Qwen/Qwen3-VL-8B-Instruct",
    local_dir="models/qwen/Qwen3-VL-8B-Instruct",
    local_dir_use_symlinks=False,
)

print("Download Complete!")