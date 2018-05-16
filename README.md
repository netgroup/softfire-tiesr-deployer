# SoftFIRE TIESR Deployer  #

This project creates the configuration of virtual networks for testing the SRv6 technology over IAAS like testbeds

### Prerequisite ###

This project depends on [Dreamer Topology Parser and Validator](https://github.com/netgroup/Dreamer-Topology-Parser)

    > git clone https://github.com/netgroup/Dreamer-Topology-Parser
    > sudo python setup.py install

### Run an example experiment ###

**--help** for usage options:

    Usage: softfire-tiesr-deployer.py [options]

    Options:
    -h, --help            show this help message and exit
    --topology=TOPOLOGY   Topology file

You can obtain the configuration files of a topology just providing a complete topology file (including the mapping):

    > ./softfire-tiesr-deployer.py --topology topo/example_softfire_complete_topology.json

Otherwise you need to provide also the OpenBaton notification file:

    > ./softfire_tiesr_deployer.py --topology topo/example_softfire_topology.json --ob_notification topo/example_openbaton_notification.json

The generated files are in the cfg folder: 

    > cat cfg/*.cfg

cfg folder includes also the vm-mapping file:
    
    > cat cfg/ip_addr_map.json