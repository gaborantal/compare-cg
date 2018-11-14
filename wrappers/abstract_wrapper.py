import abc
import contextlib
import os
import pathlib
import subprocess

@contextlib.contextmanager
def cd(new_dir):
    cwd = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(cwd)


class AbstractWrapper(object):
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.results = []

    def get_results(self):
        return self.results

    @abc.abstractmethod
    def run_command(self, input_directory):
        pass

    def change_directory(self):
        return None

    def pre_analyze(self, inp):
        if not os.path.exists(os.path.join(self.config.results_dir, self.name)):
            os.makedirs(os.path.join(self.config.results_dir, self.name))

    def post_analyze(self, inp):
        pass

    def run(self, input_directory):
        new_dir = os.getcwd()
        if self.change_directory():
            new_dir = self.change_directory()
        inputs = [input_directory]
        if self.config.individual_files:
            inputs = pathlib.Path(input_directory).glob('*.%s' % self.config.file_ext)
            inputs = [str(i) for i in list(inputs)]
        with cd(new_dir):
            status = 0
            for inp in inputs:
                self.pre_analyze(inp)
                try:
                    co = subprocess.run(self.run_command(str(inp)), check=True, shell=True)
                    status = status | co.returncode
                    self.post_analyze(inp)
                except Exception as ex:
                    print(ex)
                    print("Analysis failed!")
            return status
