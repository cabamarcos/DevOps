#!/bin/bash

# Definir el directorio de películas
DIRECTORY="../../DEVOPS"

# Recorrer todos los archivos .py dentro del directorio de películas
for file in $(find "$MOVIES_DIR" -name "*.py"); do
    # Ejecutar pylint en el archivo actual y capturar la salida
    pylint_output=$(pylint --rcfile=pylint.rc "$file")

    # Verificar si el archivo cumple con los estándares de pylint
    if [ $? -eq 0 ]; then
        echo "El archivo $file cumple con los estándares de pylint."
    else
        echo "El archivo $file no cumple con los estándares de pylint:"
        echo "$pylint_output"
    fi
done