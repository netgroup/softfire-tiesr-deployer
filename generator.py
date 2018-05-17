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
# Properties generator for Segment Routing IPv6
#
# @author Pier Luigi Ventre <pierventre@hotmail.com>
# @author Stefano Salsano <stefano.salsano@uniroma2.it>

from utils import *

DEFAULT_VNF_TERM_LAYER="L3"
DEFAULT_VNF_TERM_IF="eth0"
DEFAULT_VNF_TERM_BIT=32


# Encapsulate router properties
class RouterProperties(object):
  
  def __init__(self, loopback, routerid):
    self.loopback = loopback
    self.routerid = routerid

  def __str__(self):
    return "{'loopback':'%s/128', 'routerid': '%s'}" %(self.loopback, self.routerid)

# Encapsulate link properties used to build the testbed object in softfire-tiesr-deployer
class LinkProperties(object):

  def __init__(self, iplhs, iprhs, net):
    self.iplhs = iplhs
    self.iprhs = iprhs
    self.net = net

  def __str__(self):
    return "{'iplhs':'%s', 'iprhs':'%s', net':'%s'}" %(self.iplhs, self.iprhs, self.net)

# Encapsulate vnf properties used to build the testbed object in softfire-tiesr-deployer
# most properties are generated in getVNFsTERMsProperties
class VNF_TERM_Properties(object):

  #vnf_type = "lxd"
  #layer = "L3"
  #intf = "eth0"
  #bit = 32

  def __init__(self, myid, ip, via, br, net, vnf_type, layer, intf, bit):
    self.id = myid
    self.ip = ip
    self.via = via
    self.br = br
    self.net = net
    self.vnf_type = vnf_type
    self.layer = layer
    self.intf = intf
    self.bit = bit

  def __str__(self):
    return "{'type':'%s', 'id':'%s', 'ip':'%s', 'via':'%s', 'br':'%s', 'net':'%s', 'vnf_type':'%s', 'layer':'%s', 'intf:'%s', 'bit': '%s' }"  \
           %(self.vnf_type, self.myid, self.ip, self.via,   self.br, self.net, self.vnf_type,   self.layer, self.intf, self.bit)

# Encapsulate vnf properties
class TERProperties(object):

  #bit = 32
  #intf = "eth0"

  def __init__(self, ip, via, br, net, term_type, bit, intf):
    self.ip = ip
    self.via = via
    self.br = br
    self.net = net
    self.term_type = term_type
    self.bit = bit
    self.intf = intf

  def __str__(self):
    return "{'ip':'%s/%s', 'intf:'%s', 'via':'%s/%s', 'net':'%s', 'type':'%s'}"  \
    %(self.ip, self.bit, self.intf, self.via, self.bit, self.net, self.term_type)

# Generator of 
class PropertiesGenerator(object):

  def __init__(self):
    self.verbose = False
    self.loopbackAllocator = LoopbackAllocator()
    self.routerIdAllocator = RouterIdAllocator()
    self.netAllocator = NetAllocator()
    self.allocated = 1

  # Generater for router properties
  def getRoutersProperties(self, nodes):
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

  # Generator for vnf and term properties used to build the testbed object in softfire-tiesr-deployer
  # vnfs and terms is a list and not anymore an integer
  def getVNFsTERMsProperties(self, vnfs_and_terms):
    output_vnfs = []
    output_terms = []
    #if vnfs > 0 or terms > 0:
    allocator = VNFandTERMAllocator(self.allocated)
    self.allocated = self.allocated + 1

    i_vnf = 1
    i_term = 1
    #print vnfs_and_terms
    for vnf_or_term, value_dict in vnfs_and_terms.items() :
      if value_dict['type'] in ['ovnf_netns', 'ovnf_lxdcont'] :
        vnf_net = allocator.next_vnfNetAddress()
        hosts = vnf_net.hosts()

        ip = next(hosts).__str__()
        for j in range(0, 252):
          next(hosts)
        via = next(hosts).__str__()
        br = "br%s" % i_vnf
        i_vnf = i_vnf +1

        layer = value_dict.get('layer', DEFAULT_VNF_TERM_LAYER)
        intf = value_dict.get('intf', DEFAULT_VNF_TERM_IF)
        bit = value_dict.get('bit', DEFAULT_VNF_TERM_BIT)

        vnfproperties = VNF_TERM_Properties(vnf_or_term, ip, via, br, vnf_net.__str__(), value_dict['type'], layer, intf, bit)
        if self.verbose == True:      
          print vnfproperties
        output_vnfs.append(vnfproperties)


      elif value_dict['type'] in ['term_netns', 'term_lxdcont']:


        term_net = allocator.next_termNetAddress()
        hosts = term_net.hosts()

        ip = next(hosts).__str__()
        for j in range(0, 252):
          next(hosts)
        via = next(hosts).__str__()
        br = "br%s" % i_term
        i_term = i_term +1

        layer = value_dict.get('layer', DEFAULT_VNF_TERM_LAYER)
        intf = value_dict.get('intf', DEFAULT_VNF_TERM_IF)
        bit = value_dict.get('bit', DEFAULT_VNF_TERM_BIT)

        #termproperties = TERProperties(ip, via, br, term_net.__str__(), value_dict['type'], bit, intf)
        termproperties = VNF_TERM_Properties(vnf_or_term, ip, via, br, term_net.__str__(), value_dict['type'], layer, intf, bit)
        if self.verbose == True:      
          print termproperties
        output_terms.append(termproperties)

    return [output_vnfs, output_terms, allocator.net]


