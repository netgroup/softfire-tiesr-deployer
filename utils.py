#!/usr/bin/python

##############################################################################################
# Copyright (C) 2018 Pier Luigi Ventre - (CNIT and University of Rome "Tor Vergata")
# Copyright (C) 2018 Stefano Salsano - (CNIT and University of Rome "Tor Vergata")
# www.uniroma2.it/netgroup - www.cnit.it
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Utils for Segment Routing IPv6
#
# @author Pier Luigi Ventre <pierventre@hotmail.com>
# @author Stefano Salsano <stefano.salsano@uniroma2.it>

from ipaddress import IPv6Network, IPv4Network

import ipaddress
import sys
import re

# Store and endip object
class EndIP(object):

  def __init__(self, name, remoteIP, localIntf):
    self.name = name
    self.remoteIP = remoteIP
    self.localIntf = localIntf

  def serialize(self):
    return "declare -a %s=(%s %s)\n" %(self.name, self.remoteIP, self.localIntf)

  def __str__(self):
          return "{'name':'%s', 'endip':'%s' 'localintf':'%s'}" %(self.name, self.remoteIP, self.localIntf)

# Store an OSPF network
class OSPFNetwork(object):
 
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

# VNF and its interfaces toward the SRv6 router node used in nodes.py
class VNF_TERM_data(object):

  #TODO we should NOT set these properties again!!
  #vnf_type = "lxd"
  #layer = "L3"
  #intf = "eth0"
  #bit = 32
  
  def __init__(self, name, ip, via, br, net, mytype, layer, intf, bit):
    self.name = name
    self.id = name.lower()
    self.ip = ip
    self.via = via
    self.br = br
    self.net = net
    self.vnf_type = mytype
    self.layer = layer
    self.intf = intf
    self.bit = bit

  
  def serialize(self):

    output_type = 'unknown'
    if self.vnf_type == 'ovnf_lxdcont' :
      output_type = 'lxd'
    elif self.vnf_type == 'ovnf_netns' :
      output_type = 'netns'
    elif self.vnf_type == 'term_lxdcont' : 
      output_type = 'lxd'
    elif self.vnf_type == 'term_netns' :
      output_type = 'netns'

    print "***************", self.name
    serialize = "declare -a %s=(%s %s %s_DEV)\n" \
    % (self.name, output_type, self.id, self.name)
    serialize = serialize + "declare -a %s_DEV=(%s_DEV1)\n" \
    % (self.name, self.name)
    serialize = serialize + "declare -a %s_DEV1=(%s %s %s %s %s %s)\n" \
    % (self.name, self.layer, self.via, self.bit, self.ip, self.intf, self.br)
    return serialize

  def __str__(self):
    return "{'name':'%s', type':'%s', 'id': '%s', layer':'%s', 'via':'%s', 'bit': '%s', 'ip':'%s', 'intf:'%s', 'br':'%s'}"  \
    %(self.name, self.vnf_type, self.id, self.layer, self.via, self.bit, self.ip, self.intf, self.br)


# TERM and its interfaces toward the SRv6 router node used in nodes.py
class TERM(object):

  intf = "eth0"
  bit = 32
  
  def __init__(self, name, ip, via, br, net, mytype, layer, intf, bit):
    self.name = name
    self.ip = ip
    self.via = via
    self.net = net
  
  def serialize(self):
    return "declare -a %s=(%s/%s %s %s/%s)\n" \
    % (self.name, self.ip, self.bit, self.intf, self.via, self.bit)

  def __str__(self):
    return "{'name':'%s', 'ip':'%s/%s', 'intf:'%s', 'via':'%s/%s'}"  \
    %(self.name, self.ip, self.bit, self.intf, self.via, self.bit)

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

# Allocates subnets for the ters
class VNFandTERMAllocator(object):

  bit = 16
  
  def __init__(self, base):
    hex_string = format(base, '#04x')
    hex_string = hex_string[2:]
    self.net = unicode("fd%s::/%s" % (hex_string, self.bit))

    print "*** Calculating Available VNFs Networks"
    self.vnf_net = (IPv6Network(self.net)).subnets(new_prefix=32)
    for i in range(0, 241):
      next(self.vnf_net)

    print "*** Calculating Available TERMs Networks"
    self.term_net = (IPv6Network(self.net)).subnets(new_prefix=32)
    next(self.term_net)

  def next_vnfNetAddress(self):
    n_net = next(self.vnf_net)
    return n_net

  def next_termNetAddress(self):
    n_net = next(self.term_net)
    return n_net
