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
# device_if should be a property of the router
def topo(topology, default_device_if, ob_notification):

  # First parse the json file
  verbose = True
  if verbose:
    print "*** Building Topology from parsed file"
  parser = SRv6TopoParser(topology, ob_notification, verbose = False)
  parser.parse_data()

  # Get back the parsed data
  testbed = SoftfireSRv6Router(parser.tunneling)
  routers = parser.routers
  p_routers_properties = parser.routers_properties
  p_routers_dict = parser.routers_dict
  p_ip_addr_map = parser.ip_addr_map
  core_links = parser.core_links
 
  # store ip_addr_map
  ip_file = open("cfg/ip_addr_map.json", 'w')
  ip_file.write(json.dumps(p_ip_addr_map))
  ip_file.close() 

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
  static_routes = {}
  for router in routers:
    #vnfs = parser.getVNF(router)
    #ters = parser.getTER(router)
    vnfs_and_ters = parser.getVNFandTERMdict(router)

    [r_vnf_properties, r_ter_properties, net] = generator.getVNFsTERMsProperties(vnfs_and_ters)
    vnfs_properties[router] = r_vnf_properties
    ters_properties[router] = r_ter_properties
    static_routes[router] = net

  print "*** Adding SRv6 routers"
  i = 0
  # Add router to the testbed
  for router_properties in routers_properties:
    router = routers[i]
    vnf_properties = vnfs_properties[router]
    ter_properties = ters_properties[router]

    static_route = static_routes[router]
    router_properties = routers_properties[i]
    p_router_properties = p_routers_properties[i]
    p_router_properties['loopback'] = router_properties.loopback
    p_router_properties['routerid'] = router_properties.routerid

    #adding IP addresses retrieved from OpenBaton notification
    p_router_properties['internal_ip'] = p_ip_addr_map[router]['internal_ip']
    p_router_properties['floating_ip'] = p_ip_addr_map[router]['floating_ip']

    testbed.addSRv6Router(
      router,
      p_router_properties,
      vnf_properties,
      ter_properties,
      static_route,
      default_device_if
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
  # ./softfire-tiesr-deployer.py --topology topo/linear-2ads-2surrey.json
  # ./softfire-tiesr-deployer.py --topology ../dreamer-topology-parser-and-validator/rdcl4nodesok.json --ob_notification ../dreamer-topology-parser-and-validator/openbaton_notification.json


  parser = argparse.ArgumentParser(description='Softfire TIESR Deployer')
  parser.add_argument('--topology', dest='topoInfo', action='store', default='topo:topo1.json', help='topo:param see README for further details')
  parser.add_argument('--default_dev_if', dest='defDevIf', action='store', default='ens3', help='topo:param see README for further details')
  parser.add_argument('--ob_notification', dest='OB_notif', action='store', default='openbaton.json', help='topo:param see README for further details')
  # Check params number
  args = parser.parse_args()  
  if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    # Return the topology name
  topo_data = args.topoInfo 
  def_device_if = args.defDevIf
  ob_notification = args.OB_notif
  return (topo_data, def_device_if, ob_notification)

if __name__ == '__main__':
  (topology, def_device_if, ob_notification) = parse_cmd_line()
  topo(topology, def_device_if, ob_notification)
