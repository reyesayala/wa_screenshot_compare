import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--sort", action='store_true', help="Include to sort the output")  # optional
args = parser.parse_args()
print(args.sort)