#!/usr/bin/env python
with open("monfichier.txt", "w") as file:
        file.write("Voici le texte de mon fichier")

print("Successfull")
print("Hello world")

import cgitb
cgitb.enable()

print("Content-Type: text/plain;charset=utf-8")
print()

print("Hello World!")
