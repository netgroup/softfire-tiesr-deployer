#!/usr/bin/python

from ipaddress import IPv6Network, IPv4Network

import ipaddress
import sys
import re

# Store and endip object
class EndIP:

  def __init__(self, name, remoteIP, localIntf):
    self.name = name
    self.remoteIP = remoteIP
    self.localIntf = localIntf

  def serialize(self):
    return "declare -a %s=(%s %s)\n" %(self.name, self.remoteIP, self.localIntf)

  def __str__(self):
          return "{'name':'%s', 'endip':'%s' 'localintf':'%s'}" %(self.name, self.remoteIP, self.localIntf)

# Store an OSPF network
class OSPFNetwork:
 
  def __init__(self, name, net, cost=1, hello_int=5, area="0.0.0.0"):

    self.net = net
    data = net.split("/")
    self.netbitOSPF = int(data[1])
    self.subnet = []
    self.cost = cost
    self.hello_int = hello_int
    self.area = area
    self.name = name

  def serialize(self):
    return "declare -a %s=(%s %s)\n" %(self.name, self.net, self.area)
  
  def __str__(self):
    return "{'name':'%s', 'net':'%s', 'area':'%s'}" %(self.name, self.net, self.area)

# Allocates loopbacks
class LoopbackAllocator(object):

  bit = 64
  net = unicode("fdff::/%d" % bit)

  def __init__(self): 
    print "*** Calculating Available Loopback Addresses"
    self.loopbacknet = (IPv6Network(self.net)).hosts()
  
  def next_hostAddress(self):
    n_host = next(self.loopbacknet)
    return n_host.__str__()

# Allocates router ids
class RouterIdAllocator(object):

  bit = 0
  _id = unicode("0.0.0.0/%d" % bit)

  def __init__(self): 
    print "*** Calculating Available Router Ids"
    self.router_id = (IPv4Network(self._id)).hosts()
  
  def next_routerId(self):
    n_id = next(self.router_id)
    return n_id.__str__()

# Allocates subnets for the links
class NetAllocator(object):

  bit = 16
  net = unicode("fdf0::/%s" % bit) 
  
  def __init__(self):
    print "*** Calculating Available IP Networks"
    self.ipv6net = (IPv6Network(self.net)).subnets(new_prefix=64)
  
  def next_netAddress(self):
    n_net = next(self.ipv6net)
    return n_net

# Allocates subnets for the vnfs
class VNFAllocator(object):

  bit = 16
  net = unicode("fd00::/%s" % bit) 
  
  def __init__(self):
    print "*** Calculating Available VNFs Networks"
    self.ipv6net = (IPv6Network(self.net)).subnets(new_prefix=32)
  
  def next_netAddress(self):
    n_net = next(self.ipv6net)
    return n_net

# Allocates subnets for the ters
class TERAllocator(object):

  bit = 16
  net = unicode("fd01::/%s" % bit) 
  
  def __init__(self):
    print "*** Calculating Available TERs Networks"
    self.ipv6net = (IPv6Network(self.net)).subnets(new_prefix=32)
  
  def next_netAddress(self):
    n_net = next(self.ipv6net)
    return n_net
