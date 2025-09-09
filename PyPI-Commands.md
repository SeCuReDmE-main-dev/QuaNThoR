# PyPI Package Publishing Commands

## QuaNThoR Educational Tool - SCL Guardian Package

### Prerequisites
```bash
pip install twine build
```

### Build Package
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build distribution packages
python -m build

# Expected output:
# dist/scl-guardian-quanthor-2.0.0.tar.gz
# dist/scl_guardian_quanthor-2.0.0-py3-none-any.whl
```

### Test on TestPyPI First
```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ scl-guardian-quanthor
```

### Production PyPI Upload  
```bash
# Upload to production PyPI
python -m twine upload dist/*

# Verify installation
pip install scl-guardian-quanthor
```

### PyPI Account Setup Required
1. Create account at: https://pypi.org/account/register/
2. Use email: jeansebastienbeaulieuscrde.01@gmail.com
3. Generate API token
4. Configure credentials:

```bash
# ~/.pypirc
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC... # Your API token
```

### Package Information
- **Name**: scl-guardian-quanthor
- **Version**: 2.0.0
- **License**: SCL-2.0
- **Author**: Jean-Sébastien Beaulieu & SeCuReDmE Initiative
- **Email**: jeansebastienbeaulieuscrde.01@gmail.com

### Automatic Integration
Once published, QuaNThoR will automatically:
1. Install SCL Guardian on first run
2. Verify license compliance 
3. Activate educational protection
4. Monitor for violations

### Update Process
To update the package:
1. Increment version in setup.py
2. Update CHANGELOG.md
3. Rebuild and upload
4. All QuaNThoR installations will auto-update