#!/usr/bin/python

from collections import defaultdict

import argparse
import sys
import os

parser_path = "../dreamer-topology-parser-and-validator/"
if parser_path == "":
  print "Error Set Environment Variable At The Beginning Of File"
  sys.exit(-2)

sys.path.append(parser_path)
from srv6_topo_parser import SRv6TopoParser
from generator import PropertiesGenerator

# Build Topology from json file and as output of the computation
# build configuration files for the experiment
def topo(topology):

  # First parse the json file
  verbose = True
  if verbose:
    print "*** Build Topology from parsed file"
  parser = SRv6TopoParser(topology, verbose = False)
  parser.parse_data()

  # Get back the parsed data
  testbed = parser.testbed
  tunneling = parser.tunneling
  routers = parser.routers
  routers_properties = parser.routers_properties
  core_links = parser.core_links

  # Let' s properties generator
  generator = PropertiesGenerator()

  # Second step is the generation of the nodes parameters
  routers_properties = generator.getRouterProperties(routers)

  # Debug prints
  for router_properties in routers_properties:
    if verbose:
      print router_properties

  # Third step is the generation of the links parameters
  core_links_properties = []
  for core_link in parser.core_links:
    core_links_properties.append(generator.getLinksProperties([core_link]))

  # Debug prints
  for core_link_properties in core_links_properties:
    if verbose:
      print core_link_properties[0]

  # Then VNFs related parameters
  vnfs_properties = defaultdict(list)
  for router in routers:
    vnfs = parser.getVNF(router)
    r_vnf_properties = generator.getVNFsProperties(vnfs)
    vnfs_properties[router] = r_vnf_properties

  # Debug prints
  for router in routers:
    r_vnf_properties = vnfs_properties[router]
    for vnf_properties in r_vnf_properties:
      if verbose:
        print vnf_properties

  # Finally TERMs related parameters
  ters_properties = defaultdict(list)
  for router in routers:
    ters = parser.getTER(router)
    r_ter_properties = generator.getTERsProperties(ters)
    ters_properties[router] = r_ter_properties

  # Debug prints
  for router in routers:
    r_ter_properties = ters_properties[router]
    for ter_properties in r_ter_properties:
      if verbose:
        print ter_properties

# Parse cmd line
def parse_cmd_line():
  # We just have the topology as cmd line parameter
  parser = argparse.ArgumentParser(description='Softfire TIESR Deployer')
  parser.add_argument('--topology', dest='topoInfo', action='store', default='topo:topo1.json', help='topo:param see README for further details')
  # Check params number
  args = parser.parse_args()  
  if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    # Return the topology name
  topo_data = args.topoInfo 
  return (topo_data)

if __name__ == '__main__':
  (topology) = parse_cmd_line()
  topo(topology)