#!/bin/env python3


import os
import json
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Context:
    install_path: str
    java_path: str
    screen_name: str
    active_instance: str
    instances: dict


@dataclass
class RemoteFile:
    src: str
    sha: str
    filename: str


@dataclass
class Java(RemoteFile):
    name: str


@dataclass
class Instance:
    name: str
    version: str
    server: RemoteFile
    forge: Optional[RemoteFile]
    world: Optional[str]
    command: str
    java: Java
    mods: List[RemoteFile]


def load_json(filename):
    return json.load(
        open(os.path.join(os.path.dirname(__file__), "server", filename)))


def context():
    config = load_json("config.json")

    ctx = Context(
        install_path=config["installPath"],
        java_path=config["javaPath"],
        screen_name=config["screenName"],
        active_instance=config["activeInstance"],
        instances=config["instances"])

    return ctx


def instance(name: str) -> Instance:
    ctx = context()
    versions = load_json("versions.json")
    mod_versions = load_json("mods.json")

    assert name in ctx.instances, f"instance {name} not found in config.json"
    instance = ctx.instances[name]

    version = versions[instance["version"]]
    available_mods = mod_versions[instance["version"]]
    
    forge, mods = None, []
    if instance["forge"]:
        forge = RemoteFile(
            src=version["forge"]["src"],
            sha=version["forge"]["sha"],
            filename=version["forge"]["filename"],)
        
        for mod in instance["mods"]:
            assert mod in available_mods, \
                f"mod {mod} not present in mods.json for {instance['version']}"
            
            mods.append(
                RemoteFile(
                    src=available_mods[mod]["src"],
                    sha=available_mods[mod]["sha"],
                    filename=available_mods[mod]["filename"]))
    
    server = RemoteFile(
        src=version["server"]["src"],
        sha=version["server"]["sha"],
        filename=version["server"]["filename"])

    java = Java(
        src=version["java"]["src"],
        sha=version["java"]["sha"],
        name=version["java"]["name"],
        filename=version["java"]["filename"])

    return Instance(
        name=name,
        version=instance["version"],
        forge=forge,
        world=instance["world"],
        command=instance["command"],
        server=server,
        java=java,
        mods=mods)