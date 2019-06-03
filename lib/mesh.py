import numpy as np

def OneDOneMaterial(num_nodes, node_size):
	physicalNames = ["Base", "Bulk", "Emitter"]
	coordinates = []
	elements = []
	for x in range(0, num_nodes):
		coordinates.extend([float(x)*node_size, 0.0, 0.0])
		if x != num_nodes - 1:
			elements.extend([1,1,x,x+1])

	elements.extend(([0, 0, 0]))
	elements.extend(([0, 2, num_nodes-1]))
	return (physicalNames, coordinates, elements)


