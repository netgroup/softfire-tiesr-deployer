#!/usr/bin/python

import copy

from nodes import SRv6Router
from utils import OSPFNetwork

class SoftfireSRv6Router( object ):

  def __init__(self, tunneling):
    # Name to node mapping
    self.nameToNode = {}
    # Set the chosen tunneling
    self.tunneling = tunneling
    # Init the vni base
    self.vniBase = 1
    # Init the ospf base
    self.ospfBase = 1
    # Array of SRV6 based routers
    self.srv6Routers = []
    # Mapping Nodes to VIM
    self.nodesToVIM = {}
    # Mapping Nodes to floating IP
    self.nodesToFIP = {}
    #M Mapping Nodes to internal IP
    self.nodesToIIP = {}
    # All ospf networks in this testbed
    self.ospfnets = []
    # Mapping name to network
    self.nameToOSPFNet = {}

  # Lookup nodes by name
  def getNodeByName(self, key):
    return self.nameToNode[key]

  # Add a new router to the testbed
  def addSRv6Router(self, router, properties, vnfs, terms, static_routes, device_if):
    print "*** Adding router", router

    # Add mapping node to vim
    self.nodesToVIM[router] = properties['vim']

    # Add mapping node to floating ip
    self.nodesToFIP[router] = properties['floating_ip']

    # Add mapping node to internal ip
    self.nodesToIIP[router] = properties['internal_ip']

    # Let's create a SRv6 router
    srv6Router = SRv6Router(
      router,
      self.tunneling,
      properties,
      vnfs,
      terms,
      static_routes,
      device_if
    )

    # Let's save it in the list of the routers
    self.srv6Routers.append(srv6Router)

    # Finally set name-node lookup
    self.nameToNode[router] = srv6Router

    # Done, return the new object
    return srv6Router

  # Add a new router to the testbed
  def addCoreLink(self, link, properties):
    print "*** Adding link", link

    # Retrieve lhs, rhs
    lhs = self.getNodeByName(link[0]) 
    rhs = self.getNodeByName(link[1])

    # According to the location of the VMS
    # retrieve the proper remote endpoint
    rhs_eth_ip = self.getRemoteIP(lhs, rhs)
    lhs_eth_ip = self.getRemoteIP(rhs, lhs)

    # Allocate the tap for OpenVPN and the VNI for VXLAN
    lhs_tap_port = lhs.newTapPort()
    rhs_tap_port = rhs.newTapPort()
    vni = self.newVNI()

    # Create the OSPF network for the link
    ospf_net = self.addOSPFNet(properties.net)
    lhs_ip = properties.iplhs
    rhs_ip = properties.iprhs
    lhs_ospf_net = copy.deepcopy(ospf_net)
    rhs_ospf_net = copy.deepcopy(ospf_net)

    # Add the interfaces to the nodes
    (lhs_tap, lhs_ospf_net) = lhs.addIntf([
      rhs_eth_ip, lhs_tap_port,
      rhs_tap_port, vni,
      lhs_ospf_net, lhs_ip
    ])
    (rhs_tap, rhs_ospf_net) = rhs.addIntf([
      lhs_eth_ip, rhs_tap_port, 
      lhs_tap_port, vni,
      rhs_ospf_net, rhs_ip
    ])

    # Done, return the useful interfaces
    return [(lhs_tap, lhs_ospf_net), (rhs_tap, rhs_ospf_net)]

  # Retrieve the remote endpoint
  def getRemoteIP (self, local, remote):

    # Retrieve local vim and remote vim
    local_vim = self.nodesToVIM[local.name]
    remote_vim = self.nodesToVIM[remote.name]

    # We have to use the internal ip
    if local_vim == remote_vim:
      return self.nodesToIIP[remote.name]

    # Otherwise we have to use the floating ip
    return self.nodesToFIP[remote.name]

  # Allocate a new VNI
  def newVNI(self):
    ret = self.vniBase
    self.vniBase = self.vniBase + 1
    return ret

  # Allocate a new OSPF net and verify its existence    
  def addOSPFNet(self, ip):
    found = False
    for ospfnet in self.ospfnets:
      if ip == ospfnet.net:
        found = True
        break
    if found == False:
      name = self.newOSPFNetName()
      net = OSPFNetwork(name, ip)
      self.ospfnets.append(net)
      self.nameToOSPFNet[name] = net
    else:
      net = ospfnet 
    return net

  # Create a new network name
  def newOSPFNetName(self):
    ret = self.ospfBase
    self.ospfBase = self.ospfBase + 1
    return "NET%s" % ret

  # Create ocnfiguration files for the nodes
  def configure(self):
    # Iterates over the SRv6 routers and call configure
    for srv6Router in self.srv6Routers:
      srv6Router.configure([
        "SOFTFIRE",
        self.tunneling
      ])
