import os
import sys
import platform
import subprocess

import pybind11
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPython_EXECUTABLE=' + sys.executable,
                      '-Dpybind11_DIR=' + pybind11.get_cmake_dir(),
                      '-DPYBIND11_FINDPYTHON=ON',
                      '-DVERSION="' + self.distribution.get_version() + '"']

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.', '--target', 'cityflow'] + build_args, cwd=self.build_temp)


setup(
    name='CityFlow',
    version='0.1',
    author='Huichu Zhang',
    author_email='zhc@apex.sjtu.edu.cn',
    description='CityFlow: A Multi-Agent Reinforcement Learning Environment for Large Scale City Traffic Scenario',
    long_description='',
    ext_modules=[CMakeExtension('cityflow')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False
)
