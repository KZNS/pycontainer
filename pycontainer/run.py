import getopt
import os
import subprocess
from typing import List
from . import network
from . import cgroup

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
        os.system("sudo tar -xf centos.tar -C {}".format(cfg["container_root"]))

    cgroup.cgroup_create(
        cfg["cgroup_root"],
        cfg["cpu_shares"],
        cfg["cpu_cfs_period_us"],
        cfg["cpu_cfs_quota_us"],
        cfg["memory_limit_in_bytes"],
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
    proc = subprocess.Popen(
        "sudo cgexec -g cpu,memory:{} sudo unshare --ipc --uts {} --user -r --mount --root {} --pid --mount-proc --fork {}".format(
            cfg["cgroup_root"], netns_opt, cfg["container_root"], run_task
        ),
        shell=True,
    )

    network.init_netns(cfg["netns_name"], cfg["ip_addr"])

    proc.wait()


def exit_container():
    cgroup.cgroup_delete(cfg["cgroup_root"])
    network.disconnect(cfg["network_name"], cfg["netns_name"])


def run(argv: List[str]):
    short_opts = "hit:m:"
    long_opts = [
        "help",
        "name=",
        "cpu_shares=",
        "cpu_cfs_period_us=",
        "cpu_cfs_quota_us=",
        "memory=",
        "network=",
        "ip=",
    ]

    opts, args = getopt.getopt(argv, short_opts, long_opts)

    run_task = "bash"

    cfg["container_name"] = ""
    cfg["cpu_shares"] = -1
    cfg["cpu_cfs_period_us"] = -1
    cfg["cpu_cfs_quota_us"] = -1
    cfg["memory_limit_in_bytes"] = -1
    cfg["network_name"] = ""

    for opt, arg in opts:
        if opt == "-t":
            run_task = arg
        elif opt == "-i":
            pass
        elif opt == "--name":
            cfg["container_name"] = arg
        elif opt == "--cpu_shares":
            if arg.isdigit() and 1 <= int(arg) <= 1024:
                cfg["cpu_shares"] = int(arg)
            else:
                print("illegal cpu_shares = {}".format(arg))
                return -1
        elif opt == "--cpu_cfs_period_us":
            cfg["cpu_cfs_period_us"] = int(arg)
        elif opt == "--cpu_cfs_quota_us":
            cfg["cpu_cfs_quota_us"] = int(arg)
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
