#!/usr/bin/python3

import os
import sys
import argparse
import math
import subprocess
import urllib3
import datetime
import json
import xml.etree.ElementTree as ET

from datetime import timedelta,datetime
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
	default=datetime.now().strftime("%d/%m/%Y"),
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

debug = True

if debug:
	start_date = datetime(2018,1,31)
else:
	try:
		start_date = datetime.strptime(args.inicio[0],"%d/%m/%Y")
	except ValueError:
		sys.stderr.write("Erro: formato de data inicial invalido")
		sys.exit(-1)
start = start_date.strftime("%Y%m")

if debug:
	end_date = datetime.now()
else:
	try:
		end_date = datetime.strptime(args.fim,"%d/%m/%Y")
	except ValueError:
		sys.stderr.write("Erro: formato de data final invalido")
		sys.exit(-1)
end = end_date.strftime("%Y%m")

capital_inicial = capital
sys.stdout.write("Capital: " + str(capital) + '\n')
sys.stdout.write("Taxa contratada: " + str(taxa) + '\n')
sys.stdout.write("Data inicial do investimento: " + str(start) + '\n')
sys.stdout.write("Data final do investimento: " + str(end) + '\n')
	
#start.strftime("%d/%m/%Y") :
#url2 = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial="+start+"&dataFinal="+today
#url3 = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&amp;dataInicial="+start+"&amp;dataFinal="+today

#datain = urlencode( { 'dataInicial'  : start , 'dataFinal'  : end, 'formato' : 'json' } )
#url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?" + datain

url = "http://api.sidra.ibge.gov.br/values/t/1419/n1/all/p/"+str(start)+"-"+str(end)+"/v/63"

if debug:
	print('URL:',url)

header = {}
header['user-agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0' 
header['Accept'] = 'application/json'

# all_days = [ start_date+timedelta(days=number_of_days) for number_of_days in range((end_date-start_date).days) ] 

# print(all_days)

http_query = urllib3.PoolManager()
response = http_query.request('GET', url, headers = header)

if response.status == 200:
	if debug:
		print(url)
		print(response.status)
		print(response.data)

	# tree = ET.fromstring(response.data)

	data = json.loads(response.data.decode('utf-8'))

	# print(data)

	IPCA_mensal_periodo = {}
	for i in range(len(data)):
		try:
			IPCA_mensal_periodo[data[i]['D2C']] = float(data[i]['V'])
		except ValueError:
			pass

	# print(IPCA_mensal)

	ganhos = []
		
	for n in range((end_date-start_date).days):

		dia = start_date + timedelta(days=n)

		if dia.weekday() <5:
			try:
				IPCA_mensal = IPCA_mensal_periodo[dia.strftime('%Y%m')]
			except:
				continue

			IPCA_diario = (IPCA_mensal/(31*100))
		
			juros = 1.0 + IPCA_diario + taxa/(252*100)

			capital*=juros
			ganhos.append(capital)
		
	ganho_diario = [ ganhos[i]-ganhos[i-1]  for i in range(1,len(ganhos)) ]
	dias_corridos = len(ganhos)

	sys.stdout.write("Dias corridos: " + str(dias_corridos) + "\n")
	sys.stdout.write("Capital final: " + str(capital) + "\n")

else: 
	sys.stderr.write("Erro: nao foi possivel baixar dados do IPCA\n")
