#!/usr/bin/env python

import obja
from obja import Face
import numpy as np
import sys
import random

class Decimater(obja.Model):
    """
    A simple class that decimates a 3D model stupidly.
    """
    def __init__(self):
        super().__init__()
        self.deleted_faces = set()
        self.deleted_vertices = set()

    def edge_collapse(self, operations, edge, deleted_edges, keep_edges):

        vertex1 = edge[0]
        vertex2 = edge[1]
        face1 = edge[2]
        face2 = edge[3]

        # Collapse vertex1 and vertex2
        v1 = self.vertices[vertex1]
        v2 = self.vertices[vertex2]

        # New coordinates
        v_new = 0.5 * (v1 + v2)

        # Set v1 and v2 to v_new
        self.vertices[vertex1] = v_new
        self.vertices[vertex2] = v_new
        operations.append(('edit', vertex1, v1))  # reset vertex1 to v1
        operations.append(('edit', vertex2, v2))  # reset vertex2 to v2

        # Delete all faces where v1 and v2 appears
        for (face_index_2, face_2) in enumerate(self.faces):
            f = [face_2.a, face_2.b, face_2.c]
            if vertex1 in f and vertex2 in f:
                self.deleted_faces.add(face_index_2)
                operations.append(('face', face_index_2, face_2))

        # Edit all faces where v2 appears
        for (face_index_2, face_2) in reversed(list(enumerate(self.faces))):
            if face_index_2 not in self.deleted_faces:
                if face_2.a == vertex2:
                    self.faces[face_index_2].a = vertex1
                    operations.append(('edit_face', face_index_2, face_2))
                if face_2.b == vertex2:
                    self.faces[face_index_2].b = vertex1
                    operations.append(('edit_face', face_index_2, face_2))
                if face_2.c == vertex2:
                    self.faces[face_index_2].c = vertex1
                    operations.append(('edit_face', face_index_2, face_2))

        # Delete v2
        operations.append(('vertex', vertex2, v_new))  # add vertex2 at v_new
        self.deleted_vertices.add(vertex2)

        l_e = []  # Liste des edges
        l_v = []  # Liste des vertex
        for ind_e, e in enumerate(self.edges):

            if ind_e not in keep_edges:
                # Delete the edge associated to v1 and v2
                if (e[0] == vertex1 and e[1] == vertex2) or (e[0] == vertex2 and e[1] == vertex1):
                    deleted_edges.add(ind_e)
                    # self.edges.pop(ind_e)

                # Edit all edges where v2 appears
                elif e[0] == vertex2:
                    self.edges[ind_e][0] = vertex1
                    l_e.append(ind_e)
                    l_v.append(self.edges[ind_e][1])
                elif e[1] == vertex2:
                    self.edges[ind_e][1] = vertex1
                    l_e.append(ind_e)
                    l_v.append(self.edges[ind_e][0])

                elif e[0] == vertex1:
                    l_e.append(ind_e)
                    l_v.append(self.edges[ind_e][1])
                elif e[1] == vertex1:
                    l_e.append(ind_e)
                    l_v.append(self.edges[ind_e][0])

        # Delete 1 over 2 edges mixed
        for ind_v1, v1 in enumerate(l_v):
            l_v.pop(ind_v1)
            ind_e = l_e.pop(ind_v1)
            for ind_v2, v2 in enumerate(l_v):
                if v1 == v2:
                    deleted_edges.add(ind_e)
                    # Modifier la face du edge conservé
                    new_edge = self.edges[l_e[ind_v2]]

                    if new_edge[2] == self.edges[ind_e][2]:
                        new_edge[2] = self.edges[ind_e][3]
                    elif new_edge[2] == self.edges[ind_e][3]:
                        new_edge[2] = self.edges[ind_e][2]
                    elif new_edge[3] == self.edges[ind_e][2]:
                        new_edge[3] = self.edges[ind_e][3]
                    else:
                        new_edge[3] = self.edges[ind_e][2]
                    # MAJ de l'edge
                    self.edges[l_e[ind_v2]] = new_edge
                    # self.edges.pop(ind_e)

        return operations

    def contract(self, output, sharp_list):
        """
        Decimates the model stupidly, and write the resulting obja in output.
        """

        level = 10

        epsilon_list = np.linspace(0.5, 2.5, level)

        operations = []

        for i in range(level):
            print("\nLevel :", i)
            base_list = self.get_base_edges(epsilon_list[i])  # Calcul des base edges
            sharp_list = self.get_sharp_edges()  # Calcul des sharp edges
            keep_edges = sharp_list + base_list

            prec_len_bl = -1

            while len(base_list) != prec_len_bl:
                print(len(base_list), " base edges")

                # removable_vertices = [True for i in range(len(self.vertices))]  # Liste booléenne vertices à supp
                # for index_e in keep_edges:
                #     e = self.edges[index_e]
                #     removable_vertices[e[0]] = False
                #     removable_vertices[e[1]] = False

                # for k in range(len(removable_vertices)):
                #     if removable_vertices[k]:  # Si le sommet est supprimable
                #         """ Récupérer les edges liés à ce sommet """
                #         list_edges = []
                #         liste_poids = []
                #         for q in range(len(self.edges)):
                #             e = self.edges[q]
                #             if (e[0] == k) or (e[1] == k):
                #                 list_edges.append(q)
                #                 liste_poids.append(self.get_edge_weight(q)) # Calcul du poids

                #         """ Ordre de priorité """
                prec_len_bl = len(base_list)
                deleted_edges = set()
                # MAJ des edges seulement hors de la boucle suivante ?
                for j, e in enumerate(self.edges):
                    if j not in keep_edges:
                        """
                        EDGE COLLAPSE
                        """
                        operations = self.edge_collapse(operations, e, deleted_edges, keep_edges)

                print("Num deleted edges : ", len(deleted_edges))
                # MAJ des edges
                edges_tmp = []
                for j, e in enumerate(self.edges):
                    if j in keep_edges:
                        edges_tmp.append(e)
                    elif j not in deleted_edges:
                        edges_tmp.append(e)
                self.edges = edges_tmp

                # Mise à jour de keep_edges
                base_list = self.get_base_edges(epsilon_list[i])  # Calcul des base edges
                sharp_list = self.get_sharp_edges()  # Calcul des sharp edges
                keep_edges = sharp_list + base_list

        print("\n", len(self.deleted_faces), " deleted faces\n")
        print(len(self.deleted_vertices), " deleted vertices\n")
        #print(self.deleted_vertices)
        for (face_index, face) in reversed(list(enumerate(self.faces))):
            if face_index not in self.deleted_faces:
                #print("Store : ", face_index + 1)
                operations.append(('face', face_index, face))

        for (vertex_index, vertex) in reversed(list(enumerate(self.vertices))):
            if vertex_index not in self.deleted_vertices:
                #print("Store vertex : ", vertex_index)
                operations.append(('vertex', vertex_index, vertex))

        # To rebuild the model, run operations in reverse order
        operations.reverse()
        
        # Write the result in output file
        output_model = obja.Output(output, random_color=False)

        for (ty, index, value) in operations:
            #print(index, value)
            if ty == "vertex":
                output_model.add_vertex(index, value)
            elif ty == "face":
                #print(index, value)
                output_model.add_face(index, value)
            elif ty == "edit_face":
                #print(index, value)
                output_model.edit_face(index, value)   
            elif ty == "edit":
                output_model.edit_vertex(index, value)


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

    with open('example/test.obja', 'w') as output:
        model.contract(output, sharp_list)

    print("Modèle initial : ",nb_edges,"arrêtes\n")
    print("Modèle sharp : ", nb_sharp_edges, "arrêtes\n")

if __name__ == '__main__':
    main()
