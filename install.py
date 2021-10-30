#!/bin/env python3


import os
import sys
import ssl
import json
import shutil
import hashlib
import tempfile
import subprocess
import urllib.request
from typing import Optional, List
from context import instance, context
from context import Java, RemoteFile
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


def install_java(java: Java, dest_dir: str):
    if os.path.isdir(os.path.join(dest_dir, java.name)):
        return
    
    os.makedirs(dest_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as path:
        download_path = os.path.join(path, java.filename)
        download_file(java.src, download_path, java.sha)
        shutil.unpack_archive(download_path, dest_dir)


def install_server(server: RemoteFile, dest_dir: str):
    dest_file = os.path.join(dest, server.filename)

    if os.path.isfile(dest_file):
        return
    
    os.makedirs(dest_dir, exist_ok=True)
    download_file(server.src, dest_file, server.sha)


def install_forge(forge: RemoteFile, dest_dir: str, java_home: str):
    os.makedirs(dest_dir, exist_ok=True)
    os.chdir(dest_dir)
    dest_file = os.path.join(dest_dir, forge.filename)
    
    if not os.path.isfile(dest_file):
        download_file(forge.src, dest_file, forge.sha)
    
    java_bin = os.path.join(java_home, "java")
    subprocess.call([java_bin, "-jar", forge.filename, "--installServer"])
    os.chdir(DIRNAME)


def install_mods(mods: List[RemoteFile], dest_dir:str):
    os.makedirs(dest_dir, exist_ok=True)
    
    for mod in mods:
        dest_file = os.path.join(dest_dir, mod.filename) 
        download_file(mod.src, dest_file, mod.sha)


def post_install(dest_dir: str, screen_name: str, command: str, java_home: str):
    templates = os.path.join(DIRNAME, "templates")
    
    # Add eula
    shutil.copy(os.path.join(templates, "eula.txt"), dest_dir)
    
    # Add screen script
    make_file(
        template=os.path.join(templates, "screen.sh"),
        dest=os.path.join(dest_dir, "screen.sh"),
        mode=0o744,
        kwargs={"screenName": screen_name})
    
    # Add start script
    make_file(
        template=os.path.join(templates, "start.sh"),
        dest=os.path.join(dest_dir, "start.sh"),
        mode=0o744,
        kwargs={"command": command, "javaHome": java_home})


def make_file(template: str, dest: str, mode: int, kwargs: dict):

    with open(template, "r") as o:
        template_string = o.read()
    with open(dest, "w") as d:
        d.write(template_string % kwargs)
    os.chmod(dest, mode)


def main():
    ctx = context()
    instance_name = sys.argv[1] if len(sys.argv) == 2 else ctx.active_instance
    ins = instance(instance_name)
    ins_path = os.path.join(ctx.install_path, instance_name)

    java_home = os.path.join(ctx.java_path, ins.java.name, "bin")
    install_java(java=ins.java, dest_dir=ctx.java_path)
    
    if ins.forge:
        install_forge(forge=ins.forge, dest_dir=ins_path, java_home=java_home)
        install_mods(mods=ins.mods, dest_dir=os.path.join(ins_path, "mods"))
    else:
        install_server(server=ins.server, dest_dir=ins_path)

    post_install(
        dest=ins_path,
        screen_name=config["screenName"],
        command=instance["command"],
        java_home=java_home)


if __name__ == "__main__":
    main()
