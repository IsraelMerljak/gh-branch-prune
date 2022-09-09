from lib import delete_branches
import argparse
import signal


def __exit_handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(1)


signal.signal(signal.SIGINT, __exit_handler)

parser = argparse.ArgumentParser(description='CLI tool used to help pruning unused branches from specified repository.')

parser.add_argument('-o', '--organization', type=str, help='organization to lookup repository')
parser.add_argument('-r', '--repository', type=str, help='repository used to scan branches', required=True)
parser.add_argument('-a', '--age', type=int, help='minimum age of the branches to delete', default=60)
parser.add_argument('--dry-run', action='store_true', help='mark execution as dry-run', default=True)
parser.add_argument('-q', '--quiet', action='store_true', help='decrease verboseness', default=False)

args = parser.parse_args()

delete_branches(
    args.repository,
    args.organization,
    age=args.age,
    quiet=args.quiet,
    dry_run=args.dry_run
)
