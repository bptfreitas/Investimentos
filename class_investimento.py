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

from class_interest import Juros, JurosCDI, JurosFixos, SemJuros

from urllib.parse import urlencode

class Investimento:

	def __init__(self, capital=0):
		self._capital = round(capital,2)
		self._limite_ganhos_diarios = 5
		self._Juros = SemJuros()

	def getDailyWinningsLimit(self):
		return self._limite_ganhos_diarios

	def setFixed(self, yearlyRate):		
		self._Juros = JurosFixos()
		self._Juros.setYearlyFixedRate( yearlyRate )

	def setIPCA(self, fixedRate):		
		self._Juros = JurosIPCA()
		self._Juros.setFixedRate( fixedRate )

	def setCDI(self, contractRate):
		self._Juros = JurosCDI()
		self._Juros.setContractRate(contractRate)

	def setStartingCapital(self, capital):
		self._capital = round(capital,2)

	def getStartingCapital(self):
		return self._capital

	def getWinnings(self, inicio, fim = datetime.datetime.now().strftime("%d/%m/%Y")):

		capital = self.getStartingCapital()
		# taxa = self.getRate()

		interestRates = self._Juros.getInterestRates(inicio,fim)

		ganhos = []

		limite_ganhos_diarios = self.getDailyWinningsLimit()
		
		for dia in sorted(interestRates.keys()):

			juros = interestRates[dia]

			capital*=juros

			ganhos.append(capital)
			if len(ganhos)>limite_ganhos_diarios+1:
				ganhos = ganhos[0:limite_ganhos_diarios+1]
			
		ganho_diario = [ ganhos[i]-ganhos[i-1]  for i in range(1,len(ganhos)) ]
		dias_corridos = len(ganhos)

		return round(capital,2), len(interestRates), ganho_diario


class TestFixedInvestments(unittest.TestCase):

	def setUp(self):
		self.Investment1 = Investimento(10.33*1002.32)
		self.Investment1.setFixed(10.02)

		self.Investment2 = Investimento(10*1013.59)
		self.Investment2.setFixed(10)		

		self.Investment3 = Investimento(5*1032.31)
		self.Investment3.setFixed(10.01)

	def test_010_JurosSemestrais(self):

		print("\nChecking fixed investment ...")

		start_capital1 = self.Investment1.getStartingCapital()
		capital1, dias1, ganhos1 = self.Investment1.getWinnings('01/07/2019','31/12/2019')
		print(start_capital1,capital1,dias1,capital1-start_capital1)

		start_capital2 = self.Investment2.getStartingCapital()
		capital2, dias2, ganhos2 = self.Investment2.getWinnings('01/07/2019','31/12/2019')
		print(self.Investment2.getStartingCapital(),capital2,dias2, capital2-start_capital2)

		start_capital3 = self.Investment3.getStartingCapital()
		capital3, dias3, ganhos3 = self.Investment3.getWinnings('01/07/2019','31/12/2019')
		print(self.Investment3.getStartingCapital(),capital3,dias3, capital3-start_capital3)

		sys.stdout.flush()


class TestCDIInvestment(unittest.TestCase):

	def setUp(self):
		self.Investment = Investimento(10000)
		self.Investment.setCDI(0.85)

	def test_010_CDI(self):

		print("\nChecking CDI investment...")
		
		capital, dias, ganhos = self.Investment.getWinnings('18/02/2019','13/02/2020')

		print(self.Investment.getStartingCapital(),capital,dias)
		sys.stdout.flush()

		# self.assertEqual(selic, 'FOO')

	#def test_isupper(self):
	#   self.assertTrue('FOO'.isupper())
	#  self.assertFalse('Foo'.isupper())

	#def test_split(self):
	#   s = 'hello world'
	#  self.assertEqual(s.split(), ['hello', 'world'])
	# check that s.split fails when the separator is not a string
	# with self.assertRaises(TypeError):
	#    s.split(2)

class TestIPCAInvestment(unittest.TestCase):

	def setUp(self):
		self.Investment1 = Investimento(4652.98)
		self.Investment1.setFixed(3.71)

		self.Investment2 = Investimento(4743.20)
		self.Investment2.setFixed(3.61)
		
	def test_010_CDI(self):

		print("\nChecking IPCA investment...")
		
		start_capital1 = self.Investment1.getStartingCapital()
		capital1, dias1, ganhos1 = self.Investment1.getWinnings('19/07/2019','15/01/2020')
		print(start_capital1,capital1,dias1,capital1-start_capital1)

		start_capital2 = self.Investment2.getStartingCapital()
		capital2, dias2, ganhos2 = self.Investment2.getWinnings('07/08/2019','15/01/2020')
		print(start_capital2,capital2,dias2,capital2-start_capital2)		

		sys.stdout.flush()

		# self.assertEqual(selic, 'FOO')

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