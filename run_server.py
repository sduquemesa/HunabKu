from PDBServer.PDBServer import PDBServer
import requests
import json

import sys
import socket
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--db', type=str, default='colav', help='database name (default colav)')
parser.add_argument('--ip', type=str, default=None, help='local server ip (optional for public ip)')
parser.add_argument('--port', type=str, default=8080, help='server port (default 8080)')

args = parser.parse_args()
if args.ip == None:
    ip=socket.gethostbyname(socket.gethostname())

if __name__ == '__main__':
    server=PDBServer(dbname=args.db,ip=ip,port=args.port)
    server.start()


