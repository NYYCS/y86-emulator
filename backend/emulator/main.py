import argparse
import json
import sys

from cpu import CPU

BATCH_SIZE = 10000

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', type=lambda s: json.loads(s))
    args = parser.parse_args()

    cpu = CPU()
    cpu.load_program(sys.stdin.read())
    history = []

    if args.state:
        cpu.state = args.state
    
    for state in cpu.run():
        history.append(state)
        if len(history) == BATCH_SIZE:
            break

    sys.stdout.write(json.dumps(history))
