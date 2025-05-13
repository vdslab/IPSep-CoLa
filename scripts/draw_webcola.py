import argparse
import json
import os
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest', default='.')
    parser.add_argument('--iterations', type=int, default=30)
    parser.add_argument('--overlap-removal',
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('--cluster-overlap-removal',
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('input', nargs='+')
    args = parser.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    for filepath in args.input:
        basename = os.path.basename(filepath)
        command = ['node', 'js/src/draw_webcola.js',
                   '--graphFile', filepath,
                   '--output', os.path.join(args.dest, basename)]
        if args.overlap_removal:
            command.append('--overlapRemoval')
        if args.cluster_overlap_removal:
            command.append('--clusterOverlapRemoval')
        subprocess.run(command)


if __name__ == '__main__':
    main()
