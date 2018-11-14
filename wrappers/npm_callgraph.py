import os
import shutil
import json
import re
import utils
import wrappers.abstract_wrapper as abstract_wrapper

NPM_CG_EDGEREGEX = re.compile(r".* -> .*")


class NpmCallGraphWrapper(abstract_wrapper.AbstractWrapper):

    def __init__(self, config):
        super(NpmCallGraphWrapper, self).__init__("npm-callgraph", config)

    def run_command(self, inp):
        return ["node",  "node_modules\callgraph\index.js", inp]

    def change_directory(self):
        return r"D:\work\callgraph-comparator\tmp"

    def _convert(self, out):
        edges = set()
        j = utils.create_schema()
        with open(out, "r") as fp:
            lines = fp.readlines()
        for line in lines:
            if NPM_CG_EDGEREGEX.match(line):
                line = line.strip()
                line = line.replace('"', '')
                c = line.split("->")
                src = c[0].strip()
                tgt = c[1].strip()
                if src + "->" + tgt in edges:
                    continue
                utils.add_node(j, src, src + ":0:0")
                utils.add_node(j, tgt, tgt + ":0:0")
                utils.add_link(j, src, tgt, True)
                edges.add(src + "->" + tgt)

        with open(os.path.join(os.path.join(self.config.results_dir, self.name), "output_" + os.path.basename(out).replace('.dot', '.json')), 'w') as fp:
            json.dump(j, fp, indent=2)

    def post_analyze(self, out):
        new_filename = os.path.basename(out).replace(".js", ".dot")
        shutil.move("callgraph.dot", new_filename)
        self._convert(new_filename)
