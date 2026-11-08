# Fase 8 - Configuracion del switch SW-SUC-02-CORE (CLI)

Evidencia de solo lectura tomada en el switch IOSvL2 despues de configurarlo por CLI.

## show vlan brief

VLAN 10  ADMINISTRACION  active  Gi0/1
VLAN 20  OPERACION       active  Gi0/2
VLAN 99  GESTION         active  Gi0/3

## show interfaces trunk

Gi0/0  modo on  encapsulacion 802.1q  estado trunking  nativa 1
VLAN permitidas y activas: 10,20,99

## Puertos (show running-config | section interface)

Gi0/0  TRONCAL-R-SUC-02  trunk dot1q  VLAN permitidas 10,20,99
Gi0/1  PC-ADM            acceso VLAN 10  portfast
Gi0/2  PC-OPE            acceso VLAN 20  portfast
Gi0/3  PC-GES            acceso VLAN 99  portfast

## Conectividad

PC-ADM 10.20.0.2/26 hace ping a su gateway 10.20.0.1
PC-OPE 10.20.0.66/27 hace ping a su gateway 10.20.0.65
PC-GES 10.20.0.98/28 hace ping a su gateway 10.20.0.97
