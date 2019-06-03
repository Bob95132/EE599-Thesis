from devsim import *
from util.model import *
from util.model_create import *
from util.model_factory import *
import sympy
import mpmath
from sympy.solvers.solveset import _transolve
import scipy.linalg
from scipy.optimize import root
import numpy as np
import cmath
import math

class Solver:

	def __init__(self, nodeSize):
		self._nodeSize = nodeSize
		self._rhs = np.zeros(nodeSize, dtype=complex)
		self._matrix = np.zeros((nodeSize, nodeSize), dtype=complex)

	def AddMatrixVal(self, row, col, value):
		self._matrix[row][col] = value
	
	def Solve(self):
		self.GenerateMatrix()
		self.GenerateBC()
		if not np.any(self._rhs):
			weights, vectors = scipy.linalg.eig(self._matrix)
			index = list(weights).index(min(weights))
			self._sol = vectors[index]
		else:
			invMatrix = np.linalg.inv(self._matrix)
			self._sol = invMatrix * self._rhs

	def GetSolution(self):
		return self._sol

class HelmholtzSolver(Solver):
	boundaryTypes = ('Reflecting', 'Sommerfield')

	def __init__(self, device, frequency_0, activeRegion):
		self._device = device
		self._frequency = float(frequency_0)
		self._frequencyStr = frequency_0
		self._sbeta = sympy.Symbol('x', real=True)
		self._beta = 0
		self._activeRegion = activeRegion
		self._refractiveIndices = []
		self._boundaries = {}

		self._dimension = get_dimension(device=device)
		if self._dimension > 1:
			raise NotImplementedError

		nodeSize = 0
		
		self._positions = []

		for region in get_region_list(device=device):
			self._positions.extend(get_node_model_values(device=device, region=region, name="x"))

		self._positions = sorted(self._positions)
		nodeSize = len(self._positions)

		for region in get_region_list(device=device):

			positions = get_node_model_values(device=device, region=region, name="x")
			#get boundaries 
			boundaries = get_node_model_values(device=device, region=region, name="OpticalDensityBoundary_"+self._frequencyStr) 
						
			for index, val in enumerate(boundaries):
				if val > 0 and val < len(HelmholtzSolver.boundaryTypes):
					trueIndex = self._positions.index(positions[index])		
					self.SetBoundary(trueIndex, HelmholtzSolver.boundaryTypes[int(val) - 1])

			 #get nodes	
				
		super(HelmholtzSolver, self).__init__(nodeSize)
		self.GenerateModeIndices()

	def Update(self):
		self.GenerateRefractiveIndices()
		
	def GetContactComplexRefractiveIndex(self, contact):
		models = ("n_" + self._frequencyStr,
					 "k_" + self._frequencyStr)

		opticalParams = []
		for model in models:
			opticalParams.append(float(get_db_entry(material=get_material(device=self._device, contact=contact), parameter=model)[0]))

		opticalParams.append(((pow(opticalParams[0], 2) - pow(opticalParams[1], 2)) + 2*1j*opticalParams[0]*opticalParams[1]))

		return opticalParams

	def GetRegionComplexRefractiveIndex(self, region):
		models = ("n_" + self._frequencyStr,
					 "k_" + self._frequencyStr)

		opticalParams = []
		for model in models:
			opticalParams.append(float(get_db_entry(material=get_material(device=self._device, region=region), parameter=model)[0]))

		opticalParams.append(((pow(opticalParams[0], 2) - pow(opticalParams[1], 2)) + 2*1j*opticalParams[0]*opticalParams[1]))

		return opticalParams

	def GetContactIndices(self):
		for contact in get_contact_list(device=self._device):
			#get complex index of refraction
			contactIndex = self.GetContactComplexRefractiveIndex(contact)[0] ** 2
			#only 1 region per contact
			region = get_region_list(device=self._device, contact=contact)[0]			
			regionIndex = self.GetRegionComplexRefractiveIndex(region)[0] ** 2
			#1-dimensional
			
			positions = []
			position = get_node_model_values(device=self._device, region=region, name="x")
			for val in get_element_node_list(device=self._device, region=region, contact=contact):
				positions.append(position[val[0]])
			
			fposition = sum(positions)/len(positions)
			self._refractiveIndices.append((fposition, contactIndex, regionIndex, "Contact"))	
			
	def GetInterfaceIndices(self):
		for interface in get_interface_list(device=self._device):
			indices = []
			position = []
			for region in get_region_list(device=self._device, interface=interface):
				indices.append(self.GetRegionComplexRefractiveIndex(region)[2])
				elementList = get_element_node_list(device=self._device, region=region, interface=interface)[0]			
				position = get_node_model_values(device=self._device, region=region, name="x")[elementList]

			avgPosition = sum(positions)/len(positions)
			self._refractiveIndices.append((position, indices[0], indices[1], "Interface"))
			
	def GenerateModeIndices(self):
		#+2 for contacts
		self.GetContactIndices()
		self.GetInterfaceIndices()

		k_0 = 2 * math.pi * self._frequency / 3e8
		def transcendental(x):
			length = 2*len(get_region_list(device=self._device)) + 2
			modalMatrix = np.zeros((length, length), dtype='complex')
			self._refractiveIndices.sort(key=lambda x: x[0], reverse=True)
			for index, indices in enumerate(self._refractiveIndices):
				position = indices[0]
				#k0 = indices[1]
				#k1 = indices[2]
				boundTypes = indices[3]
				if boundTypes == "Contact":
					k0 = cmath.sqrt(x**2 - (k_0*indices[1])**2)
					k1 = cmath.sqrt((k_0*indices[2])**2 - x**2)
					#may not be the best way... to establish flipping of signs for contacts
					if index == len(self._refractiveIndices) - 1:
						modalMatrix[2*index,index] = cmath.exp(-1j*k1*position)
						modalMatrix[2*index,index+1] = cmath.exp(1j*k1*position)
						modalMatrix[2*index,index+2] = -1 
						modalMatrix[2*index+1,index] = k1*cmath.exp(-1j*k1*position)
						modalMatrix[2*index+1,index+1] = -k1*cmath.exp(1j*k1*position)
						modalMatrix[2*index+1,index+2] = -1j * k0
					else:
						modalMatrix[2*index,index] = -1
						modalMatrix[2*index,index+1] = cmath.exp(-1j*k1*position)
						modalMatrix[2*index,index+2] = cmath.exp(1j*k1*position)
						modalMatrix[2*index+1,index] = 1j * k0
						modalMatrix[2*index+1,index+1] = k1*cmath.exp(-1j*k1*position)
						modalMatrix[2*index+1,index+2] = -k1*cmath.exp(1j*k1*position)
						
				elif boundTypes == "Interface":
					k0 = cmath.sqrt((k_0*indices[1])**2 - x**2)
					k1 = cmath.sqrt((k_0*indices[2])**2 - x**2)
					modalMatrix[2*index , index] = cmath.exp(-1j*k0*position)
					modalMatrix[2*index , index+1] = cmath.exp(1j*k0*position)
					modalMatrix[2*index , index+2] = cmath.exp(-1j*k1*position)
					modalMatrix[2*index , index+3] = cmath.exp(1j*k1*position)
					modalMatrix[2*index , index] = -1j*k0*cmath.exp(-1j*k0*position)
					modalMatrix[2*index , index+1] = 1j*k0*cmath.exp(1j*k0*position)
					modalMatrix[2*index , index+2] = -1j*k1*cmath.exp(-1j*k1*positin)
					modalMatrix[2*index , index+3] = 1j*k1*cmath.exp(1j*k1*position)
	
				else:
					print("Do not recognize boundary type")

			return (scipy.linalg.det(modalMatrix) * 1j).real

		self._beta = scipy.optimize.newton(transcendental, k_0 * self.GetRegionComplexRefractiveIndex(self._activeRegion)[0])
		self._neff = self._beta / k_0


	#does not include free carrier loss or line width broadening
	def GenerateRefractiveIndices(self):
		self._complexRefIndex = []
		for region in get_region_list(device=self._device):
			opticalParams = self.GetRegionComplexRefractiveIndex(region)
			absorptionLoss = 4 * math.pi * opticalParams[1] * self._frequency / 3e8
			waveNumber_0 = 2 * math.pi * self._frequency / 3e8
			position = get_node_model_values(device=self._device, region=region, name="x")
			gain = get_node_model_values(device=self._device, region=region, name="PhotonLocalGain_"+self._frequencyStr)

			for index, g in enumerate(gain):
				trueIndex = self._positions.index(position[index])
				self._complexRefIndex.insert(trueIndex, (waveNumber_0**2 * (opticalParams[0] + opticalParams[1] + (-(1j * (g-absorptionLoss)) / waveNumber_0))**2) - pow(self._beta,2))

	def SetBoundary(self, index, boundaryType):
		if boundaryType in HelmholtzSolver.boundaryTypes:
			self._boundaries[index] = boundaryType
		else:
			raise NotImplementedError

	def GenerateBoundary(self, index, boundaryType):
		if boundaryType in 'Reflecting':
			self.AddMatrixVal(index, index, 1)
		elif boundaryType in 'Sommerfield':
			if index == self._nodeSize - 1:
				edgeLength = self._positions[index] - self._positions[index - 1]
			else:
				edgeLength = self._positions[index + 1] - self._positions[index]

			self.AddMatrixVal(index, index, 1)
			self.AddMatrixVal(index, index - 1, 
				-(cmath.cos(cmath.sqrt(self._complexRefIndex[index])*edgeLength) + 
				1j*cmath.sin(cmath.sqrt(self._complexRefIndex[index])*edgeLength)))

	def GenerateMatrixRow(self, index):
		if self._dimension > 1:
			raise NotImplementedError
		elif self._dimension == 1:
			if index == self._nodeSize - 1:
				edgeLength = self._positions[index] - self._positions[index - 1]
			else:
				edgeLength = self._positions[index + 1] - self._positions[index]
			self.AddMatrixVal(index, index - 1, -1 / pow(edgeLength, 2))
			self.AddMatrixVal(index, index + 1, -1 / pow(edgeLength,2))
			self.AddMatrixVal(index, index, 2 * cmath.cos(cmath.sqrt(self._complexRefIndex[index]) * edgeLength) / pow(edgeLength, 2))

	def GenerateMatrix(self):
		for index in range(0, self._nodeSize):
			if index not in list(self._boundaries.keys()):
				self.GenerateMatrixRow(index)

	def GenerateBC(self):
		for key, val in self._boundaries.items():
			self.GenerateBoundary(key, val)

	def ExportOpticalDensity(self):
		for region in get_region_list(device=self._device):
			opticalDensity = "OpticalDensity_"+self._frequencyStr
			nEff = "n_eff_"+self._frequencyStr
			if not InNodeModelList(self._device, region, opticalDensity):
				CreateSolution(self._device, region, opticalDensity)

			if not InNodeModelList(self._device, region, nEff):
				CreateSolution(self._device, region, nEff)

			set_node_value(device=self._device, region=region, name=nEff, value=self._neff) 

			positions = get_node_model_values(device=self._device, region=region, name="x")
			for index, val in enumerate(positions):
				trueIndex = self._positions.index(val)
				set_node_value(device=self._device, region=region, 
									name=opticalDensity, index=index,
									value=float((pow(abs(self._sol[trueIndex]), 2))))
				

			
			
	def Solve(self):
		self.Update()
		super(HelmholtzSolver, self).Solve()
		self.ExportOpticalDensity()		
		
		
