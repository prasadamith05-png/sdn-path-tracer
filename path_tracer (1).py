"""
path_tracer.py — Ryu SDN Controller for Path Tracing
Course : UE24CS252B — Computer Networks
Project: SDN Path Tracing Tool

Description:
    A Ryu OpenFlow 1.3 controller that implements a learning switch
    with path tracing. It handles packet_in events, installs flow
    rules, and logs the forwarding path for each packet.

Usage:
    ryu-manager path_tracer.py --observe-links

Requirements:
    pip install ryu
    sudo apt install mininet openvswitch-switch -y
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, icmp, arp
from ryu.lib import mac
import logging

LOG = logging.getLogger('path_tracer')
LOG.setLevel(logging.DEBUG)


class PathTracerController(app_manager.RyuApp):
    """
    Learning switch controller with path tracing.

    For each packet_in event:
      1. Learn the source MAC → port mapping on that switch.
      2. Look up the destination MAC in the table.
      3. If known, install a flow rule and forward; log the path.
      4. If unknown, flood and wait for the reply to complete the learning.
    """

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PathTracerController, self).__init__(*args, **kwargs)
        # mac_to_port[dpid][mac] = port_number
        self.mac_to_port = {}
        # path_log stores traced paths as list of (dpid, in_port, out_port)
        self.path_log = []

    # ------------------------------------------------------------------
    # Switch handshake: install a table-miss flow entry
    # ------------------------------------------------------------------
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto  = datapath.ofproto
        parser   = datapath.ofproto_parser

        # Table-miss: send everything to controller
        match  = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self._add_flow(datapath, priority=0, match=match, actions=actions)
        LOG.info('[s%s] Connected — table-miss entry installed', datapath.id)

    # ------------------------------------------------------------------
    # Packet-in handler
    # ------------------------------------------------------------------
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg      = ev.msg
        datapath = msg.datapath
        ofproto  = datapath.ofproto
        parser   = datapath.ofproto_parser
        dpid     = datapath.id
        in_port  = msg.match['in_port']

        pkt     = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        if eth_pkt is None:
            return

        dst_mac = eth_pkt.dst
        src_mac = eth_pkt.src

        # ---- 1. Learn source MAC ----
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src_mac] = in_port

        # ---- 2. Determine output port ----
        if dst_mac in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst_mac]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # ---- 3. Log the path hop ----
        ip_pkt   = pkt.get_protocol(ipv4.ipv4)
        icmp_pkt = pkt.get_protocol(icmp.icmp)
        arp_pkt  = pkt.get_protocol(arp.arp)

        proto_str = 'ETH'
        if ip_pkt:
            proto_str = 'IPv4'
            if icmp_pkt:
                proto_str = 'ICMP'
        elif arp_pkt:
            proto_str = 'ARP'

        LOG.info(
            '[PATH] dpid=s%s  in_port=%s  src=%s  dst=%s  proto=%s  '
            'out_port=%s',
            dpid, in_port, src_mac, dst_mac, proto_str,
            out_port if out_port != ofproto.OFPP_FLOOD else 'FLOOD'
        )

        self.path_log.append({
            'dpid':     dpid,
            'in_port':  in_port,
            'out_port': out_port,
            'src_mac':  src_mac,
            'dst_mac':  dst_mac,
            'proto':    proto_str,
        })

        # ---- 4. Install flow rule (skip for floods) ----
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst_mac,
                                    eth_src=src_mac)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self._add_flow(datapath, priority=10, match=match,
                               actions=actions,
                               buffer_id=msg.buffer_id)
                return
            else:
                self._add_flow(datapath, priority=10, match=match,
                               actions=actions)

        # ---- 5. Send packet out ----
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data
        )
        datapath.send_msg(out)

    # ------------------------------------------------------------------
    # Helper: add a flow entry
    # ------------------------------------------------------------------
    def _add_flow(self, datapath, priority, match, actions,
                  buffer_id=None, idle_timeout=20, hard_timeout=0):
        ofproto = datapath.ofproto
        parser  = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]

        kwargs = dict(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout,
        )
        if buffer_id and buffer_id != ofproto.OFP_NO_BUFFER:
            kwargs['buffer_id'] = buffer_id

        mod = parser.OFPFlowMod(**kwargs)
        datapath.send_msg(mod)
        LOG.debug('[s%s] Flow installed  priority=%s  match=%s  actions=%s',
                  datapath.id, priority, match, actions)

    # ------------------------------------------------------------------
    # Print path summary (call from Ryu REST or test)
    # ------------------------------------------------------------------
    def get_path_summary(self):
        if not self.path_log:
            return 'No packets traced yet.'
        lines = ['--- PATH TRACE SUMMARY ---']
        for i, hop in enumerate(self.path_log[-10:], 1):   # last 10 hops
            lines.append(
                f"  Hop {i:02d}: s{hop['dpid']}  "
                f"in={hop['in_port']} out="
                f"{'FLOOD' if isinstance(hop['out_port'], int) and hop['out_port'] > 0xfff0 else hop['out_port']}"
                f"  [{hop['proto']}]  {hop['src_mac']} → {hop['dst_mac']}"
            )
        lines.append('--------------------------')
        return '\n'.join(lines)
