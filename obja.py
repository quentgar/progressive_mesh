#!/usr/bin/env python3

import sys
import numpy as np
import random

"""
obja model for python.
"""

class Face:
    """
    The class that holds a, b, and c, the indices of the vertices of the face.
    """
    def __init__(self, a, b, c, at, bt, ct, an, bn, cn, visible = True):
        self.a = a
        self.b = b
        self.c = c

        self.at = at
        self.bt = bt
        self.ct = ct

        self.an = an
        self.bn = bn
        self.cn = cn

        self.visible = visible

    def from_array(array):
        """
        Initializes a face from an array of strings representing vector indices (starting at 1)
        """
        face = Face(0, 0, 0, 0, 0, 0, 0, 0, 0)
        face.set(array)
        face.visible = True
        return face

    def set(self, array):
        """
        Sets a face from an array of strings representing vector indices (starting at 1)
        """
        self.a = int(array[0].split('/')[0]) - 1
        self.b = int(array[1].split('/')[0]) - 1
        self.c = int(array[2].split('/')[0]) - 1

        self.at = int(array[0].split('/')[1]) - 1
        self.bt = int(array[1].split('/')[1]) - 1
        self.ct = int(array[2].split('/')[1]) - 1

        self.an = int(array[0].split('/')[2]) - 1
        self.bn = int(array[1].split('/')[2]) - 1
        self.cn = int(array[2].split('/')[2]) - 1
        return self

    def clone(self):
        """
        Clones a face from another face
        """
        return Face(self.a, self.b, self.c, self.at, self.bt, self.ct, self.an, self.bn, self.cn, self.visible)

    def copy(self, other):
        """
        Sets a face from another face
        """
        self.a = other.a
        self.b = other.b
        self.c = other.c

        self.at = other.at
        self.bt = other.bt
        self.ct = other.ct

        self.an = other.an
        self.bn = other.bn
        self.cn = other.cn

        self.visible = other.visible
        return self

    def test(self, vertices, line = "unknown"):
        """
        Tests if a face references only vertices that exist when the face is declared.
        """
        if self.a >= len(vertices):
            raise VertexError(self.a + 1, line)
        if self.b >= len(vertices):
            raise VertexError(self.b + 1, line)
        if self.c >= len(vertices):
            raise VertexError(self.c + 1, line)

    def __str__(self):
        return "Face(V : ({}, {}, {}), VT : ({}, {}, {}), VN : ({}, {}, {}))".format(self.a, self.b, self.c,
                                                                 self.at, self.bt, self.ct,
                                                                 self.an, self.bn, self.cn)

    def __repr__(self):
        return str(self)

class VertexError(Exception):
    """
    An operation references a vertex that does not exist.
    """
    def __init__(self, index, line):
        """
        Creates the error from index of the referenced vertex and the line where the error occured.
        """
        self.line = line
        self.index = index
        super().__init__()

    def __str__(self):
        """
        Pretty prints the error.
        """
        return f'There is no vector {self.index} (line {self.line})'

class FaceError(Exception):
    """
    An operation references a face that does not exist.
    """
    def __init__(self, index, line):
        """
        Creates the error from index of the referenced face and the line where the error occured.
        """
        self.line = line
        self.index = index
        super().__init__()

    def __str__(self):
        """
        Pretty prints the error.
        """
        return f'There is no face {self.index} (line {self.line})'

class FaceVertexError(Exception):
    """
    An operation references a face vector that does not exist.
    """
    def __init__(self, index, line):
        """
        Creates the error from index of the referenced face vector and the line where the error occured.
        """
        self.line = line
        self.index = index
        super().__init__()

    def __str__(self):
        """
        Pretty prints the error.
        """
        return f'Face has no vector {self.index} (line {self.line})'

class UnknownInstruction(Exception):
    """
    An instruction is unknown.
    """
    def __init__(self, instruction, line):
        """
        Creates the error from instruction and the line where the error occured.
        """
        self.line = line
        self.instruction = instruction
        super().__init__()

    def __str__(self):
        """
        Pretty prints the error.
        """
        return f'Instruction {self.instruction} unknown (line {self.line})'

class Model:
    """
    The OBJA model.
    """
    def __init__(self):
        """
        Intializes an empty model.
        """
        self.vertices = []
        self.faces = []
        self.textures = []
        self.normals = []
        self.edges = []
        self.line = 0

    def compute_edges(self):
        """
        Obtenir toutes les arretes (edges) à partir des faces
        Format edge : np.array([v1, v2, f1, f2])
        """

        for i,face in enumerate(self.faces):
            list_edges = []
            list_edges.append(np.array([face.a, face.b, i]))
            list_edges.append(np.array([face.b, face.c, i]))
            list_edges.append(np.array([face.c, face.a, i]))

            for e in list_edges:
                # Si l'arrete n'est pas déjà dans la liste, l'ajouter (eviter (1,2) en plus de (2,1))
                if not (any((e[0:2] == x[0:2]).all() for x in self.edges) or any((np.flip(e)[1:3] == x[0:2]).all() for x in self.edges)):
                    self.edges.append(e)
                else:
                    t = [(x[0], x[1]) for x in self.edges]
                    if (e[0], e[1]) in t:
                        ind = t.index((e[0], e[1]))
                    else:
                        ind = t.index((e[1], e[0]))
                    f = self.edges[ind][2]  # Récupérer la première face enregistrée
                    self.edges[ind] = np.array([e[0], e[1], f, i])

    def get_boundary_edges(self):
        """
        Renvoie les indices des boundary edges sous forme de liste
        """
        size_list = [x.size for x in self.edges]  # Liste des tailles de chaque element edge
        ind_list = [i for i, x in enumerate(size_list) if x == 3]  # Récupérer les indices des elements de taille 3 (1 face)

        return ind_list

    def get_sharp_edges(self, err_t=1e-3, err_n=1e-3):
        """
        Renvoie les indices des sharp edges sous forme de  liste
        """
        boundary_list = self.get_boundary_edges()

        sharp_list = boundary_list

        for i, e in enumerate(self.edges):
            if i not in boundary_list:  # Les boundary edges sont des sharp edges
                f1, f2 = e[2], e[3]  # Test différence des attributs discrets des faces adjacentes
                face1 = self.faces[f1]
                face2 = self.faces[f2]
                at1, bt1, ct1 = face1.at, face1.bt, face1.ct
                at2, bt2, ct2 = face2.at, face2.bt, face2.ct

                t1 = np.concatenate((self.textures[at1], self.textures[bt1], self.textures[ct1]))
                t2 = np.concatenate((self.textures[at2], self.textures[bt2], self.textures[ct2]))

                diff = np.sum(np.square(t1-t2))  # Comparer cette erreur à un certain seuil ?

                if diff > err_t:  # Si différence supérieure à un certain seuil --> sharp edge
                    sharp_list.append(i)

                else:  # Sinon test avec les attributs scalaires des wedges adjacents

                    if face1.a == e[0]:  # n11 normale associée à la face 1 et e[0]=v1
                        n11 = face1.an
                    elif face1.b == e[0]:
                        n11 = face1.bn
                    else:
                        n11 = face1.cn

                    if face1.a == e[1]:  # n12 normale associée à la face 1 et e[1]=v2
                        n12 = face1.an
                    elif face1.b == e[1]:
                        n12 = face1.bn
                    else:
                        n12 = face1.cn

                    if face2.a == e[0]:  # n21 normale associée à la face 2 et e[0]=v1
                        n21 = face2.an
                    elif face2.b == e[0]:
                        n21 = face2.bn
                    else:
                        n21 = face2.cn

                    if face2.a == e[1]:  # n22 normale associée à la face 2 et e[1]=v2
                        n22 = face2.an
                    elif face2.b == e[1]:
                        n22 = face2.bn
                    else:
                        n22 = face2.cn

                    n1 = np.concatenate((self.normals[n11], self.normals[n12]))
                    n2 = np.concatenate((self.normals[n21], self.normals[n22]))

                    diff = np.square(n1-n2)

                    if (np.sum(diff[:3]) > err_n) or (np.sum(diff[3:]) > err_n):
                        sharp_list.append(i)

        return sharp_list

    def get_base_edges(self, epsilon, err_t=1e-3, err_n=1e-3):
        """
        Renvoie les indices des base edges de niveau i
        """
        sharp_list = self.get_sharp_edges(err_t, err_n)

        base_list = []

        for i, e in enumerate(self.edges):
            if i not in sharp_list:
                f1, f2 = e[2], e[3]  # Test différence des attributs scalaires des wedges adjacentes
                face1 = self.faces[f1]
                face2 = self.faces[f2]

                if face1.a == e[0]:  # n11 normale associée à la face 1 et e[0]=v1
                    n11 = face1.an
                elif face1.b == e[0]:
                    n11 = face1.bn
                else:
                    n11 = face1.cn

                if face1.a == e[1]:  # n12 normale associée à la face 1 et e[1]=v2
                    n12 = face1.an
                elif face1.b == e[1]:
                    n12 = face1.bn
                else:
                    n12 = face1.cn

                if face2.a == e[0]:  # n21 normale associée à la face 2 et e[0]=v1
                    n21 = face2.an
                elif face2.b == e[0]:
                    n21 = face2.bn
                else:
                    n21 = face2.cn

                if face2.a == e[1]:  # n22 normale associée à la face 2 et e[1]=v2
                    n22 = face2.an
                elif face2.b == e[1]:
                    n22 = face2.bn
                else:
                    n22 = face2.cn

                n1 = np.concatenate((self.normals[n11], self.normals[n12]))
                n2 = np.concatenate((self.normals[n21], self.normals[n22]))

                diff = np.square(n1 - n2)

                if (np.sum(diff[:3]) < err_n) and (np.sum(diff[3:]) < err_n): # Si les wedges ont les mêmes attributs scalaires
                    poids = np.sum(abs(self.normals[n11] - self.normals[n12]))
                    if poids > epsilon:
                        base_list.append(i)

        return base_list

    def get_edge_weight(self, edge_index):

        e = self.edges[edge_index]

        f1, f2 = e[2], e[3]  # Test différence des attributs scalaires des wedges adjacentes
        face1 = self.faces[f1]
        face2 = self.faces[f2]

        if face1.a == e[0]:  # n11 normale associée à la face 1 et e[0]=v1
            n11 = face1.an
        elif face1.b == e[0]:
            n11 = face1.bn
        else:
            n11 = face1.cn

        if face1.a == e[1]:  # n12 normale associée à la face 1 et e[1]=v2
            n12 = face1.an
        elif face1.b == e[1]:
            n12 = face1.bn
        else:
            n12 = face1.cn

        if face2.a == e[0]:  # n21 normale associée à la face 2 et e[0]=v1
            n21 = face2.an
        elif face2.b == e[0]:
            n21 = face2.bn
        else:
            n21 = face2.cn

        if face2.a == e[1]:  # n22 normale associée à la face 2 et e[1]=v2
            n22 = face2.an
        elif face2.b == e[1]:
            n22 = face2.bn
        else:
            n22 = face2.cn

        n1 = np.concatenate((self.normals[n11], self.normals[n12]))
        n2 = np.concatenate((self.normals[n21], self.normals[n22]))

        poids = np.sum(abs(self.normals[n11] - self.normals[n12]))

        return poids


    def get_vector_from_string(self, string):
        """
        Gets a vector from a string representing the index of the vector, starting at 1.

        To get the vector from its index, simply use model.vertices[i].
        """
        index = int(string) - 1
        if index >= len(self.vertices):
            raise FaceError(index + 1, self.line)
        return self.vertices[index]

    def get_face_from_string(self, string):
        """
        Gets a face from a string representing the index of the face, starting at 1.

        To get the face from its index, simply use model.faces[i].
        """
        index = int(string) - 1
        if index >= len(self.faces):
            raise FaceError(index + 1, self.line)
        return self.faces[index]

    def parse_file(self, path):
        """
        Parses an OBJA file.
        """
        with open(path, "r") as file:
            for line in file.readlines():
                self.parse_line(line)

    def parse_line(self, line):
        """
        Parses a line of obja file.
        """
        self.line += 1

        split = line.split()

        if len(split) == 0:
            return

        if split[0] == "v":
            self.vertices.append(np.array(split[1:], np.double))

        elif split[0] == "vt":
            self.textures.append(np.array(split[1:], np.double))

        elif split[0] == "vn":
            self.normals.append(np.array(split[1:], np.double))

        elif split[0] == "ev":
            self.get_vector_from_string(split[1]).set(split[2:])

        elif split[0] == "tv":
            self.get_vector_from_string(split[1]).translate(split[2:])

        elif split[0] == "f" or split[0] == "tf":
            for i in range(1, len(split) - 2):
                face = Face.from_array(split[i:i+3])
                face.test(self.vertices, self.line)
                self.faces.append(face)

        elif split[0] == "ts":
            for i in range(1, len(split) - 2):
                if i % 2 == 1:
                    face = Face.from_array([split[i], split[i + 1], split[i + 2]])
                else:
                    face = Face.from_array([split[i], split[i + 2], split[i + 1]])
                face.test(self.vertices, self.line)
                self.faces.append(face)

        elif split[0] == "ef":
            self.get_face_from_string(split[1]).set(split[2:])

        elif split[0] == "efv":
            face = self.get_face_from_string(split[1])
            vector = int(split[2])
            new_index = int(split[3]) - 1
            if vector == 1:
                face.a = new_index
            elif vector == 2:
                face.b = new_index
            elif vector == 3:
                face.c = new_index
            else:
                raise FaceVertexError(vector, self.line)

        elif split[0] == "df":
            self.get_face_from_string(split[1]).visible = False

        elif split[0] == "#":
            return

        else:
            return
            # raise UnknownInstruction(split[0], self.line)

def parse_file(path):
    """
    Parses a file and returns the model.
    """
    model = Model()
    model.parse_file(path)
    return model

class Output:
    """
    The type for a model that outputs as obja.
    """
    def __init__(self, output, random_color = False):
        """
        Initializes the index mapping dictionnaries.
        """
        self.vertex_mapping = dict()
        self.face_mapping = dict()
        self.edge_mapping = dict()
        self.output = output
        self.random_color = random_color

    def add_vertex(self, index, vertex):
        """
        Adds a new vertex to the model with the specified index.
        """
        self.vertex_mapping[index] = len(self.vertex_mapping)
        print('v {} {} {}'.format(vertex[0], vertex[1], vertex[2]), file = self.output)

    def edit_vertex(self, index, vertex):
        """
        Changes the coordinates of a vertex.
        """
        if len(self.vertex_mapping) == 0:
            print('ev {} {} {} {}'.format(index, vertex[0], vertex[1],vertex[2]), file = self.output)
        else:
            print('ev {} {} {} {}'.format(self.vertex_mapping[index] + 1, vertex[0], vertex[1],vertex[2]), file = self.output)

    def add_edge(self, index, edge):
        """
        Adds an edge to the model
        """
        self.edge_mapping[index] = len(self.edge_mapping)
        print('l {} {}'.format(edge[0], edge[1]), file=self.output)

    def add_face(self, index, face):
        """
        Adds a face to the model.
        """
        self.face_mapping[index] = len(self.face_mapping)
        print('f {} {} {}'.format(
                self.vertex_mapping[face.a] + 1,
                self.vertex_mapping[face.b] + 1,
                self.vertex_mapping[face.c] + 1,
            ),
            file = self.output
        )

        if self.random_color:
            print('fc {} {} {} {}'.format(
                len(self.face_mapping),
                random.uniform(0, 1),
                random.uniform(0, 1),
                random.uniform(0, 1)),
                file = self.output
            )

    def edit_face(self, index, face):
        """
        Changes the indices of the vertices of the specified face.
        """
        print('ef {} {} {} {}'.format(
                self.face_mapping[index] + 1,
                self.vertex_mapping[face.a] + 1,
                self.vertex_mapping[face.b] + 1,
                self.vertex_mapping[face.c] + 1
            ),
            file = self.output
        )

def main():
    if len(sys.argv) == 1:
        print("obja needs a path to an obja file")
        return

    model = parse_file(sys.argv[1])
    print(model.vertices)
    print(model.faces)

if __name__ == "__main__":
    main()
