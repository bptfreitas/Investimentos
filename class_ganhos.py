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

from class_juros import Juros, JurosLCA, JurosFixos, SemJuros

from urllib.parse import urlencode

class Investiment:

	def __init__(self,capital=0):
		self._capital = capital
		self._Juros = SemJuros()

	def setFixed(self,yearlyRate):		
		self._Juros = JurosFixos()
		self._Juros.setYearlyFixedRate(yearlyRate)

	def setLCA(self,contractRate):
		self._Juros = JurosLCA()
		self._Juros.setContractRate(contractRate)

	def setStartingCapital(self,capital):
		self._capital = capital

	def getStartingCapital(self):
		return self._capital

	def getWinnings(self, inicio, fim = datetime.datetime.now().strftime("%d/%m/%Y")):

		capital = self.getStartingCapital()
		# taxa = self.getRate()

		interestRates = self._Juros.getInterestRates(inicio,fim)

		ganhos = []
		
		for dia in sorted(interestRates.keys()):

			juros = interestRates[dia]

			capital*=juros
			ganhos.append(capital)
			
		ganho_diario = [ ganhos[i]-ganhos[i-1]  for i in range(1,len(ganhos)) ]
		dias_corridos = len(ganhos)

		return capital,dias_corridos,ganho_diario


class TestFixedInvestments(unittest.TestCase):

	def setUp(self):
		self.Investment = Investiment(10000)
		self.Investment.setFixed(10)

	def test_010_JurosSemestrais(self):
		
		capital, dias, ganhos = self.Investment.getWinnings('01/01/2019','01/07/2019')

		print(capital)
		sys.stdout.flush()


class TestLCAInvestment(unittest.TestCase):

	def setUp(self):
		self.Investment = Investiment(10000)
		self.Investment.setLCA(0.85)

	def test_010_JurosSemestrais(self):
		
		capital, dias, ganhos = self.Investment.getWinnings('18/02/2019','22/06/2019')

		print(capital)
		sys.stdout.flush()

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