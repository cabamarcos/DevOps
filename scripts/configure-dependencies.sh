#!/bin/bash

# Actualizar e instalar dependencias del sistema
sudo apt-get update -q -y
sudo apt-get install -y python3-pip python3-dev

# Instalar y actualizar pip
pip install --upgrade pip

# Instalar dependencias de Python
pip install -r requirements.txt

echo "Dependencias instaladas correctamente."
