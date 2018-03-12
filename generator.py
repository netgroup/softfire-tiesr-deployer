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

  def __init__(self, ip, via, br, net):
    self.ip = ip
    self.via = via
    self.br = br
    self.net = net

  def __str__(self):
    return "{'type':'%s', 'layer':'%s', 'via':'%s', 'bit': '%s', 'ip':'%s', 'intf:'%s', 'br':'%s', 'net':'%s'}"  \
    %(self.vnf_type, self.id, self.layer, self.via, self.bit, self.ip, self.intf, self.br, self.net)

# Encapsulate vnf properties
class TERProperties(object):

  bit = 32
  intf = "eth0"

  def __init__(self, ip, via, net):
    self.ip = ip
    self.via = via
    self.net = net

  def __str__(self):
    return "{'ip':'%s/%s', 'intf:'%s', 'via':'%s/%s', 'net':'%s'}"  \
    %(self.ip, self.bit, self.intf, self.via, self.bit, self.net)

# Generator of 
class PropertiesGenerator(object):

  def __init__(self):
    self.verbose = False
    self.loopbackAllocator = LoopbackAllocator()
    self.routerIdAllocator = RouterIdAllocator()
    self.netAllocator = NetAllocator()
    self.allocated = 1

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

  # Generator for vnf and term properties  
  def getVNFsTERMsProperties(self, vnfs, terms):
    output_vnfs = []
    output_terms = []
    if vnfs > 0 or terms > 0:
      allocator = VNFandTERMAllocator(self.allocated)
      self.allocated = self.allocated + 1

    for i in range(1, vnfs + 1):
      vnf_net = allocator.next_vnfNetAddress()
      hosts = vnf_net.hosts()

      ip = next(hosts).__str__()
      for j in range(0, 252):
        next(hosts)
      via = next(hosts).__str__()
      br = "br%s" % i

      vnfproperties = VNFProperties(ip, via, br, vnf_net.__str__())
      if self.verbose == True:      
        print vnfproperties
      output_vnfs.append(vnfproperties)

    for i in range(1, terms + 1):
      term_net = allocator.next_termNetAddress()
      hosts = term_net.hosts()

      ip = next(hosts).__str__()
      for j in range(0, 252):
        next(hosts)
      via = next(hosts).__str__()

      termproperties = TERProperties(ip, via, term_net.__str__())
      if self.verbose == True:      
        print termproperties
      output_terms.append(termproperties)

    return [output_vnfs, output_terms, allocator.net]


