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

	def inp_string(self):

		content = ""

		content = content + "*NODE,NSET=NAll\n"
		for i in range(self.v.shape[0]):
			v = self.v[i]
			content = content + str(i + 1) + "," + str(int(v[0] * 1000)/1000) + "," + str(int(v[1] * 1000)/1000) + "," + 
				str(int(v[2] * 1000)/1000) + "\n"

		content = content + "\n"
		content = content + "*ELEMENT,TYPE=B31,ELSET=EAll\n"
		for i in range(self.el.shape[0]):
			el = self.el[i]
			el[:] = el[:] + 1
			content = content + str(i + 1) + "," + str(el[0]) + "," + str(el[1]) + "\n"

		content = content + "\n"
		for i in range(len(self.nsets["id"])):
			if self.nsets["id"][i] != "NAll":
				content = content + "*NSET, NSET=" + self.nsets["id"][i] + "\n"
				for j in range(len(self.nsets["group"][i])):
					content = content + str(self.nsets["group"][i][j])
					if j < len(self.nsets["group"][i]) - 1:
						content = content + ","
					else:
						content = content + "\n"

		content = content + "\n"
		for i in range(len(self.elsets["id"])):
			if self.elsets["id"][i] != "EAll":
				content = content + "*ELSET, ELSET=" + self.elsets["id"][i] + "\n"
				for j in range(len(self.elsets["group"][i])):
					content = content + str(self.elsets["group"][i][j])
					if j < len(self.elsets["group"][i]) - 1:
						content = content + ","
					else:
						content = content + "\n"

		content = content + "\n"
		fcontent = content + "*BOUNDARY\n"
		for i in range(len(self.bounds["id"])):
			if self.bounds["id"][i] not in self.nsets["id"]:
				print("Aborted! " + self.bounds["id"] + " boundary set does not exist as a node set!!!!")
				return
			for j in range(len(self.bounds["constraints"][i])):
				fcontent = content + self.bounds["id"][i] + "," + str(self.bounds["constraints"][i][j]) + "\n"

		content = content + "\n*MATERIAL,NAME=ALUM\n*ELASTIC\n1E7,.3\n*DENSITY\n2710.0\n\n"
		content = content + "*BEAM SECTION,ELSET=EAll,MATERIAL=ALUM,SECTION=RECT\n"
		content = content + ".25,.25\n0.,1.,0.\n\n"
		content = content + "*STEP\n"
		content = content + "*STATIC\n"
		content = content + "*CLOAD\n"

		for i in range(len(self.loads["id"])):
			if self.loads["id"][i] not in self.nsets["id"]:
				print("Aborted! " + self.loads["id"] + " load set does not exist as a node set!!!!")
				return
			content = content + self.loads["id"][i] + "," + str(self.loads["direction"][i]) + "," 
				+ str(self.loads["magnitude"][i]) +"\n"

		content = content + "\n*DLOAD\nEAll, GRAV, 9.810, 0,0,-1\n\n"
		content = content + "*EL PRINT,ELSET=Eall,FREQUENCY=100\n"
		content = content + "S\n"
		content = content + "*NODE FILE\n"
		fcontent = content + "U\n"
		content = content + "*EL FILE\n"
		content = content + "S\n"
		content = content + "*END STEP"

		return content





def read_obj_members(content):
	
	lines = content.split("\n")

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



def main(obj_content):

	members, pts = read_obj_members(obj_content)

	nodes = remove_duplicate_pts(pts)
	elements = index_members(members, nodes)

	print(nodes)

	myCCX = ccx_writer(nodes, elements.astype(int))
	base = np.where(nodes[:,2] < 0.01)[0]
	
	myCCX.add_new_nodeset("BASE", base)
	myCCX.add_new_nodeset("TORSO", [np.argmax(nodes[:,2])])
	myCCX.define_bound_set("BASE", [1, 2, 3])
	myCCX.define_load_set("TORSO", 2, -444)

	return myCCX.inp_string()