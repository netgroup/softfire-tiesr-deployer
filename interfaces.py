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
# Interface objects for Segment Routing IPv6
#
# @author Pier Luigi Ventre <pierventre@hotmail.com>
# @author Stefano Salsano <stefano.salsano@uniroma2.it>

# Generic interface object
class Intf:
  
  def __init__(self, name):
    self.name = name

# Loopback interface
class LoIntf(Intf):
  
  def __init__(self, ip, name="LOOPBACK", netbit=128, hello_int=2, cost=1):
    Intf.__init__(self,name)
    self.ip = ip
    self.netbit = netbit
    self.hello_int = hello_int
    self.cost = cost
  
  def serialize(self):
    return "declare -a %s=(%s/%s %s %s LBN)\n" %(self.name, self.ip, self.netbit, self.cost, self.hello_int)

  def __str__(self):
    return "{'name':'%s', 'ip':'%s', 'netbit':'%s', 'hello_int':'%s', 'cost':'%s'}" \
    % (self.name, self.ip, self.netbit, self.cost, self.hello_int)

# Generic tap interface object
class TapIntf(Intf):
  def __init__(self, name, endipname, ip, net):
    Intf.__init__(self,name)
    self.endipname = endipname
    self.ip = ip
    self.net = net
  
  def serialize(self):
    raise NotImplementedError("Abstract Method")
  
  def __str__(self):
    return "{'name':'%s', 'endip':'%s', 'ip':'%s/%s', 'net':'%s'}" \
    % (self.name, self.endipname, self.ip, self.net.netbitOSPF, self.net)

# OpenVPN tap interface for SRv6Router
class TapOpenVPNIntf(TapIntf):
  
  def __init__(self, name, localport, remoteport, endipname, ip, net):
    TapIntf.__init__(self, name, endipname, ip, net)
    self.localport = localport
    self.remoteport = remoteport
  
  def serialize(self):
    return "declare -a %s=(%s %s %s %s/%s %s %s %s)\n" \
    % (self.name, self.localport, self.remoteport, self.endipname, self.ip, self.net.netbitOSPF, self.net.hello_int, self.net.cost, self.net.name)
  
  def __str__(self):
    return "{'name':'%s', 'localport':'%s', 'remoteport':'%s', 'endip':'%s', 'ip':'%s/%s', 'net':'%s'}" \
    % (self.name, self.localport, self.remoteport, self.endipname, self.ip, self.net.netbitOSPF, self.net)

# VXLAN tap interface for SRv6Router
class TapVXLANIntf(TapIntf):
  
  def __init__(self, name, vni, endipname, ip, net):
    TapIntf.__init__(self, name, endipname, ip, net)
    self.vni = vni
  
  def serialize(self):
    return "declare -a %s=(%s %s %s/%s %s %s %s)\n" \
    % (self.name, self.vni, self.endipname, self.ip, self.net.netbitOSPF, self.net.hello_int, self.net.cost, self.net.name)
  
  def __str__(self):
    return "{'name':'%s', 'vni':'%s', 'endip':'%s', 'ip':'%s/%s', 'net':'%s'}" \
    % (self.name, self.vni, self.endipname, self.ip, self.net.netbitOSPF, self.net)







