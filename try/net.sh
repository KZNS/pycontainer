sudo ip link add dev br0 type bridge
sudo ip link set dev br0 up
sudo iptables -A FORWARD -i br0 -j ACCEPT

# net1

sudo ip netns add net1
sudo ip link add t1_c type veth peer name t1_b

sudo ip link set dev t1_c netns net1
sudo ip netns exec net1 ip addr add 10.0.0.1/24 dev t1_c
sudo ip netns exec net1 ip link set dev t1_c up

sudo ip link set dev t1_b master br0
sudo ip link set dev t1_b up

# net2

sudo ip netns add net2
sudo ip link add t2_c type veth peer name t2_b

sudo ip link set dev t2_c netns net2
sudo ip netns exec net2 ip addr add 10.0.0.2/24 dev t2_c
sudo ip netns exec net2 ip link set dev t2_c up

sudo ip link set dev t2_b master br0
sudo ip link set dev t2_b up

# test

sudo ip netns exec net1 ping 10.0.0.2
