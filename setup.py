#!/usr/bin/env python
"""The setup script."""

from setuptools import setup

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="call_detector",
    version="0.1.0",
    author="Gleb Sinyavskiy",
    author_email="zhulik.gleb@gmail.com",
    description="Detects if the user is an online call, publishes gathered information to an MQTT broker",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/zhulik/call_detector",
    license="The MIT License",
    install_requires=[
        "pulsectl-asyncio>=0.1.5",
        "gmqtt>=0.6.9",
        "minotaur>=0.0.4",
        "click>=8.0.0",
    ],
    entry_points={"console_scripts": ["call_watcher=call_watcher.__main__:main"]},
    packages=["call_detector"],
    package_dir={"call_detector": "call_detector"},
    include_package_data=True,
    zip_safe=True,
    keywords="home-automation,home-assistant,mqtt,pulseaudio,pipewire,camera",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Home Automation",
    ],
)
