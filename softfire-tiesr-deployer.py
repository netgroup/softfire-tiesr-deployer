#!/usr/bin/python

from collections import defaultdict

from testbed import SoftfireSRv6Router

import argparse
import sys
import os
import json

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
    print "*** Building Topology from parsed file"
  parser = SRv6TopoParser(topology, verbose = False)
  parser.parse_data()

  # Get back the parsed data
  testbed = SoftfireSRv6Router(parser.tunneling)
  routers = parser.routers
  p_routers_properties = parser.routers_properties
  core_links = parser.core_links

  # Creates properties generator
  generator = PropertiesGenerator()

  print "*** Generating configuration parameters"
  # Second step is the generation of the nodes parameters
  routers_properties = generator.getRouterProperties(routers)

  # Third step is the generation of the links parameters
  core_links_properties = []
  for core_link in parser.core_links:
    core_links_properties.append(generator.getLinksProperties([core_link]))

  # Finally VNFs and TERMs related parameters
  vnfs_properties = defaultdict(list)
  ters_properties = defaultdict(list)
  default_routes = {}
  for router in routers:
    vnfs = parser.getVNF(router)
    ters = parser.getTER(router)
    [r_vnf_properties, r_ter_properties, net] = generator.getVNFsTERMsProperties(vnfs, ters)
    vnfs_properties[router] = r_vnf_properties
    ters_properties[router] = r_ter_properties
    default_routes[router] = net

  print "*** Adding SRv6 routers"
  i = 0
  # Add router to the testbed
  for router_properties in routers_properties:
    router = routers[i]
    vnf_properties = vnfs_properties[router]
    ter_properties = ters_properties[router]
    default_route = default_routes[router]
    router_properties = routers_properties[i]
    p_router_properties = p_routers_properties[i]
    p_router_properties['loopback'] = router_properties.loopback
    p_router_properties['routerid'] = router_properties.routerid
    testbed.addSRv6Router(
      router,
      p_router_properties,
      vnf_properties,
      ter_properties,
      default_route
    )
    i = i + 1;

  print "*** Adding core links"
  i = 0;
  # Add core links to the testbed
  for core_link_properties in core_links_properties:
    link = core_links[i]
    testbed.addCoreLink(
      link,
      core_link_properties[0]
    )
    i = i + 1

  print "*** Generating configuration files"
  testbed.configure()

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
