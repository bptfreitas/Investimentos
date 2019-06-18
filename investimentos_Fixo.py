#!/usr/bin/python3

import os
import sys
import argparse
import math
import subprocess
import urllib3
import datetime
import json

from urllib.parse import urlencode

parser = argparse.ArgumentParser(description='Programa para cálculo de rendimentos de LCIs e LCAs')
parser.add_argument('--inicio', 
	metavar='N', 
	type=str, 
	nargs='+',
	help='starting date of investment')

parser.add_argument('--fim', 
	metavar='N', 
	type=str, 
	nargs='?',
	default=datetime.datetime.now().strftime("%d/%m/%Y"),
    help='ending date of the investment')

parser.add_argument('--taxa', 
	metavar='N',
	type=float, 
	nargs='+',
    help='taxa sobre a CDI do contrato')

parser.add_argument('--capital', 
	metavar='N',
	type=float, 
	nargs='+',
    help='capital inicial do investimento')


args = parser.parse_args()

capital = args.capital[0]
taxa = args.taxa[0]

debug = False

if debug:
	start = datetime.datetime(2019,2,18).strftime("%d/%m/%Y")
else:
	try:
		start = datetime.datetime.strptime(args.inicio[0],"%d/%m/%Y").strftime("%d/%m/%Y")
	except ValueError:
		sys.stderr.write("Erro: formato de data inicial invalido")
		sys.exit(-1)

if debug:
	today = datetime.datetime.now().strftime("%d/%m/%Y")
else:
	try:
		end = datetime.datetime.strptime(args.fim,"%d/%m/%Y").strftime("%d/%m/%Y")
	except ValueError:
		sys.stderr.write("Erro: formato de data final invalido")
		sys.exit(-1)

capital_inicial = capital
sys.stdout.write("Capital: " + str(capital) + '\n')
sys.stdout.write("Taxa contratada: " + str(taxa) + '\n')
sys.stdout.write("Data inicial do investimento: " + str(start) + '\n')
sys.stdout.write("Data final do investimento: " + str(end) + '\n')
	
#start.strftime("%d/%m/%Y") :
#url2 = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial="+start+"&dataFinal="+today
#url3 = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&amp;dataInicial="+start+"&amp;dataFinal="+today

datain = urlencode( { 'dataInicial'  : start , 'dataFinal'  : end, 'formato' : 'json' } )

url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?" + datain

header = {}
header['user-agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0' 
header['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

http_query = urllib3.PoolManager()
response = http_query.request('GET', url, headers = header)

if response.status == 200:
	if debug:
		print(url)
		print(response.status)
		print(response.data)
	capital = 10000
	cdi = 6.4/6.5

	data_json = json.loads(response.data.decode('utf-8'))

	data={}
	for d in data_json:
		data[d['data']]=d['valor']

	ganhos = []
		
	for dia in sorted(data.keys()):

		cdi_prop = 6.4/6.5
		SELIC = (float(data[dia])/100)

		cdi = SELIC*cdi_prop
		juros = 1.0 + cdi*taxa

		capital*=juros
		ganhos.append(capital)
		
	ganho_diario = [ ganhos[i]-ganhos[i-1]  for i in range(1,len(ganhos)) ]
	dias_corridos = len(ganhos)

	sys.stdout.write("Dias corridos: " + str(dias_corridos) + "\n")
	sys.stdout.write("Capital final: " + str(capital) + "\n")
