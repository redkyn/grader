from main import run
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create images for grading.')
    parser.add_argument('--no-cache', default=False, action='store_true', 
           help='Rebuild the image from scratch; don\'t use cached intermediary'
           + ' images.')
    parser.add_argument('target', metavar='target', 
                       help='Source with Dockerfile and image.json.')
    args = parser.parse_args()
    run(args.target, args.no_cache)
