#!/usr/bin/env python

import obja
import numpy as np
import sys

class Decimater(obja.Model):
    """
    A simple class that decimates a 3D model stupidly.
    """
    def __init__(self):
        super().__init__()
        self.deleted_faces = set()

    def contract(self, output, sharp_list):
        """
        Decimates the model stupidly, and write the resulting obja in output.
        """
        v_index = []
        f_index = []
        vertex = []
        faces = []

        for edge_index in sharp_list:
            edge = self.edges[edge_index]
            if not edge[0] in v_index:
                v_index.append(edge[0])
                vertex.append((edge[0], self.vertices[edge[0]]))
            if not edge[1] in v_index:
                v_index.append(edge[1])
                vertex.append((edge[1], self.vertices[edge[1]]))
            if not edge[2] in f_index:
                f_index.append(edge[2])
                faces.append((edge[2], self.faces[edge[2]]))
            if not edge[3] in f_index:
                f_index.append(edge[3])
                faces.append((edge[3], self.faces[edge[3]]))

        # Write the result in output file
        output_model = obja.Output(output, random_color=False)

        for (index, v) in vertex:
            output_model.add_vertex(index, v)
        for (index, f) in faces:
            if (f.a in v_index) and (f.b in v_index) and (f.c in v_index):
                output_model.add_face(index, f)

def main():
    """
    Runs the program on the model given as parameter.
    """
    np.seterr(invalid = 'raise')
    model = Decimater()
    model.parse_file('example/suzanne.obj')
    print("Computing edges... \n")
    model.compute_edges()
    nb_edges = len(model.edges)

    print("Edges computed\n")
    sharp_list = model.get_sharp_edges(5e-3, 5e-3)
    nb_sharp_edges = len(sharp_list)

    with open('example/test.obj', 'w') as output:
        model.contract(output, sharp_list)

    print("Modèle initial : ",nb_edges,"arrêtes\n")
    print("Modèle sharp : ", nb_sharp_edges, "arrêtes\n")

if __name__ == '__main__':
    main()
