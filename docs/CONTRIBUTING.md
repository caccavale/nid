
fork and pr or contact bouk for repo perms

setup steps

from your terminal:
```sudo apt update
sudo apt install python3 python3-pip```

verify your installs:
```python3 --version
pip3 --version```

clone your repo.

from nid/ run the justfile setup step
`justfile setup`

Justfile setup will install your venv and install all requirements.

Activate venv after calling `justfile setup` w/:
`source venv/bin/activate`