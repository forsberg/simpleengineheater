from setuptools import setup, find_packages

setup(name="Simple Engine Heater Script",
      packages=find_packages(),
      version="0.7",
      install_requires=["requests", "pytz"],
      entry_points={
          "console_scripts": ["start-engineheater=simpleengineheater.cmd:start_engineheater"]}
      )
