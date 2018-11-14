import os
import time

import comparator

import wrappers.npm_callgraph as npm_cg
import wrappers.tajs as tajs


dir_tool_map = {
    r'tmp/results/acg-results': 'acg',
    r'tmp/results/closure-results': 'closure',
    r'tmp/results/npm-callgraph-results': 'npm-cg',
    r'tmp/results/wala-results': 'wala',
    r'tmp/results/tajs-results': 'tajs'
}


out_dir = r'tmp/results/compared'

config = {
    "file_ext": "js",
    "results_dir": os.path.abspath("new_results"),
    "individual_files": True
}

class Config(object):
    def __init__(self, cfg):
        self.config = cfg

    def __getattr__(self, name):
        return self.config[name]

conf = Config(config)

mapping = dict()
tool_list = list()

def init_tool(tool_class):
    # global tool_list
    # global mapping
    # global conf
    tool = tool_class(conf)
    tool_list.append(tool)
    mapping[os.path.join(conf.results_dir, tool.name)] = tool.name


def setup():
    #init_tool(npm_cg.NpmCallGraphWrapper)
    init_tool(tajs.TajsWrapper)

    # tool = npm_cg.NpmCallGraphWrapper(conf)
    # tool.run(os.path.abspath(os.path.join("tmp2", "sources")))
    print(tool_list)
    print(mapping)

def main():
    start = time.time()
    setup()
    print("# Started wrappers")
    for tool in tool_list:
        tool.run(os.path.abspath(os.path.join("tmp2", "sources")))
    print("# Finished")
    print("# Started conversion")
    print("# Finished")
    print("# Started comparing")
    comparator.compare(dir_tool_map, out_dir)
    print("# Finished")
    end = time.time()
    print(end - start, "seconds")

if __name__ == '__main__':
    main()
