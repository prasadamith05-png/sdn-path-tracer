import networkx as nx
import random

# -------------------------------
# TOPOLOGY
# -------------------------------
class SDNTopology:
    def __init__(self):
        self.G = nx.Graph()
        self.build()

    def build(self):
        G = self.G

        # Hosts
        hosts = ['H1','H2','H3','H4','H5']
        for h in hosts:
            G.add_node(h, type='host')

        # Switches
        switches = ['S1','S2','S3','S4','S5']
        for s in switches:
            G.add_node(s, type='switch')

        # Links
        links = [
            ('H1','S1'), ('H2','S2'),
            ('S1','S3'), ('S2','S3'),
            ('S2','S4'), ('S3','S4'),
            ('S3','H3'), ('S4','H4'),
            ('S4','S5'), ('S5','H5')
        ]

        for u, v in links:
            G.add_edge(u, v)

        self.update_weights()

    def update_weights(self):
        # Dynamic latency simulation
        for u, v in self.G.edges():
            self.G[u][v]['weight'] = random.randint(1, 10)

# -------------------------------
# FLOW TABLE (Dynamic Learning)
# -------------------------------
class FlowTable:
    def __init__(self):
        self.rules = {}

    def learn_rule(self, switch, dest, next_hop):
        if switch not in self.rules:
            self.rules[switch] = {}
        self.rules[switch][dest] = next_hop

    def get_action(self, switch, dest):
        return self.rules.get(switch, {}).get(dest, "FLOOD")

    def show(self):
        print("\n=== FLOW TABLE ===")
        if not self.rules:
            print("No learned rules yet\n")
            return

        for sw, rules in self.rules.items():
            print(f"{sw}:")
            for dest, action in rules.items():
                print(f"  if dest={dest} → forward to {action}")
            print()

# -------------------------------
# LINK FAILURE
# -------------------------------
def simulate_link_failure(topo):
    edges = list(topo.G.edges())
    if not edges:
        return

    u, v = random.choice(edges)
    topo.G.remove_edge(u, v)
    print(f"\n[!] Link failure simulated between {u} and {v}\n")

# -------------------------------
# PATH TRACING
# -------------------------------
def trace_path(topo, flow_table, src, dst):
    topo.update_weights()  # dynamic condition

    print("\n=== SDN PATH TRACING ===")

    try:
        path = nx.dijkstra_path(topo.G, src, dst)
        cost = nx.dijkstra_path_length(topo.G, src, dst)
    except:
        print("No path found (network failure)")
        return

    print(f"\nSelected Path: {' -> '.join(path)}")
    print(f"Total Cost (Latency): {cost}\n")

    print("Forwarding Decisions:\n")

    for i in range(len(path)-1):
        node = path[i]
        next_node = path[i+1]

        if topo.G.nodes[node]['type'] == 'switch':
            # learn flow rule dynamically
            flow_table.learn_rule(node, dst, next_node)

            print(f"[Switch {node}]")
            print(f"  Flow Rule Applied: if dest={dst} → output:{next_node}")
            print(f"  Next Hop: {next_node}\n")

        else:
            print(f"[Host {node}] sends packet\n")

    print(f"[Host {dst}] receives packet\n")
    print(f"Summary: Packet delivered from {src} to {dst}\n")

# -------------------------------
# MAIN MENU
# -------------------------------
def main():
    topo = SDNTopology()
    flow_table = FlowTable()

    while True:
        print("\n====== SDN PATH TRACER (ADVANCED) ======")
        print("1. Trace Path")
        print("2. Show Flow Table")
        print("3. Simulate Link Failure")
        print("4. Exit")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            print("\nAvailable Hosts: H1, H2, H3, H4, H5")
            src = input("Enter source host: ").strip().upper()
            dst = input("Enter destination host: ").strip().upper()

            if src == dst:
                print("Source and destination cannot be same")
                continue

            trace_path(topo, flow_table, src, dst)

        elif choice == '2':
            flow_table.show()

        elif choice == '3':
            simulate_link_failure(topo)

        elif choice == '4':
            print("Exiting...")
            break

        else:
            print("Invalid choice")

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    main()
