import os
import time
from typing import List


def prepare_connect(network_name: str, netns_name: str, ip_addr: str):
    if not os.system("ip link show {} > /dev/null 2>&1".format(network_name)) == 0:
        create_network(network_name)

    os.system("sudo mkdir -p /var/run/netns")
    os.system("sudo touch /var/run/netns/{}".format(netns_name))

    os.system("sudo ip link add {0}_c type veth peer name {0}_b".format(netns_name))

    os.system("sudo ip link set dev {0}_b master {1}".format(netns_name, network_name))
    os.system("sudo ip link set dev {}_b up".format(netns_name))


def init_netns(netns_name: str, ip_addr: str):
    while (
        not os.system("sudo ip netns exec {0} true > /dev/null 2>&1".format(netns_name))
        == 0
    ):
        time.sleep(1)

    os.system("sudo ip link set dev {0}_c netns {0}".format(netns_name))
    os.system(
        "sudo ip netns exec {0} ip addr add {1} dev {0}_c".format(netns_name, ip_addr)
    )
    os.system("sudo ip netns exec {0} ip link set dev {0}_c up".format(netns_name))


def disconnect(network_name: str, netns_name: str):
    os.system("sudo ip link delete {}_b".format(netns_name))

    while True:
        ret = os.system("sudo ip netns delete {} > /dev/null 2>&1".format(netns_name))
        if ret == 0:
            break
        else:
            time.sleep(1)


def create_network(network_name: str):
    os.system("sudo ip link add dev {} type bridge".format(network_name))
    os.system("sudo ip link set dev {} up".format(network_name))
    os.system("sudo iptables -A FORWARD -i {} -j ACCEPT".format(network_name))


def network(argv: List[str]):
    if len(argv) < 2:
        print("wrong command: {}".format(" ".join(argv)))
        return -1

    command = argv[0]
    network_name = argv[1]

    if command == "create":
        create_network(network_name)
    elif command == "rm":
        os.system("sudo ip link delete dev {}".format(network_name))
    else:
        print("unknow command: {}".format(command))
