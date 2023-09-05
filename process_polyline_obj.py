import numpy as np
import os


class ccx_writer:

	def __init__(self, nodes, elements):

		self.v = nodes
		self.el = elements
		self.nsets = {"id": ["NAll"], "group":[list(np.arange(self.v.shape[0]) + 1)]}
		self.elsets = {"id": ["EAll"], "group":[list(np.arange(self.el.shape[0]) + 1)]}
		self.bounds = {"id": [], "constraints":[]}
		self.loads = {"id": [], "direction":[], "magnitude":[]}

	def add_new_nodeset(self, ID, indices):

		self.nsets["id"].append(ID)
		self.nsets["group"].append(indices)

	def add_new_elset(self, ID, indices):

		self.elsets["id"].append(ID)
		self.elsets["group"].append(indices)

	def define_bound_set(self, ID, constraints):

		self.bounds["id"].append(ID)
		self.bounds["constraints"].append(constraints)

	def define_load_set(self, ID, direction, magnitude):

		self.loads["id"].append(ID)
		self.loads["direction"].append(direction)
		self.loads["magnitude"].append(magnitude)

	def write(self, filename = "output.inp"):

		f = open(filename, 'w')

		f.write("*NODE,NSET=NAll\n")
		for i in range(self.v.shape[0]):
			v = self.v[i]
			f.write(str(i + 1) + "," + str(int(v[0] * 1000)/1000) + "," + str(int(v[1] * 1000)/1000) + "," + 
				str(int(v[2] * 1000)/1000) + "\n")

		f.write("\n")
		f.write("*ELEMENT,TYPE=B31,ELSET=EAll\n")
		for i in range(self.el.shape[0]):
			el = self.el[i]
			el[:] = el[:] + 1
			f.write(str(i + 1) + "," + str(el[0]) + "," + str(el[1]) + "\n")

		f.write("\n")
		for i in range(len(self.nsets["id"])):
			if self.nsets["id"][i] != "NAll":
				f.write("*NSET, NSET=" + self.nsets["id"][i] + "\n")
				for j in range(len(self.nsets["group"][i])):
					f.write(str(self.nsets["group"][i][j]))
					if j < len(self.nsets["group"][i]) - 1:
						f.write(",")
					else:
						f.write("\n")

		f.write("\n")
		for i in range(len(self.elsets["id"])):
			if self.elsets["id"][i] != "EAll":
				f.write("*ELSET, ELSET=" + self.elsets["id"][i] + "\n")
				for j in range(len(self.elsets["group"][i])):
					f.write(str(self.elsets["group"][i][j]))
					if j < len(self.elsets["group"][i]) - 1:
						f.write(",")
					else:
						f.write("\n")

		f.write("\n")
		f.write("*BOUNDARY\n")
		for i in range(len(self.bounds["id"])):
			if self.bounds["id"][i] not in self.nsets["id"]:
				print("Aborted! " + self.bounds["id"] + " boundary set does not exist as a node set!!!!")
				return
			for j in range(len(self.bounds["constraints"][i])):
				f.write(self.bounds["id"][i] + "," + str(self.bounds["constraints"][i][j]) + "\n")

		f.write("\n")
		f.write("*MATERIAL,NAME=ALUM\n*ELASTIC\n1E7,.3\n*DENSITY\n2710.0\n")
		
		f.write("\n")
		f.write("*BEAM SECTION,ELSET=EAll,MATERIAL=ALUM,SECTION=RECT\n")
		f.write(".25,.25\n0.,1.,0.\n")

		f.write("\n")
		f.write("*STEP\n")
		f.write("*STATIC\n")
		f.write("*CLOAD\n")

		for i in range(len(self.loads["id"])):
			if self.loads["id"][i] not in self.nsets["id"]:
				print("Aborted! " + self.loads["id"] + " load set does not exist as a node set!!!!")
				return
			f.write(self.loads["id"][i] + "," + str(self.loads["direction"][i]) + "," 
				+ str(self.loads["magnitude"][i]) +"\n")

		f.write("\n")
		f.write("*DLOAD\n")
		f.write("EAll, GRAV, 9.810, 0,0,-1\n")

		f.write("\n")
		f.write("*EL PRINT,ELSET=Eall,FREQUENCY=100\n")
		f.write("S\n")
		f.write("*NODE FILE\n")
		f.write("U\n")
		f.write("*EL FILE\n")
		f.write("S\n")
		f.write("*END STEP")

		f.close()





def read_obj_members(filename):

	f = open(filename, 'r')
	lines = f.read().split("\n")

	crvs = []
	crv = []
	pts = []
	for line in lines:
		if "end" in line:
			crvs.append(crv)
			crv = []
		elif "v " in line and "c" not in line:
			info = line.split(" ")
			pt = [float(info[1]), float(info[2]), float(info[3])]
			pts.append(pt)
			crv.append(pt)

	crvs = np.array(crvs)
	pts = np.array(pts)

	return crvs, pts



def remove_duplicate_pts(pts):

	unique = np.array([pts[0]])
	picked = [0]

	for i in range(pts.shape[0]):

		if i not in picked:
			
			vectors = unique - pts[i]
			distances = np.linalg.norm(vectors, axis = 1)
			indices = np.where(distances < 0.01)[0]
			
			if len(indices) == 0:
				unique = np.append(unique, [pts[i]], axis = 0)

			vectors = pts - pts[i]
			distances = np.linalg.norm(vectors, axis = 1)
			indices = np.where(distances < 0.01)[0]
			picked.extend(indices)

	return unique


def index_members(crvs, v):

	elements = np.zeros((crvs.shape[0], crvs.shape[1]))

	for i in range(crvs.shape[0]):
		for j in range(crvs.shape[1]):
			vectors = v - crvs[i, j]
			distances = np.linalg.norm(vectors, axis = 1)
			elements[i, j] = np.where(distances < 0.01)[0][0]

	return elements



def main(filename):

	members, pts = read_obj_members(filename)

	nodes = remove_duplicate_pts(pts)
	elements = index_members(members, nodes)

	print(nodes)

	myCCX = ccx_writer(nodes, elements.astype(int))
	base = np.where(nodes[:,2] < 0.01)[0]
	
	myCCX.add_new_nodeset("BASE", base)
	myCCX.add_new_nodeset("TORSO", [np.argmax(nodes[:,2])])
	myCCX.define_bound_set("BASE", [1, 2, 3])
	myCCX.define_load_set("TORSO", 2, -444)

	myCCX.write("src/" + os.path.splitext(filename)[0] + ".inp")



main("bboy_kneel_leaned.obj")