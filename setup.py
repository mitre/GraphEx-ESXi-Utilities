import os
import io
from pathlib import Path

from setuptools import find_namespace_packages, setup

def get_package_data():
    ROOT_PATH = os.path.abspath("./graphex_esxi_utils")
    DOCS_PATH = os.path.join(ROOT_PATH, "docs")
    files = []
    for directory, _, filenames in os.walk(DOCS_PATH):
        for filename in filenames:
            path = os.path.join(directory, filename)
            path = path[len(ROOT_PATH) :].strip("/")
            files.append(path)
    return {"graphex_esxi_utils": files}

def read_readme():
    readme_path = Path(__file__).parent / "README.md"
    with io.open(readme_path, "r", encoding="utf-8") as f:
        return f.read()

setup(
    name="graphex-esxi-utils",
    version="1.12.0",
    author="The MITRE Corporation",
    description="A plugin for adding python esxi utils nodes to graphex.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/mitre/GraphEx-ESXi-Utilities",
    project_urls={
        "Documentation": "https://github.com/mitre/GraphEx-ESXi-Utilities/blob/main/graphex_esxi_utils/docs/markdown/index.md",
        "Source": "https://github.com/mitre/GraphEx-ESXi-Utilities",
        "Issues": "https://github.com/mitre/GraphEx-ESXi-Utilities/issues",
        "Changelog": "https://github.com/mitre/GraphEx-ESXi-Utilities/blob/main/graphex_esxi_utils/docs/markdown/changelog.md",
    },
    license="Apache-2.0",
    license_files=["LICENSE"],
    keywords=["esxi", "vmware", "vsphere", "vcenter", "pyvmomi", "virtualization", "hypervisor", "ssh", "paramiko", "winrm", "pywinrm", "cisco", "netmiko", "network-automation", "palo-alto", "palo-alto-networks", "panos", "panorama", "pan-os", "panos-api", "firewall", "firewall-automation", "devops", "sysadmin", "infrastructure-automation", "datacenter", "automation", "remote-execution", "configuration-management", "orchestration", "python-library", "utilities"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    packages=find_namespace_packages(include=["graphex_esxi_utils*"]),
    package_data=get_package_data(),
    python_requires=">=3.10",
    install_requires=["mitre-graphex>=1.16.0", "esxi-utils>=3.25.0", "ping3==4.0.4", "pexpect==4.8.0"],
    include_package_data=True
)
