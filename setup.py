import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="solarlog-influx-sync",
    version="0.0.1",
    author="Michaël Dierick",
    author_email="michael@dierick.io",
    description="Sync SolarLog data to an influx database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "python_requires>=3.7",
        "pytz",
        "influxdb>=5.2.2",
        "pip >= 19.0.0"
        "solarlog-csv @ git+https://github.com/MikiDi/solarlog-csv.git@master",
    ],
    scripts=['solarlog_influx_sync/solarlog_influx_sync'],
     url="https://github.com/MikiDi/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
