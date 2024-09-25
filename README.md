# Nautobot Jobs Repo (WORK IN PROGRESS)

## Description

The Nautobot jobs are develop to support the network operations for the HomeLab Network. The jobs are designed to perform basic operations with the Nautobot objects to aid network administrators with data manipulation in the Source of Truth. The long term goal is to model the network in Nautobot so it reflects the desired state and then deployed on the actual devices

The operations mentioned here include the following common network operations tasks:

- Import location details from external sources
- Import devices into the Source of Truth from external sources
- Set devices in the corresponding location
- Set management settings on the devices objects in the SoT
- Set intended setup on the device objects in the SoT to model the network as intended by the administrator (i.e. Deploy settings for a branch site)

Once the network is modeled in the SoT, a configuration management tool (i.e. Ansible) can be used to retrieve the device attributes from the SoT to then render a configuration file (in the correspoding vendor configuration syntax) and then applied to the corresponding devices.

## Hierarchy defined in Nautobot for the Network

The HomeLab Network has 3 different site types:

- Data Centers: SPINE/LEAF Fabrics intended to host applications
- Campus: Buildings for companies and building operations
- Branches: Small locations for customer facing stores. Stores


All site types are set within the same hierarchy:

```bash
Country:
  State:
    City:
      Site:
       Fabric: (DataCenter Only)
       Floor: (Campus Only)
```

*A site needs to be one of these types: DataCenter, Campus, Branch*

## Jobs in this package

| Name | Description | Dependencies |
| --- | --- | --- |
| SSoT Import Locations | Pull locations via API from CMDB | |
| SSoT Import Devices | Pull Devices via API from CMDB | |
| Set MGMT IP | Job to connect a device to a Management Switch and set an IP address in the Management network | Existing management prefix with corresponding role set |
| Deploy Small Branch | For a existing branch site, deploy required settings to model the branch network | |
