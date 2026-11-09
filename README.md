# sucursal_02

Implementacion de la Sucursal 02 con un router Cisco CSR1000v (IOS XE) administrado por RESTCONF y NETCONF. Incluye programas en Python para consultar, configurar y validar la infraestructura.

Autor: Adonis Llerena
Curso: Gestion de la Infraestructura de Red

## Diseno de direccionamiento

Bloque 10.20.0.0/23, tomado del Prototipo 2 del taller de Python.

| VLAN | Nombre | Red | Gateway |
|---|---|---|---|
| 10 | ADMINISTRACION | 10.20.0.0/26 | 10.20.0.1 |
| 20 | OPERACION | 10.20.0.64/27 | 10.20.0.65 |
| 99 | GESTION | 10.20.0.96/28 | 10.20.0.97 |

Enlace WAN: 192.168.16.0/24 (R-SUC-01 .2, R-SUC-02 .10, servidor NETDEVOPS-SRV .129).

## Estructura

- python/: programas de consulta, configuracion y validacion
- datos/: archivos YAML, JSON y XML utilizados
- evidencias/estado_inicial/: estado del router antes de cada cambio
- evidencias/estado_final/: estado del router despues de cada cambio
- documentacion/: direccionamiento y evidencia del switch

## Requisitos

Python 3 con requests, PyYAML y ncclient. Las credenciales se leen de las variables de entorno NETDEV_USER y NETDEV_PASS; nunca se guardan en el repositorio.

## Programas

- fase3_capacidades.py: capacidades NETCONF y modelos YANG
- fase4_consulta_netconf.py: consulta NETCONF (dispositivo, interfaces, estado e IP)
- fase5_restconf_vlan.py: subinterfaz por RESTCONF (argumento: numero de VLAN)
- fase6_netconf_vlan.py: subinterfaz por NETCONF (argumento: numero de VLAN)
- fase9_rutas_restconf.py: rutas estaticas por RESTCONF
- fase10_validacion.py: validacion contra el YAML con CUMPLE o NO CUMPLE

## Ejecucion

Definir las credenciales y ejecutar desde la raiz del repositorio:

    export NETDEV_USER=usuario
    read -s -p "Contrasena: " NETDEV_PASS; export NETDEV_PASS
    python3 python/fase10_validacion.py

Los programas que modifican el router piden escribir SI antes de aplicar.

## Flujo de trabajo

Cada fase sigue el ciclo diseno, validacion, implementacion, verificacion y correccion, con un commit por fase.
