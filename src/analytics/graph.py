import networkx as nx
from typing import List, Dict

def build_ip_graph(events: List[Dict]) -> nx.Graph:
    G = nx.Graph()
    for e in events:
        user = e.get("user_id")
        ip = e.get("ip")
        if not user or not ip:
            continue
        G.add_node(user, kind="user")
        G.add_node(ip, kind="ip")
        G.add_edge(user, ip)
    return G

def suspicious_components(G: nx.Graph, min_degree: int = 5):
    comps = []
    for comp in nx.connected_components(G):
        H = G.subgraph(comp)
        maxdeg = max(dict(H.degree()).values())
        if maxdeg >= min_degree:
            comps.append(H)
    return comps
