from setuptools import setup, find_packages

setup(name="Simple Engine Heater Script",
      packages=find_packages(),
      version="0.3",
      install_requires=["requests"],
      entry_points={
          "console_scripts": ["start_engineheater=simpleengineheater.cmd:start_engineheater"]}
      )
