import json
import os
import utils



def compare(dir_tool_map, out_dir):
    data_container = {}

    for tool_dir in dir_tool_map.keys():
        for file in os.listdir(tool_dir):
            if file.endswith(".json"):
                data = json.load(open(os.path.join(tool_dir, file)))
                if file not in data_container.keys():
                    data_container[file] = {}
                data_container[file][dir_tool_map[tool_dir]] = data

    for jsn in data_container.keys():
        edges = set()
        nodes = set()
        raw_nodes = {}
        raw_edges = {}
        node_map = {}
        for tool in data_container[jsn].keys():
            for node in data_container[jsn][tool]['nodes']:
                if node['pos'] in nodes:
                    raw_nodes[node['pos']]['foundBy'].append(tool)
                else:
                    nodes.add(node['pos'])
                    raw_nodes[node['pos']] = node
                    raw_nodes[node['pos']]['foundBy'] = [tool]

        for tool in data_container[jsn].keys():
            for link in data_container[jsn][tool]['links']:
                link_src = link['source']
                link_tgt = link['target']
                src_pos = None
                tgt_pos = None
                for node in data_container[jsn][tool]['nodes']:
                    if node['id'] == link_src:
                        src_pos = node['pos']
                    if node['id'] == link_tgt:
                        tgt_pos = node['pos']
                if src_pos is None or tgt_pos is None:
                    print('DEAD: ' + jsn + '(' + tool + ')' ', ' + str(link_src) + ' -> ' + str(link_tgt))
                    continue
                link_id = src_pos + "->" + tgt_pos
                if link_id in edges:
                    raw_edges[link_id]['foundBy'].append(tool)
                else:
                    edges.add(link_id)
                    raw_edges[link_id] = link
                    raw_edges[link_id]['label'] = link_id
                    raw_edges[link_id]['foundBy'] = [tool]

        with open(os.path.join(out_dir, jsn), "w") as fp:
            j = utils.create_schema()
            cnt = 1
            for k in raw_nodes.keys():
                raw_nodes[k]['id'] = cnt
                cnt += 1
                node_map[raw_nodes[k]['pos']] = raw_nodes[k]['id']
                j['nodes'].append(raw_nodes[k])
            for k in raw_edges.keys():
                ends = raw_edges[k]['label'].split('->')
                raw_edges[k]['source'] = node_map[ends[0]]
                raw_edges[k]['target'] = node_map[ends[1]]
                j['links'].append(raw_edges[k])
            json.dump(j, fp, indent=2)
