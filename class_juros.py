#!/usr/bin/python3

import os
import sys
import argparse
import math
import subprocess
import urllib3
import datetime
import json
import unittest

from urllib.parse import urlencode

# class that fetches various interest rates parameters
class Juros:
	def __init__(self):
		self._SELIC_Rates = {}
		self._SELIC_Rates_Period = {}
		self._CDI_Rate = 6.4/6.5
		self._FixedRate = 1;

	def getCDIRate(self):
		# magic constant to compute the real CDI from the SELIC
		# TODO: discover how to fetch/compute the real CDI from the Internetn
		return self._CDI_Rate

	def getFixedRate(self):
		return self._FixedRate

	def setYearlyFixedRate(self,rate):
		self._FixedRate = rate/252

	def getSELICRatesPeriod(self):
		return self._SELIC_Rates_Period
	
	# fetches the SELIC rates from the BCB (www.bcb.gov.br) given a fixed period
	def fetchSELICRates(self, inicio, fim , debug=False):

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

		currentRatesPeriod = self.getSELICRatesPeriod()

		if currentRatesPeriod != {}:

			new_start = start_date
			new_end = end_date

			changed = False
			if new_start < currentRates['inicio']:
				currentRatesPeriod['inicio'] = new_start
				changed = True
			if new_end > currentRates['fim']:
				currentRatesPeriod['fim'] = new_end
				changed = True

			if changed==False:
				return self._SELIC_Rates
		else:
			currentRatesPeriod['inicio'] = start_date
			currentRatesPeriod['fim'] = end_date

		start = currentRatesPeriod['inicio'].strftime("%d/%m/%Y")
		end = currentRatesPeriod['fim'].strftime("%d/%m/%Y")

		datain = urlencode( { 'dataInicial'  : start , 'dataFinal'  : end, 'formato' : 'json' } )

		url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?" + datain

		header = {}
		header['user-agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0' 
		header['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

		http_query = urllib3.PoolManager()
		response = http_query.request('GET', url, headers = header)		

		if response.status == 200:

			data_json = json.loads(response.data.decode('utf-8'))

			data = {}
			for d in data_json:
				data[datetime.datetime.strptime(d['data'],"%d/%m/%Y")]=float(d['valor'])
			
			# sets the new SELIC period dictionary
			self._SELIC_Rates = data

			# SELIC fetch period is only updated after a successful request
			self._SELIC_Rates_Period = currentRatesPeriod

			return self._SELIC_Rates

		else:
			sys.stderr.write("Erro obtendo SELIC diaria\n")
			sys.exit(-1)

	# strategy method to implement various interest rates
	def getInterestRates(self,inicio,fim):
		pass

# computes the interest rate considering the LCA rate, defined by the SELIC and the CDI Rate
class JurosLCA(Juros):

	def getInterestRates(self,inicio,fim):
		SELIC = self.fetchSELICRates(inicio,fim)
		CDI = self.getCDIRate()
		rates = { key : (1+value)*CDI for key,value in self._SELIC_Rates.items() }
		return rates


# gets the interest rate considering fixed yearly rate
class JurosFixos(Juros):

	def getInterestRates(self,inicio,fim):
		# getting SELIC just to grab valid dates 		
		SELIC = self.fetchSELICRates(inicio,fim)

		FixedRate = self.getFixedRate()
		rates = { key : (1+FixedRate) for key,value in SELIC.items() }


class Old:

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

		# taxasSELIC = self.fetchSELICRates(inicio,fim)

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
	
#start.strftime("%d/%m/%Y") :
#url2 = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial="+start+"&dataFinal="+today
#url3 = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&amp;dataInicial="+start+"&amp;dataFinal="+today

class TestJurosClass(unittest.TestCase):

	def setUp(self):
		self.Juros = Juros()

	def test_010_fetchSELIC(self):
		selic1 = self.Juros.fetchSELICRates('01/02/2019','07/02/2019')

		print(selic1)

class TestJurosLCAClass(unittest.TestCase):

	def setUp(self):
		self.JurosLCA = JurosLCA()		

	def test_LCA(self):
		LCA = self.JurosLCA.getInterestRates('01/02/2019','07/02/2019')

		print(LCA)

class TestJurosFixosClass(unittest.TestCase):

	def setUp(self):
		self.JurosFixos = JurosFixos()

	def test_010_setYearlyFixedRate(self):

		self.JurosFixos.setYearlyFixedRate(252)
		fixos = self.JurosFixos.getFixedRate()

		self.assertEqual(fixos,1)

	def test_020_JurosFixos(self):
		JurosFixos = self.JurosFixos.getInterestRates('01/02/2019','07/02/2019')

		print(JurosFixos)		



		#self.assertEqual(selic, 'FOO')

	#def test_isupper(self):
	#   self.assertTrue('FOO'.isupper())
	#  self.assertFalse('Foo'.isupper())

	#def test_split(self):
	#   s = 'hello world'
	#  self.assertEqual(s.split(), ['hello', 'world'])
	# check that s.split fails when the separator is not a string
	# with self.assertRaises(TypeError):
	#    s.split(2)

if __name__ == '__main__':
    unittest.main()