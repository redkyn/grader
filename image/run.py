# Houses logic and functionality for creating images with payloads
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create images for grading.')
    parser.add_argument('--folder', default='', 
           help='Folder with dockerfile and optional payload.')
    parser.add_argument('--git', default='', 
           help='Git repository with dockerfile and optional payload.')

    args = parser.parse_args()
