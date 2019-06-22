#!/usr/bin/python3

import os
import sys
import argparse
import math
import subprocess
import urllib3
import datetime
import json

from class_ganhos import Investiment

from urllib.parse import urlencode

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

parser.add_argument('--tipo', 
	metavar='N',
	type=str, 
	choices = ['CDI','Fixo'],
	nargs='+',
    help='tipo de investimento (Fixo/CDI)')	

parser.add_argument('--taxa', 
	metavar='N',
	type=float, 
	nargs='+',
    help='taxa de juros. Quando investimento eh fixo, ')

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
tipo = args.tipo

print(args)

debug = False

Investimento = Investiment()
if tipo == 'Fixo':
	Investimento.setFixed(taxa)
elif tipo == 'CDI':
	Investimento.setCDI(taxa)

Investimento.setStartingCapital(capital)

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
sys.stdout.write("Tipo de investimento: " + str(tipo) + '\n')
sys.stdout.write("Capital: " + str(capital) + '\n')
sys.stdout.write("Taxa contratada: " + str(taxa) + '\n')
sys.stdout.write("Data inicial do investimento: " + str(start) + '\n')
sys.stdout.write("Data final do investimento: " + str(end) + '\n')

capital, dias_corridos, ganho_diario = Investimento.getWinnings(start,end)

sys.stdout.write("Capital final: " + str(capital) + '\n')
sys.stdout.write("Dias corridos: " + str(dias_corridos) + '\n')
sys.stdout.write("Evolucao diaria: " + str(ganho_diario) + '\n')

