import argparse
import json
import sys

from cpu import CPU

HISTORY_BATCH_SIZE = 10000

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', type=lambda s: json.loads(s))
    args = parser.parse_args()

    cpu = CPU()
    if args.state:
        cpu.state = args.state
    else:
        cpu.load_program(sys.stdin.read())
    history = []
    
    for state in cpu.run():
        history.append(state)
        if len(history) == HISTORY_BATCH_SIZE:
            break

    sys.stdout.write(json.dumps(history))