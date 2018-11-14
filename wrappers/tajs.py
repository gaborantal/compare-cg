import os
import shutil
import json
import re
import utils
import glob
import wrappers.abstract_wrapper as abstract_wrapper

EDGEREGEX = re.compile(r".* -> .*")

NODEREGEX = re.compile(r".* \[.*\]")

class TajsWrapper(abstract_wrapper.AbstractWrapper):

    def __init__(self, config):
        super(TajsWrapper, self).__init__("tajs", config)

    def run_command(self, inp):
        return ["java", "-jar", "tajs-all-old.jar", "-callgraph", inp]

    def change_directory(self):
        return r"D:\work\callgraph-comparator\tmp"

    def _convert(self):
        nodes = {}
        for f in glob.glob(os.path.join("out", "*.dot")):
            edges = set()
            j = utils.create_schema()
            with open(f, "r") as fp:
                lines = fp.readlines()

            for line in lines:
                if NODEREGEX.match(line) and ("HOST" not in line):
                    node = {
                        "file": None,
                        "line": None,
                        "column": None
                    }
                    matches = re.compile(r"(?P<alias>f\d+).*label=\"(?P<label>.*)\"")
                    search = matches.search(line)
                    alias = search.group('alias')

                    label = search.group('label')
                    if label == "<main>":
                        node["file"] = "toplevel"
                        node["line"] = '1'
                        node["column"] = '1'
                        nodes[alias] = node
                        continue
                    c = label.split("\\n")
                    s = c[1].split(":")
                    node["line"] = s[1]
                    node["column"] = s[2]

                    detect_function = re.compile(r".*\((?P<filename>.*)\).*")
                    search_function = detect_function.search(s[0])
                    if search_function is not None:
                        node["file"] = os.path.basename(search_function.group('filename'))
                    else:
                        node["file"] = os.path.basename(s[0])
                    nodes[alias] = node
                    continue

            for line in lines:
                if EDGEREGEX.match(line):
                    line = line.strip()
                    line = line.replace('"', '')
                    c = line.split("->")
                    src = c[0].strip()
                    tgt = c[1].strip()
                    if src + "->" + tgt in edges:
                        continue
                    if src not in nodes.keys() or tgt not in nodes.keys():
                        continue
                    node_src = nodes.get(src)
                    utils.add_node(j, node_src.get("file")+"@"+node_src.get("line") if node_src.get("file") != "toplevel" else "[toplevel]", node_src.get("file") + ":"+node_src.get("line")+":"+node_src.get("column"))
                    node_tgt = nodes.get(tgt)
                    utils.add_node(j, node_tgt.get("file")+"@"+node_tgt.get("line") if node_tgt.get("file") != "toplevel" else "[toplevel]", node_tgt.get("file") + ":"+node_tgt.get("line")+":"+node_tgt.get("column"))
                    utils.add_link(j, node_src.get("file") + ":" + node_src.get("line") + ":" + node_src.get("column"), node_tgt.get("file") + ":" + node_tgt.get("line") + ":" + node_tgt.get("column"), False)
                    edges.add(src + "->" + tgt)

            with open(os.path.join(self.config.results_dir, self.name, "output_"+os.path.basename(f).replace('.dot', '.json')), 'w') as fp:
                json.dump(j, fp, indent=2)

    def post_analyze(self, out):
        new_filename = os.path.basename(out).replace(".js", ".dot")
        shutil.move(os.path.join("out", "callgraph.dot"), os.path.join("out", new_filename))
        self._convert()



