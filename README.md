# PyContainer

简单实现的容器引擎。

- 使用 unshare 控制 namespace 进行隔离，
- 使用 cgcreate 系列指令控制 cgroup 限制系统资源，
- 使用 ip link 进行容器间网络通信。

## Usage

首先需要获取一个 centos 镜像
```shell
docker create centos
docker ps -a
docker export -o centos.tar [containerID]
```

在容器中执行

```shell
python main.py run --name aa --memory 10m --cpu_cfs_period_us 100000 --cpu_cfs_quota_us 50000 --network net1 --ip 10.0.0.1/24 -it bash
```
