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
else:
    ip=args.ip
    
if __name__ == '__main__':
    server=PDBServer(dbname=args.db,ip=ip,port=args.port)
    server.create_cites_endpoints()
    server.create_cache_endpoints()
    server.create_lookup_endpoints()
    server.create_gsquery_endpoints()
    #server.create_endpoints('redalyc')
    #server.create_endpoints('udea')
    #server.create_endpoints('colciencias')
    #server.create_endpoints('estudios_gerenciales')
    #server.create_endpoints('covid19')
    #server.create_endpoints('coronavirus')
    #server.create_endpoints('covid_19')
    #server.create_endpoints('hcov_19')
    #server.create_endpoints('sars_cov_2')
    #server.create_endpoints('sarscov2')
    #server.create_endpoints('covid_2019')
    #server.create_endpoints('medrxiv')
    #server.create_endpoints('arxiv')
    #server.create_endpoints('nature')
    #server.create_endpoints('medicine')
    #server.create_endpoints('science')
    #server.create_endpoints('lancet')
    #server.create_endpoints('plos_one')
    #server.create_endpoints('cell')
    #server.create_endpoints('infectious_diseases')
    #server.create_endpoints('radiology')
    #server.create_endpoints('bmj')
    #server.create_endpoints('transfusion')
    #server.create_endpoints('infection')
    #server.create_endpoints('emerging_infectious_diseases')
    #server.create_endpoints('biorxiv')
    #server.create_endpoints('critical_care')
    #server.create_endpoints('public_health')
    #server.create_endpoints('critical_care_medicine')
    #server.create_endpoints('methods')
    #server.create_endpoints('pediatrics')
    #server.create_endpoints('clinical_infectious_diseases')
    #server.create_endpoints('biochemistry')
    #server.create_endpoints('virology')
    #server.create_endpoints('the_journal_of_infectious_diseases')
    #server.create_endpoints('journal_of_infection')
    #server.create_endpoints('jama')
    #server.create_endpoints('structure')
    #server.create_endpoints('journal_of_virology')
    #server.create_endpoints('hepatology')
    #server.create_endpoints('journal_of_medical_virology')
    #server.create_endpoints('biochimica_et_biophysica_acta')
    #server.create_endpoints('virus_research')
    #server.create_endpoints('biochemical_and_biophysical_research_communications')
    #server.create_endpoints('respiratory_medicine')
    #server.create_endpoints('gene')
    #server.create_endpoints('lancet_infectious_diseases')
    #server.create_endpoints('antiviral_research')
    server.start()



