#!/bin/bash
pip install -r requirements.txt
python -c "from base_datos import crear_base_datos; crear_base_datos(); print('Base de datos inicializada')"
