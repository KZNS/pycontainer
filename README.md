# PyContainer

简单实现的容器引擎。

- 使用 unshare 控制 namespace 进行隔离，
- 使用 cgcreate 系列指令控制 cgroup 限制系统资源，
- 使用 ip link 进行容器间网络通信。

## Usage

```shell
python main.py run --name aa --memory 10m --cpushares 512 --network net1 --ip 10.0.0.1/24 -it bash
```

## Note

从 docker 获取 centos 的全部文件：

```shell
docker create centos
docker ps -a

docker export -o centos.tar [containerID]
tar -xvf centos.tar -C centos/
```