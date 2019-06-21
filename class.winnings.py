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