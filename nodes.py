#!/usr/bin/python

from interfaces import LoIntf, TapVXLANIntf, TapOpenVPNIntf
from utils import OSPFNetwork, EndIP, VNFdata, TERM

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

  #intf = "eth0"

  def __init__( self, name, tunneling, properties, vnfs, terms, static_routes, device_if):
    # Init Host object
    Host.__init__(self, name, properties['floating_ip'], tunneling)

    self.device_if = device_if

    # Save static_routes
    self.static_routes = static_routes

    # Init objects related to OSPF networks
    self.ospfnets = []
    self.nameToNets = {}
    self.ospfNetBase = 1

    # Save vnfs 
    self.vnfs = []
    self.nameToVNFs = {}
    self.vnfBase = 1
    self.vnfNetBase = 1
    for vnf in vnfs:
      self.addVNF(vnf)

    # Save terms 
    self.terms = []
    self.nameToTERMs = {}
    self.termBase = 1
    self.termNetBase = 1
    for term in terms:
      self.addTERM(term)

    # Create Loopback interface and save router id
    self.loopback = self.addLoopback(properties['loopback'])
    self.routerid = properties['routerid']

  # Utility function to create a new TER
  # OSPFNet name
  def newTERMNetName(self):
    ret = self.termNetBase
    self.termNetBase = self.termNetBase + 1
    return "TNE%s" % ret 

  # Utility function to create a new TER name
  def newTERMName(self):
    ret = self.termBase
    self.termBase = self.termBase + 1
    return "TER%s" % ret 

  # Utility function to create a new VNF
  def addTERM(self, property):
    name = self.newTERMName()
    term = TERM(
      name, 
      property.ip,
      property.via,
      property.net
    )
    termnet = OSPFNetwork(name, property.net)
    self.addOSPFNet(termnet, "TERM")
    self.terms.append(term)
    self.nameToTERMs[name] = term
    return term

  # Utility function to create a new VNF
  # OSPFNet name
  def newVNFNetName(self):
    ret = self.vnfNetBase
    self.vnfNetBase = self.vnfNetBase + 1
    return "VNE%s" % ret 

  # Utility function to create a new VNF name
  def newVNFName(self):
    ret = self.vnfBase
    self.vnfBase = self.vnfBase + 1
    return "VNF%s" % ret 


  # Utility function to create a new VNF
  def addVNF(self, property):
    #name = self.newVNFName()
    vnf = VNFdata(
      property.id, 
      property.ip,
      property.via,
      property.br,
      property.net,
      property.vnf_type,
      property.layer,
      property.intf,
      property.bit
    )
    name = property.id
    vnfnet = OSPFNetwork(name, property.net)
    self.addOSPFNet(vnfnet, "VNF")
    self.vnfs.append(vnf)
    self.nameToVNFs[name] = vnf
    return vnf

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
    endip = self.addEndIP(remote_ip)
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
  def addEndIP(self, remoteIP):
    name = self.newEndIPName()
    endip = EndIP(name, remoteIP, self.device_if)
    self.endips.append(endip)
    self.nameToEndIps[name] = endip
    return endip

  # Utility method to serialize all the taps
  def tapsSerialization(self):
    return "declare -a TAP=(" + " ".join("%s" % tap.name for tap in self.taps) + ")\n"

  # Utility method to serialize all the taps
  def ospfnetsSerialization(self):
    return "declare -a OSPFNET=(" + " ".join("%s" % net.name for net in self.ospfnets) + ")\n"

  # Utility method to serialize all the vnfs
  def vnfsSerialization(self):
    return "declare -a VNF=(" + " ".join("%s" % vnf.name for vnf in self.vnfs) + ")\n"

  # Utility method to serialize all the vnfs
  def termsSerialization(self):
    return "declare -a TER=(" + " ".join("%s" % term.name for term in self.terms) + ")\n"

  # Utility method to serialize all the vnfs
  def routesSerialization(self):
    return "declare -a STATIC_ROUTES=("  + self.static_routes + ")\n"

  # Create configuration file for the router
  def configure(self, params=[]):
    # Retrieve params
    testbed = params[0]
    tunneling = params[1]
    # Create the file and bash macro
    cfg = open('cfg/%s.cfg' % self.name,'w')
    cfg.write("#!/bin/bash\n")
    # Let's write the general options
    cfg.write("TESTBED=%s\n" % testbed)
    cfg.write("TUNNELING=%s\n" % tunneling)
    cfg.write("ROUTERPWD=srv6\n")
    cfg.write("ROUTERID=%s\n\n" % self.routerid)
    # Write the loopback
    cfg.write(self.loopback.serialize())

    # Write the tap information on the cfg
    cfg.write(self.tapsSerialization())
    for tap in self.taps:
      cfg.write(tap.serialize())

    # Write the endips
    for endip in self.endips:
      cfg.write(endip.serialize())

    cfg.write("\n")

    # Write the OSPF information on the cfg
    cfg.write(self.ospfnetsSerialization())
    for ospfnet in self.ospfnets:
      cfg.write(ospfnet.serialize())

    if len(self.vnfs) > 0:
      cfg.write("\n")
      # Write the VNF information on the cfg
      cfg.write(self.vnfsSerialization())
      for vnf in self.vnfs:
        cfg.write(vnf.serialize())

    if len(self.terms) > 0:
      cfg.write("\n")
      # Write the VNF information on the cfg
      cfg.write(self.termsSerialization())
      for term in self.terms:
        cfg.write(term.serialize())

    #if len(self.vnfs) > 0 or len(self.terms) > 0:
    cfg.write("\n")
    # Write the STA information on the cfg
    cfg.write(self.routesSerialization())
