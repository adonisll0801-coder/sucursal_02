# Direccionamiento Sucursal 02

Bloque asignado: 10.20.0.0/23
Fuente: datos/sucursal_02_generada.yml (Prototipo 2)

| VLAN | Nombre | Red | Máscara | Prefijo | Gateway | Rango utilizable | Hosts previstos | Hosts utilizables |
|------|--------|-----|---------|---------|---------|------------------|-----------------|-------------------|
| 10 | ADMINISTRACION | 10.20.0.0/26 | 255.255.255.192 | 26 | 10.20.0.1 | 10.20.0.1 - 10.20.0.62 | 50 | 62 |
| 20 | OPERACION | 10.20.0.64/27 | 255.255.255.224 | 27 | 10.20.0.65 | 10.20.0.65 - 10.20.0.94 | 25 | 30 |
| 99 | GESTION | 10.20.0.96/28 | 255.255.255.240 | 28 | 10.20.0.97 | 10.20.0.97 - 10.20.0.110 | 10 | 14 |

## Validación
- Las tres redes pertenecen al bloque 10.20.0.0/23.
- No hay superposiciones entre ellas.
- Las puertas de enlace son direcciones utilizables de cada red.
- La capacidad de hosts cubre lo requerido en las tres VLAN.
- No se encontraron errores en el diseño; no hubo necesidad de rediseñar.
