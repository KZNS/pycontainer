import getopt
import os
import subprocess
from typing import List
from . import network

cfg = {}


def get_container_root(container_name: str):
    return os.path.join(".containers", container_name)


def get_cgroup_root(container_name: str):
    return os.path.join("pycontainer", container_name)


def init_container():
    cfg["container_root"] = get_container_root(cfg["container_name"])
    cfg["cgroup_root"] = get_cgroup_root(cfg["container_name"])

    if not os.path.exists(cfg["container_root"]):
        os.makedirs(cfg["container_root"])
        os.system("tar -xf centos.tar -C {}".format(cfg["container_root"]))

    os.system("sudo cgcreate -g cpu,memory:{}".format(cfg["cgroup_root"]))

    if cfg["cpu_shares"] > 0:
        os.system(
            "sudo cgset -r cpu.shares={} {}".format(
                cfg["cpu_shares"], cfg["cgroup_root"]
            )
        )
    if cfg["memory_limit_in_bytes"] > 0:
        os.system(
            "sudo cgset -r memory.limit_in_bytes={} {}".format(
                cfg["memory_limit_in_bytes"], cfg["cgroup_root"]
            )
        )

    if cfg["network_name"]:
        cfg["netns_name"] = cfg["container_name"] + "_net"
        network.prepare_connect(cfg["network_name"], cfg["netns_name"], cfg["ip_addr"])
    else:
        cfg["netns_name"] = ""


def run_in_container(run_task: str):
    if cfg["netns_name"]:
        netns_opt = "--net=" + os.path.join("/var/run/netns", cfg["netns_name"])
    else:
        netns_opt = "--net"
    print(netns_opt)
    proc = subprocess.Popen(
        "sudo cgexec -g cpu,memory:{} sudo unshare --ipc --uts {} --user -r --mount --root {} --pid --mount-proc --fork {}".format(
            cfg["cgroup_root"], netns_opt, cfg["container_root"], run_task
        ),
        shell=True,
    )

    network.init_netns(cfg["netns_name"], cfg["ip_addr"])

    # os.system("sudo cgclassify -g cpu,memory:{} {}".format(cgroup_root, proc.pid))

    proc.wait()


def exit_container():
    os.system("sudo cgdelete -r -g cpu,memory:{}".format(cfg["cgroup_root"]))
    network.disconnect(cfg["network_name"], cfg["netns_name"])


def run(argv: List[str]):
    short_opts = "hit:m:"
    long_opts = ["help", "name=", "cpushares=", "memory=", "network=", "ip="]

    opts, args = getopt.getopt(argv, short_opts, long_opts)

    run_task = "bash"

    cfg["container_name"] = ""
    cfg["cpu_shares"] = -1
    cfg["memory_limit_in_bytes"] = -1
    cfg["network_name"] = ""

    for opt, arg in opts:
        if opt == "-t":
            run_task = arg
        elif opt == "-i":
            pass
        elif opt == "--name":
            cfg["container_name"] = arg
        elif opt == "--cpushares":
            if arg.isdigit() and 1 <= int(arg) <= 1024:
                cfg["cpu_shares"] = int(arg)
            else:
                print("illegal cpu_shares = {}".format(arg))
                return -1
        elif opt in ["-m", "--memory"]:
            if arg.isdigit():
                cfg["memory_limit_in_bytes"] = int(arg)
            elif len(arg) > 2 and arg[:-1].isdigit():
                unit = arg[-1]
                unit_map = {"k": 1024, "m": 1024**2, "g": 1024**3}
                if unit in unit_map.keys():
                    cfg["memory_limit_in_bytes"] = int(arg[:-1]) * unit_map[unit]
                else:
                    print("unkonw unit: {}".format(unit))
                    return -1
            else:
                print("illegal memory limit = {}".format(arg))
                return -1
        elif opt == "--network":
            cfg["network_name"] = arg
        elif opt == "--ip":
            cfg["ip_addr"] = arg
        else:
            print("unknow arg: {} {}".format(opt, arg))
            return -1

    if not cfg["container_name"]:
        print('need container name by "--name <container_name>"')
        return -1

    init_container()
    run_in_container(run_task)
    exit_container()

    return 0
