#!/usr/bin/python

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







