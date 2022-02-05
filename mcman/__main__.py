import os
import sys
from mcman import install
from mcman.context import context, get_instance


def main():
    ctx = context()
    instance_name = sys.argv[1] if len(sys.argv) == 2 else ctx.active_instance
    ins = get_instance(instance_name)
    ins_path = os.path.join(ctx.install_path, instance_name)

    java_home = os.path.join(ctx.java_path, ins.java.name, "bin")
    install.java(java=ins.java, dest_dir=ctx.java_path)
    
    if ins.forge:
        install.forge(forge=ins.forge, dest_dir=ins_path, java_home=java_home)
        install.mods(mods=ins.mods, dest_dir=os.path.join(ins_path, "mods"))
    else:
        install.server(server=ins.server, dest_dir=ins_path)

    install.post_install(
        dest_dir=ins_path,
        screen_name=ctx["screenName"],
        command=ins["command"],
        java_home=java_home)


if __name__ == "__main__":
    main()
