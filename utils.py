import copy
import json
import os
import re
import glob


CNT = 1

FILTER = re.compile(r".*:.*:.* -> .*:.*:.*")
NODE_POS = re.compile(r".*\.js\[(.*)\]$")

def create_schema():
    json_graph = {
        "directed": True,
        "multigraph": False,
        "nodes": list(),
        "links": list()
    }

    return copy.deepcopy(json_graph)


def add_node(j, label, pos, entry=False, final=True):
    for node in j.get("nodes"):
        if node.get("pos") == pos:
            return
    global CNT

    if pos == "GUESS":
        pos_match = NODE_POS.match(label)
        pos = pos_match.group(1)

    j.get("nodes").append({"id": CNT, "label": label, "pos": pos, "entry": entry, "final": final})
    CNT += 1

def add_link(j, from_name, to_name, nomod=False):
    target_id = 0
    source_id = 0
    for node in j.get("nodes"):
        if node.get("pos") == from_name:
            source_id = node.get("id")
            node["final"] = False
        if node.get("pos") == to_name:
            target_id = node.get("id")
    if nomod:
        label = from_name + "->" + to_name
    else:
        label = ':'.join(from_name.split(':')[:-2]) + '@' + (from_name.split(':')[-2] if not from_name.startswith('toplevel') else '[toplevel]') + " -> " + ':'.join(to_name.split(':')[:-2]) + '@' + (to_name.split(':')[-2] if not to_name.startswith('toplevel') else '[toplevel]')
    j.get("links").append({"target": target_id, "source": source_id, "label": label})

