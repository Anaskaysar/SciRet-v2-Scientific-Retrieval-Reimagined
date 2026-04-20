# This script reinstalls PyTorch with CUDA 12.4 support for the SciRet2 venv.
# CUDA 12.4 is chosen for compatibility with the CUDA 12.8 driver detected on this system.

.\venv\Scripts\python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 --force-reinstall
