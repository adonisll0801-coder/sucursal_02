# Topologia, pruebas y descripcion tecnica

## Topologia

- R-SUC-02 (CSR1000v, IOS XE 17.03.04a): Gi1 = 192.168.16.10/24 (gestion y WAN hacia SW-WAN), Gi2 = enlace troncal hacia SW-SUC-02-CORE con las subinterfaces Gi2.10, Gi2.20 y Gi2.99.
- SW-SUC-02-CORE (IOSvL2): Gi0/0 troncal 802.1q hacia el router (VLAN 10, 20, 99); Gi0/1 PC-ADM (VLAN 10), Gi0/2 PC-OPE (VLAN 20), Gi0/3 PC-GES (VLAN 99).
- SW-WAN (IOSvL2 sin configurar): conecta el servidor NETDEVOPS-SRV (192.168.16.129), R-SUC-01 (192.168.16.2) y R-SUC-02 (192.168.16.10).
- Servidor Ubuntu (NETDEVOPS-SRV): ejecuta los programas de Python.

## Pruebas realizadas

| Fase | Prueba | Resultado |
|---|---|---|
| 3 | NETCONF (SSH 830) y RESTCONF (HTTPS 443) desde el servidor | Disponibles |
| 4 | Consulta NETCONF de dispositivo, interfaces, estado e IP | Datos procesados |
| 5 | Subinterfaz VLAN 10 por RESTCONF, verificada con Postman | Aplicada |
| 6 | Subinterfaz VLAN 20 por NETCONF | Aplicada |
| 7 | VLAN 99 con consulta cruzada y cambio de descripcion visible por ambos mecanismos | Correcto |
| 8 | VLAN, troncal y puertos de acceso del switch; ping de los PC a su gateway | Correcto |
| 9 | Rutas estaticas por RESTCONF y ruta de retorno en R-SUC-01; pings entre sucursales | Correcto |
| 10 | Validacion automatica contra el YAML, 21 condiciones | CUMPLE |

## Diferencias detectadas y corregidas

- Fase 10: la primera ejecucion dio NO CUMPLE (HTTP 401 y fallo de autenticacion NETCONF) porque la contrasena se definio mal en la variable de entorno. Se redefinio y la segunda ejecucion dio CUMPLE en todas las condiciones.
- Fase 7: la descripcion de Gi2.99 se modifico a VLAN99-GESTION-MOD de forma controlada; no se considera error.

## Descripcion tecnica

- El estado operativo de las interfaces se obtiene del modelo Cisco-IOS-XE-interfaces-oper, no de ietf-interfaces.
- Las subinterfaces se configuran con el modelo Cisco-IOS-XE-native, ruta interface/GigabitEthernet=2.NN.
- Las rutas estaticas se aplican con RESTCONF (PATCH) sobre Cisco-IOS-XE-native:native/ip/route.
- La ruta de retorno 10.20.0.0/23 via 192.168.16.10 se configuro por CLI en R-SUC-01, que no admite RESTCONF.
- Los cambios al router piden confirmacion SI y guardan evidencia del estado anterior y posterior.
