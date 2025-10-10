import os

from setuptools import find_packages, setup

def get_package_data():
    ROOT_PATH = os.path.abspath("./graphex-esxi-utils")
    DOCS_PATH = os.path.join(ROOT_PATH, "docs")
    files = []
    for directory, _, filenames in os.walk(DOCS_PATH):
        for filename in filenames:
            path = os.path.join(directory, filename)
            path = path[len(ROOT_PATH) :].strip("/")
            files.append(path)
    return {"graphex-esxi-utils": files}

setup(
    name="graphex-esxi-utils",
    version="1.9.1",
    author="The MITRE Corporation",
    description="A plugin for adding python esxi utils nodes to graphex.",
    packages=find_packages(include=["graphex-esxi-utils*"]),
    package_data=get_package_data(),
    python_requires=">=3.10",
    install_requires=["mitre-graphex>=1.16.0", "esxi-utils>=3.22", "ping3==4.0.4", "pexpect==4.8.0"],
    include_package_data=True
)
