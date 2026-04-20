# Reinstall PyTorch with CUDA Support

The user wants to enable CUDA on Windows while ensuring the project remains compatible with a Mac (no CUDA).

## Proposed Changes

### Environment Management

#### [NEW] [install_torch.ps1](file:///d:/SciRet-Scientific-Information-Made-Easy/Sciret2/install_torch.ps1)
Create a helper script for Windows users to install the correct PyTorch version with CUDA support. (Targeting CUDA 12.4 as it's the current stable support for Torch 2.4/2.5+).

```powershell
.\venv\Scripts\python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 --force-reinstall
```

#### [MODIFY] [requirements.txt](file:///d:/SciRet-Scientific-Information-Made-Easy/Sciret2/requirements.txt)
Mention that CUDA-specific PyTorch should be installed separately or use a separate file.

## Platform-Specific Strategy

| Platform | Command |
| :--- | :--- |
| **Windows (CUDA 12.4)** | `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 --force-reinstall` |
| **Mac (MPS Support)** | `pip install torch torchvision torchaudio` (This installs the default version which supports Apple Silicon/Metal natively) |

### Strategies to avoid CUDA on Mac:
1. **Don't hardcode `--index-url` in [requirements.txt](file:///d:/SciRet-Scientific-Information-Made-Easy/Sciret2/requirements.txt)**: Keep [requirements.txt](file:///d:/SciRet-Scientific-Information-Made-Easy/Sciret2/requirements.txt) simple (e.g., `torch`, `torchvision`). This is platform-agnostic.
2. **Platform-Specific Install Flow**:
   - **On Mac**: Just run `pip install -r requirements.txt`.
   - **On Windows**: Run `pip install -r requirements.txt` and then run the `--index-url` command above to "upgrade" PyTorch to the CUDA version.
3. **Environment Markers** (Advanced): You can use markers in [requirements.txt](file:///d:/SciRet-Scientific-Information-Made-Easy/Sciret2/requirements.txt) like:
   `torch --index-url https://download.pytorch.org/whl/cu124 ; sys_platform == 'win32'`
   (Note: This requires a specific pip setup and is often less reliable than a simple script).

## Verification Plan

### Automated Tests
- Run `python -c "import torch; print(torch.cuda.is_available())"` on Windows.

### Manual Verification
- Confirm `nvidia-smi` shows a compatible CUDA version.
