# Changelog

This page was created to track changes to versions of GraphEx-ESXi-Utilities. The changelog was created in v1.9.4 and only changes starting from that version are tracked here.

## 2.0.0

- Adds new nodes to support new Functionality from Python-ESXi-Utilties 4.0.0
    - VirtualMachine objects are now visible at the inventory level instead of the child host level in vCenter
        - This also means you can deploy VMs to other hosts even though you connect to a specific child
    - Support for converting VMs into templates and deploying/cloning those templates into new VMs
    - New nodes for collecting information about VM location under vCenter
- Fix several regex warnings in library import for Python version 3.12+
- Silences the deprecation warning about the pinning of setuptools pkg_resources API
- Adds the node "ESXi Hard Stop Virtual Machine" to allow for forceful shutdowns of unresponsive VMs (or quicker deletion/cleanup)

## 1.11.0

- Adds a new node: 'ESXi Get Most Recently Modified DatastoreFile' to get the file most recently modified in an ESXi Datastore for a given directory/folder

## 1.10.0

- Adds a new node: 'ESXi Virtual Machine Get Boot Time' to get the time a VM booted at

## 1.9.4

- Bugfix for node "ESXi NIC VirtualDevice Set Network" having an output socket instead of an input socket for the name of the network to assign
- Update package metadata for PyPI
- Bump required version of esxi_utils (Python-ESXi-Utilities)
