#!/usr/bin/env python

import obja
from obja import Face
import numpy as np
import sys
import random

class Decimater(obja.Model):
    """
    A not so simple class that decimates a 3D model not so stupidly.
    """
    def __init__(self):
        super().__init__()
        self.deleted_faces = set()
        self.deleted_vertices = set()

    def contract(self, output):
        """
        Decimates the model, and write the resulting obja in output.
        """
        operations = []

        # Iterate through the faces
        for (face_index, face) in enumerate(self.faces):
            #if (random.random() <= 0):
            if face_index == 2:
                
                # Collapse face.a and face.b
                v1 = self.vertices[face.a]
                v2 = self.vertices[face.b]

                print("Face A ", face.a + 1)
                print("Face B ", face.b + 1)

                # New coordinates
                v_new = 0.5 * (v1 + v2)

                # Set v1 and v2 to v_new
                self.vertices[face.a] = v_new
                self.vertices[face.b] = v_new
                operations.append(('edit', face.a, v1)) # reset face.a to v1
                operations.append(('edit', face.b, v2)) # reset face.b to v2

                # Delete all faces where v1 and v2 appears
                for (face_index_2, face_2) in enumerate(self.faces):
                    f = [face_2.a, face_2.b, face_2.c]
                    if(face.a in f and face.b in f):
                        print("Delete : ", face_index_2 + 1)
                        self.deleted_faces.add(face_index_2)
                        operations.append(('face', face_index_2, face_2))

                print(self.deleted_faces)

                # Edit all faces where v2 appears
                for (face_index_2, face_2) in reversed(list(enumerate(self.faces))):
                    if face_index_2 not in self.deleted_faces:
                        if (face_2.a == face.b) :
                            self.faces[face_index_2] = Face(face.a, face_2.b, face_2.c)
                            operations.append(('edit_face', face_index_2, face_2 ))
                        if (face_2.b == face.b) :
                            self.faces[face_index_2] = Face(face_2.a, face.a, face_2.c)
                            operations.append(('edit_face', face_index_2, face_2 ))
                        if (face_2.c == face.b) :
                            self.faces[face_index_2] = Face(face_2.a, face_2.b, face.a)
                            operations.append(('edit_face', face_index_2, face_2 ))

                # Delete v2
                operations.append(('vertex', face.b, v_new)) # add vertex face.b at v_new
                self.deleted_vertices.add(face.b)
                print(self.deleted_vertices)

        for (face_index, face) in reversed(list(enumerate(self.faces))):
            if face_index not in self.deleted_faces:
                operations.append(('face', face_index, face))

        for (vertex_index, vertex) in reversed(list(enumerate(self.vertices))):
            if vertex_index not in self.deleted_vertices:
                print("Store : ", vertex_index + 1)
                operations.append(('vertex', vertex_index, vertex))

        # To rebuild the model, run operations in reverse order
        operations.reverse()

        # Write the result in output file
        output_model = obja.Output(output, random_color=True)

        for (ty, index, value) in operations:
            if ty == "vertex":
                output_model.add_vertex(index, value)
            elif ty == "face":
                output_model.add_face(index, value)
            elif ty == "edit_face":
                print(index, value)
                output_model.edit_face(index, value)   
            elif ty == "edit":
                output_model.edit_vertex(index, value)

def main():
    """
    Runs the program on the model given as parameter.
    """
    file = 'example/2d.obj'
    np.seterr(invalid = 'raise')
    model = Decimater()
    model.parse_file(file)

    with open(file + 'a', 'w') as output:
        model.contract(output)


if __name__ == '__main__':
    main()
