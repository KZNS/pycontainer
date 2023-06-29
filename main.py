import sys
import pycontainer

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('missing command, use "python main.py run"')
        exit(-1)

    command = sys.argv[1]

    if command == "run":
        ret = pycontainer.run(sys.argv[2:])
        exit(ret)
    if command == "network":
        ret = pycontainer.network(sys.argv[2:])
        exit(ret)
