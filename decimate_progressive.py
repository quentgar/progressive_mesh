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

        level = 10

        epsilon_list = np.linspace(0.5, 2.5, level)

        for i in range(level):

            base_list = self.get_base_edges(epsilon_list[i])  # Calcul des base edges

            while len(base_list) > 0:

                keep_edges = sharp_list + base_list
                removable_vertices = [True for i in range(len(self.vertices))]  # Liste booléenne vertices à supp
                for index_e in keep_edges:
                    e = self.edges[index_e]
                    removable_vertices[e[0]] = False
                    removable_vertices[e[1]] = False

                for k in range(len(removable_vertices)):
                    if removable_vertices[k]:  # Si le sommet est supprimable
                        """ Récupérer les edges liés à ce sommet """
                        list_edges = []
                        liste_poids = []
                        for q in range(len(self.edges)):
                            e = self.edges[q]
                            if (e[0] == k) or (e[1] == k):
                                list_edges.append(q)
                                liste_poids.append(self.get_edge_weight(q)) # Calcul du poids

                        """ Ordre de priorité """


                for j, e in enumerate(self.edges):
                    if (j not in sharp_list) and (j not in base_list):
                        """
                        EDGE COLLAPSE
                        """



                        """
                        SUPPRESSION DU EDGE
                        ET MAJ DES EDGES 
                        DANS LE MODELE
                        """

                        """
                        ECRITURE DE L'INFO DANS L'OBJA
                        """

        # Write the result in output file
        output_model = obja.Output(output, random_color=False)

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
