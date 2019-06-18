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


class Juros:
	def __init__(self):
		self._SELIC_Rates = {}
		self._CDI_Rate = 6.4/6.5

	def getCDIRate(self):
		# constante magica para calcular a CDI real a partir da SELIC
		# TODO: descobrir como eh o calculo certo para isso dado um periodo
		return self._CDI_Rate
	
	def getSELICRates(self, inicio, fim , debug=False):

		try:
			start_date = datetime.datetime.strptime(inicio,"%d/%m/%Y")
		except ValueError:
			sys.stderr.write("Erro: formato de data inicial invalido. Digite no formato dd/mm/aaaa.\n")
			sys.exit(-1)

		try:
			if debug:
				print("fim:"+fim+"\n")
			end_date = datetime.datetime.strptime(fim,"%d/%m/%Y")			
		except ValueError:
			sys.stderr.write("Erro: formato de data final invalido. Digite no formato dd/mm/aaaa.\n")
			sys.exit(-1)

		if self._SELIC_Rates != {} :

			new_start = start_date
			new_end = end_date

			changed = False
			if new_start < self.__start_date:
				self.__start_date = new_start
				changed = True
			if new_end > self.__end_date:
				self.__end_date = new_end
				changed = True

			if changed:
				return self._SELIC_Rates
		else:
			self.__start_date = start_date
			self.__end_date = end_date

		start = self.__start_date.strftime("%d/%m/%Y")
		end = self.__end_date.strftime("%d/%m/%Y")

		datain = urlencode( { 'dataInicial'  : start , 'dataFinal'  : end, 'formato' : 'json' } )

		url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?" + datain

		header = {}
		header['user-agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0' 
		header['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

		http_query = urllib3.PoolManager()
		response = http_query.request('GET', url, headers = header)		

		if response.status == 200:

			data_json = json.loads(response.data.decode('utf-8'))

			data={}
			for d in data_json:
				data[datetime.datetime.strptime(d['data'],"%d/%m/%Y")]=d['valor']

			self._SELIC_Rates = data

			return self._SELIC_Rates

		else:
			sys.stderr.write("Erro obtendo SELIC diaria\n")
			sys.exit(-1)

	def getInterestByDay(self,dia):
		pass

class JurosLCA(Juros):

	def __init__(self,inicio,fim):
		self._SELIC_Rates = self.getSELICRates(inicio,fim)

	def getInterestByDay(self,dia):
		if dia in self._SELIC_Rates:
			return (1+self._SELIC_Rates[dia]*self.getCDIRate())
		else
			return 1


class Investimento:

	def __init__(self):

		if tipo == 'LCA':
			self._juros_dias = JurosLCA()

	def setPeriod(self,inicio, fim = datetime.datetime.now().strftime("%d/%m/%Y")):

		try:
			start_date = datetime.datetime.strptime(inicio,"%d/%m/%Y")		
		except ValueError:
			sys.stderr.write("Erro: formato de data inicial invalido. Digite no formato dd/mm/aaaa.\n")
			sys.exit(-1)

		try:
			if debug:
				print("fim:"+fim+"\n")
			end_date = datetime.datetime.strptime(fim,"%d/%m/%Y")			
		except ValueError:
			sys.stderr.write("Erro: formato de data final invalido. Digite no formato dd/mm/aaaa.\n")
			sys.exit(-1)		

	def setStartingCapital(self,capital):
		self.__starting_capital = capital

	def getStartingCapital(self):
		return self.__starting_capital

	def getWinnings(self, inicio, fim = datetime.datetime.now().strftime("%d/%m/%Y")):

		capital = self.getStartingCapital()
		# taxa = self.getRate()

		# taxasSELIC = self.getSELICRates(inicio,fim)

		ganhos = []
		
		for dia in sorted(taxasSELIC.keys()):

			#SELIC = (float(taxasSELIC[dia])/100)

			#cdi = SELIC*self.getCDIRate()
			#juros = 1.0 + cdi*taxa

			juros = self.getInterestByDay(dia)

			capital*=juros
			ganhos.append(capital)
			
		ganho_diario = [ ganhos[i]-ganhos[i-1]  for i in range(1,len(ganhos)) ]
		dias_corridos = len(ganhos)

		return capital,dias_corridos,ganho_diario
		
Investimento = InvestimentoSELIC()

if False:
	Investimento.setRate(0.85)
	Investimento.setStartingCapital(10000)
	capital, dias_corridos, ganhos = Investimento.getWinnings('20/02/2019')

	print(capital)
	print(dias_corridos)

	sys.exit(-1)


parser = argparse.ArgumentParser(description='Programa para cálculo de rendimentos de LCIs e LCAs')
parser.add_argument('--inicio', 
	metavar='N', 
	type=str, 
	nargs='+',
	help='data inicial do investimento')

parser.add_argument('--fim', 
	metavar='N', 
	type=str, 
	nargs='?',
	default=datetime.datetime.now().strftime("%d/%m/%Y"),
    help='data final do investimento')

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

parser.add_argument('-f', 
	nargs='?', 
	type=argparse.FileType('r'),
	default=sys.stdin,
	help='le os investimentos de um arquivo')

args = parser.parse_args()

capital = args.capital[0]
taxa = args.taxa[0]

print(args)

debug = False

if debug:
	start = datetime.datetime(2019,2,18).strftime("%d/%m/%Y")
else:
	try:
		start = datetime.datetime.strptime(args.inicio[0],"%d/%m/%Y").strftime("%d/%m/%Y")
	except ValueError:
		sys.stderr.write("Erro: formato de data inicial invalido. Digite no formato dd/mm/aaaa.")
		sys.exit(-1)

if debug:
	today = datetime.datetime.now().strftime("%d/%m/%Y")
else:
	try:
		end = datetime.datetime.strptime(args.fim,"%d/%m/%Y").strftime("%d/%m/%Y")
	except ValueError:
		sys.stderr.write("Erro: formato de data final invalido. Digite no formato dd/mm/aaaa.")
		sys.exit(-1)

capital_inicial = capital
sys.stdout.write("Capital: " + str(capital) + '\n')
sys.stdout.write("Taxa contratada: " + str(taxa) + '\n')
sys.stdout.write("Data inicial do investimento: " + str(start) + '\n')
sys.stdout.write("Data final do investimento: " + str(end) + '\n')
	
#start.strftime("%d/%m/%Y") :
#url2 = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial="+start+"&dataFinal="+today
#url3 = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&amp;dataInicial="+start+"&amp;dataFinal="+today
