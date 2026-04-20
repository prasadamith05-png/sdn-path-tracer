from mininet.net import Mininet
from mininet.node import RemoteController
from topology import MyTopo

topo = MyTopo()
net = Mininet(topo=topo, controller=RemoteController)

net.start()
print("Network started")

net.pingAll()

net.interact()

net.stop()