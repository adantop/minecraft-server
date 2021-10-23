#!/bin/env python3


import os
import ssl
import json
import shutil
import hashlib
import tempfile
import subprocess
import urllib.request
from typing import Optional
# Java releases: https://jdk.java.net/archive/
# Minecraft releases: https://mcversions.net/


DIRNAME = os.path.abspath(os.path.dirname(__file__))


def download_file(url: str, filename: str, sha: Optional[str]):
    psize = 8192
    pcount = 0

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    res = urllib.request.urlopen(url, context=ctx)
    # fsize = int(res.info().get("Content-Length"))
    sha256 = hashlib.sha256()
    with open(filename, "wb") as file:
        while True:
            buffer = res.read(psize)
            if not buffer:
                break
            pcount += len(buffer)
            file.write(buffer)
            sha256.update(buffer)
            if (pcount / psize) % 1024 == 0:
                print(".", end="", flush=True)
    assert sha256.hexdigest() == sha, "Download failed"


def install_java(url: str, name: str, filename: str, sha: Optional[str], dest: str):
    if os.path.isdir(os.path.join(dest, name)):
        return
    
    os.makedirs(dest, exist_ok=True)
    with tempfile.TemporaryDirectory() as path:
        download_path = os.path.join(path, filename)
        download_file(url, download_path, sha)
        shutil.unpack_archive(download_path, dest)


def install_server(url: str, dest: str, filename: str, sha: Optional[str]):
    os.makedirs(dest, exist_ok=True)
    if os.path.isdir(os.path.join(dest, filename)):
        return
    
    if not os.path.isfile(os.path.join(dest, filename)):
        dl_path = os.path.join(dest, filename)
        download_file(url, dl_path, sha)


def install_forge(url: str, dest: str, filename: str, sha: Optional[str], java_home: str):
    os.makedirs(dest, exist_ok=True)
    os.chdir(dest)
    
    if not os.path.isfile(os.path.join(dest, filename)):
        dl_path = os.path.join(dest, filename)
        download_file(url, dl_path, sha)
    
    java = os.path.join(java_home, "java")
    subprocess.call([java, "-jar", filename, "--installServer"])
    os.makedirs("mods", exist_ok=True)
    # TODO: Copy mods
    os.chdir(DIRNAME)


def post_install(dest: str, screen_name: str, command: str, java_home: str):

    templates = os.path.join(DIRNAME, "templates")
    # Add eula
    shutil.copy(os.path.join(templates, "eula.txt"), dest)
    # Add screen script
    make_file(
        template=os.path.join(templates, "screen.sh"),
        dest=os.path.join(dest, "screen.sh"),
        mode=0o644,
        kwargs={"screenName": screen_name})
    # Add start script
    make_file(
        template=os.path.join(templates, "start.sh"),
        dest=os.path.join(dest, "start.sh"),
        mode=0o744,
        kwargs={"command": command, "javaHome": java_home})


def make_file(template: str, dest: str, mode: int, kwargs: dict):

    with open(template, "r") as o:
        template_string = o.read()
    with open(dest, "w") as d:
        d.write(template_string % kwargs)
    os.chmod(dest, mode)


def main():
    config = json.load(open(os.path.join(DIRNAME, "server", "config.json")))
    versions = json.load(open(os.path.join(DIRNAME, "server", "versions.json")))

    instance_id = config["activeInstanceId"]
    instance = config["instances"][instance_id]
    version = versions[instance["version"]]
    java, server, forge = version["java"], version["server"], version["forge"]
    java_home = os.path.join(config["javaPath"], java["name"], "bin")
    server_path = os.path.join(config["installPath"], instance_id)

    install_java(
        url=java["src"],
        name=java["name"],
        filename=java["filename"],
        sha=java["sha"],
        dest=config["javaPath"])

    if instance["forge"]:
        install_forge(
            url=forge["src"],
            dest=server_path,
            filename=forge["filename"],
            sha=forge["sha"],
            java_home=java_home)
    else:
        install_server(
            url=server["src"],
            dest=server_path,
            filename="server.jar",
            sha=server["sha"])
    
    post_install(
        dest=server_path,
        screen_name=config["screenName"],
        command=instance["command"],
        java_home=java_home)


if __name__ == "__main__":
    main()
