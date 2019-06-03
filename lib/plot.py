
import numpy as np
import math
import matplotlib.pyplot as plt
import csv

def plotIV(fileName, title):
	with open(fileName, 'r') as csvfile:
		rows = csv.reader(csvfile, delimiter=',')
		x = []
		y = []
		for row in rows:
			x.append(float(row[0]))
			y.append(abs(float(row[1])))

		fig = plt.figure()
		plt.plot(x, y)
		plt.xlabel('Voltage (V)')
		plt.ylabel('Current (A/cm^2)')
		plt.title(title)
		plt.show()

		return fig

def plotLogIV(fileName, title):
	with open(fileName, 'r') as csvfile:
		rows = csv.reader(csvfile, delimiter=',')
		x = []
		y = []
		for row in rows:
			x.append(float(row[0]))
			y.append(math.log10(abs(float(row[1]))))

		fig = plt.figure()
		plt.plot(x, y)
		plt.xlabel('Voltage (V)')
		plt.ylabel('Log Current (Log(A/cm^2))')
		plt.title(title)
		plt.show()
		return fig

def plotPV(fileName, title):
	with open(fileName, 'r') as csvfile:
		rows = csv.reader(csvfile, delimiter=',')
		x = []
		y = []
		for row in rows:
			x.append(float(row[0]))
			y.append(abs(float(row[2])))

		fig = plt.figure()
		plt.plot(x, y)
		plt.xlabel('Voltage (V)')
		plt.ylabel('Power (W/cm^2)')
		plt.title(title)
		plt.show()
		return fig

def plotLogPV(fileName, title):
	with open(fileName, 'r') as csvfile:
		rows = csv.reader(csvfile, delimiter=',')
		x = []
		y = []
		for row in rows:
			x.append(float(row[0]))
			y.append(math.log10(abs(float(row[2]))))

		fig = plt.figure()
		plt.plot(x, y)
		plt.xlabel('Voltage (V)')
		plt.ylabel('Log Power (Log(W/cm^2))')
		plt.title(title)
		plt.show()
		return fig

def plotGV(fileName, title):
	with open(fileName, 'r') as csvfile:
		rows = csv.reader(csvfile, delimiter=',')
		x = []
		y = []
		for row in rows:
			x.append(float(row[0]))
			y.append(float(row[3]))

		fig = plt.figure()
		plt.plot(x, y)
		plt.xlabel('Voltage (V)')
		plt.ylabel('Gain (1/cm)')
		plt.title(title)
		plt.show()
		return fig
