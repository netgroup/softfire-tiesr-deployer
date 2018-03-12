# SoftFIRE TIESR Deployer  #

This project is for creating virtual networks to emulate SRv6 

### Prerequisite ###

This project depends on Dreamer-Topology-Parser

    > cd /home/user/workspace/
    > git clone https://pierventre@bitbucket.org/ssalsano/dreamer-topology-parser-and-validator.git

Then it is necessary to properly set the path in the softfire-tiesr-deployer project

    > cd /home/user/workspace/softfire-tiesr-deployer
    > parser_path = "/home/user/workspace/dreamer-topology-parser-and-validator/"

### Run an example experiment ###

    > cd /home/user/workspace/softfire-tiesr-deployer

--help for usage options

    Usage: softfire-tiesr-deployer.py [options]

    Options:
    -h, --help            show this help message and exit
    --topology=TOPOLOGY   Topology file

You can build configuration files of a topology just providing a topology file (relative path)

    > ./softfire-tiesr-deployer.py --topology topo/example_srv6_topology.json


The generated files are in the cfg folder: 

    > cat /home/user/workspace/softfire-tiesr-deployer/cfg/*.cfg