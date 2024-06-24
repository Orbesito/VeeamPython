import os
import shutil
import time
import hashlib
import logging
from argparse import ArgumentParser

def setup_logging(log_file):#Sets up logging format 
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

def md5(file_path):#Funtion to create hash from file
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sync_folders(source, replica):#Syncronizer
    for src_dir, _, files in os.walk(source):
        relative_path = os.path.relpath(src_dir, source)
        replica_dir = os.path.join(replica, relative_path)
        if not os.path.exists(replica_dir):
            os.makedirs(replica_dir)
            logging.info(f"Created directory: {replica_dir}")
            print(f"Created directory: {replica_dir}")

        for file in files:
            src_file = os.path.join(src_dir, file)
            replica_file = os.path.join(replica_dir, file)
            if not os.path.exists(replica_file) or md5(src_file) != md5(replica_file):
                shutil.copy2(src_file, replica_file)
                logging.info(f"Copied file: {src_file} to {replica_file}")
                print(f"Copied file: {src_file} to {replica_file}")

    for rep_dir, _, rep_files in os.walk(replica):
        relative_path = os.path.relpath(rep_dir, replica)
        source_dir = os.path.join(source, relative_path)
        if not os.path.exists(source_dir):
            shutil.rmtree(rep_dir)
            logging.info(f"Removed directory: {rep_dir}")
            print(f"Removed directory: {rep_dir}")
            continue

        for file in rep_files:
            rep_file = os.path.join(rep_dir, file)
            source_file = os.path.join(source_dir, file)
            if not os.path.exists(source_file):
                os.remove(rep_file)
                logging.info(f"Removed file: {rep_file}")
                print(f"Removed file: {rep_file}")

def main():
    #Parse all the arguments
    parser = ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("source", help="Source folder path")
    parser.add_argument("replica", help="Replica folder path")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Log file path")
    args = parser.parse_args()
    
    # Ensure the log file exists
    if not os.path.exists(args.log_file):
        open(args.log_file, 'a').close()

    setup_logging(args.log_file)

    #Run infinite loop to check original and copy directories
    while True:
        sync_folders(args.source, args.replica)
        time.sleep(args.interval)

#In order to run -> python veaam.py -source_path -replica_path -interval(Seconds) -log_path
if __name__ == "__main__":
    main()
