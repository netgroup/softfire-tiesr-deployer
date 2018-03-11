#!/usr/bin/python

from utils import *

# Encapsulate router properties
class RouterProperties(object):
  
  def __init__(self, loopback, routerid):
    self.loopback = loopback
    self.routerid = routerid

  def __str__(self):
    return "{'loopback':'%s/128', 'routerid': '%s'}" %(self.loopback, self.routerid)

# Encapsulate link properties
class LinkProperties(object):

  def __init__(self, iplhs, iprhs, net):
    self.iplhs = iplhs
    self.iprhs = iprhs
    self.net = net

  def __str__(self):
    return "{'iplhs':'%s', 'iprhs':'%s', net':'%s'}" %(self.iplhs, self.iprhs, self.net)

# Encapsulate vnf properties
class VNFProperties(object):

  vnf_type = "lxd"
  layer = "L3"
  intf = "eth0"
  bit = 32

  def __init__(self, _id, ip, via, br):
    self.id = _id
    self.ip = ip
    self.via = via
    self.br = br

  def __str__(self):
    return "{'type':'%s', 'id': '%s', layer':'%s', 'via':'%s', 'bit': '%s', 'ip':'%s', 'intf:'%s', 'br':'%s'}"  \
    %(self.vnf_type, self.id, self.layer, self.via, self.bit, self.ip, self.intf, self.br)

# Encapsulate vnf properties
class TERProperties(object):

  bit = 32
  intf = "eth0"

  def __init__(self, ip, via):
    self.ip = ip
    self.via = via

  def __str__(self):
    return "{'ip':'%s/%s', 'intf:'%s', 'via':'%s/%s'}"  \
    %(self.ip, self.bit, self.intf, self.via, self.bit)

# Generator of 
class PropertiesGenerator(object):

  def __init__(self):
    self.verbose = False
    self.loopbackAllocator = LoopbackAllocator()
    self.routerIdAllocator = RouterIdAllocator()
    self.netAllocator = NetAllocator()
    self.vnfAllocator = VNFAllocator()
    self.terAllocator = TERAllocator()

  # Generater for router properties
  def getRouterProperties(self, nodes):
    output = []
    for node in nodes:
      if self.verbose == True:
        print node
      loopback = self.loopbackAllocator.next_hostAddress()
      routerid = self.routerIdAllocator.next_routerId()
      routerproperties = RouterProperties(loopback, routerid)
      if self.verbose == True:
        print routerproperties
      output.append(routerproperties)
    return output

  # Generator for link properties  
  def getLinksProperties(self, links):
    output = []
    net = self.netAllocator.next_netAddress()
    
    if self.verbose == True:    
      print net
    hosts = net.hosts()

    for link in links:
      if self.verbose == True:    
        print "(%s,%s)" % (link[0], link[1])
        
      iplhs = next(hosts).__str__()
      iprhs = next(hosts).__str__()
      ospf6net = net.__str__()

      linkproperties = LinkProperties(iplhs, iprhs, ospf6net)
      if self.verbose == True:      
        print linkproperties
      output.append(linkproperties)
    return output

  # Generator for vnf properties  
  def getVNFsProperties(self, vnfs):
    output = []
    net = self.vnfAllocator.next_netAddress()

    
    if self.verbose == True:    
      print net

    vnf_nets = net.subnets(new_prefix=48)
    if self.verbose == True:    
      print vnf_nets

    for i in range(1, vnfs+1):
      vnf_net = next(vnf_nets)
      hosts = vnf_net.hosts()

      _id = "vnf%d" % i
      ip = next(hosts).__str__()
      via = next(hosts).__str__()
      br = "br%s" % i

      vnfproperties = VNFProperties(_id, ip, via, br)
      if self.verbose == True:      
        print vnfproperties
      output.append(vnfproperties)
    return output

      # Generator for ter properties  
  def getTERsProperties(self, ters):
    output = []
    net = self.terAllocator.next_netAddress()

    
    if self.verbose == True:    
      print net

    ter_nets = net.subnets(new_prefix=48)
    if self.verbose == True:    
      print ter_nets

    for i in range(1, ters+1):
      ter_net = next(ter_nets)
      hosts = ter_net.hosts()

      ip = next(hosts).__str__()
      via = next(hosts).__str__()

      terproperties = TERProperties(ip, via)
      if self.verbose == True:      
        print terproperties
      output.append(terproperties)
    return output
