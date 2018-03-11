#!/usr/bin/python

from interfaces import LoIntf, TapVXLANIntf, TapOpenVPNIntf
from utils import OSPFNetwork, EndIP

import sys

# Generic host object
class Host(object):

  # Base host
  def __init__(self, name, mgtip, tunneling):

    # General properties
    self.name = name
    self.mgtip = mgtip
    self.tunneling = tunneling

    # Endpoints and mapping name to endip
    self.endips = []
    self.nameToEndIps = {}
    self.endIPBase = 1

    # Taps interfaces and mapping name to tap
    self.taps = []
    self.nameToTaps = {}
    self.tapBase = 1
    self.tapPortBase = 1190

# SRv6 based router
class SRv6Router(Host):

  intf = "eth0"

  def __init__( self, name, tunneling, properties, vnfs, terms):
    # Init Host object
    Host.__init__(self, name, properties['floating_ip'], tunneling)

    # Init objects related to OSPF networks
    self.ospfnets = []
    self.nameToNets = {}
    self.ospfNetBase = 1

    # Save general, vnfs and terms properties
    self.properties = properties
    self.vnfs = vnfs
    self.terms = terms

    # Create Loopback interface
    self.loopback = self.addLoopback(properties['loopback'])

  # Utility function to create a new Link
  # OSPFNet name
  def newLinkNetName(self):
    ret = self.ospfNetBase
    self.ospfNetBase = self.ospfNetBase + 1
    return "NET%s" % ret 

  # Utility function to create a new Link
  # OSPFNet name
  def newLoopbackNetName(self):
    return "LBN"

  # Create loopback interface and related OSPF network
  def addLoopback(self, loopback):
    loopback = LoIntf(ip=loopback)
    loopbacknet = OSPFNetwork("loopback", "%s/128" % loopback.ip )
    self.addOSPFNet(loopbacknet, "LOOPBACK")
    return loopback

  # Add to the node a new OSPFNetwork
  def addOSPFNet(self, net, type):
    found = False
    for ospfnet in self.ospfnets:
      if net.net == ospfnet.net:
        found = True
        break
    if found == False:
      if type == "LOOPBACK":
        name = self.newLoopbackNetName()
      elif type == "LINK":
        name = self.newLinkNetName()
      elif type == "VNF":
        name = self.newVNFNetName()
      else:
        name = self.newTERMNetName()
      net.name = name
      self.ospfnets.append(net)
      self.nameToNets[name] = net
    else:
      net = ospfnet 
    return net

  # Allocate a new tap port
  def newTapPort(self):
    self.tapPortBase = self.tapPortBase + 1
    return self.tapPortBase

  # Allocate a new tap name
  def newTapName(self):
    ret = self.tapBase
    self.tapBase = self.tapBase + 1
    return "tap%s" % ret

  # Add a new interface to the node
  def addIntf(self, param):
    if len(param) != 6:
      print "Error addIntf invalid parameter"
      sys.exit(-2)
    # Let's allocate first the net
    ospf_net = param[4]
    ospf_net = self.addOSPFNet(ospf_net, "LINK")
    # Then we create the TAP interface for the tunnel
    tap = self.addTap(param)
    return (tap, ospf_net)

  # Add a new tap interface for the link
  def addTap(self, param):
    if len(param) != 6:
        print "Error addTap invalid parameter"
        sys.exit(-2)
    name = self.newTapName()
    # Let's create the proper endpoint
    remote_ip = param[0]
    local_eth = param[1]
    endip = self.addEndIP(remote_ip, local_eth)
    # According to the tunneling mechanism
    # we are going to create the right tap
    net = param[4]
    ip = param[5]
    if self.tunneling == "OpenVPN":
      local_port = param[2]
      remote_port =param[3]
      tap = TapOpenVPNIntf(
        name, local_port,
        remote_port, endip.name,
        ip, net
      )
    elif self.tunneling == "VXLAN":
      vni = param[3]
      tap = TapVXLANIntf(
        name, vni,
        endip.name,
        ip, net
      )
    # Done, add the tap to the internal structures
    self.taps.append(tap)
    self.nameToTaps[name] = tap
    return tap

  # Allocate a new end ip name
  def newEndIPName(self):
    ret = self.endIPBase
    self.endIPBase = self.endIPBase + 1
    return "endip%s" % ret

  # Add a new end ip object
  def addEndIP(self, remoteIP, localIntf):
    name = self.newEndIPName()
    endip = EndIP(name, remoteIP, localIntf)
    self.endips.append(endip)
    self.nameToEndIps[name] = endip
    return endip


   


