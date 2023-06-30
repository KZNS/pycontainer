import os


def cgroup_create(
    cgroup_root: str,
    cpu_shares: int,
    cpu_cfs_period_us: int,
    cpu_cfs_quota_us: int,
    memory_limit_in_bytes: int,
):
    os.system("sudo cgcreate -g cpu,memory:{}".format(cgroup_root))

    if cpu_shares > 0:
        os.system("sudo cgset -r cpu.shares={} {}".format(cpu_shares, cgroup_root))
    if cpu_cfs_period_us > 0:
        os.system(
            "sudo cgset -r cpu.cfs_period_us={} {}".format(
                cpu_cfs_period_us, cgroup_root
            )
        )
    if cpu_cfs_quota_us > 0:
        os.system(
            "sudo cgset -r cpu.cfs_quota_us={} {}".format(cpu_cfs_quota_us, cgroup_root)
        )
    if memory_limit_in_bytes > 0:
        os.system(
            "sudo cgset -r memory.limit_in_bytes={} {}".format(
                memory_limit_in_bytes, cgroup_root
            )
        )


def cgroup_delete(cgroup_root: str):
    os.system("sudo cgdelete -r -g cpu,memory:{}".format(cgroup_root))
