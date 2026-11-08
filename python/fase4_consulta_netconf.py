import os
import sys
import xml.etree.ElementTree as ET
from ncclient import manager

HOST = "192.168.16.10"
RUTA = os.path.expanduser("~/sucursal_02/evidencias/estado_inicial/")
NS_IF = "urn:ietf:params:xml:ns:yang:ietf-interfaces"
NS_IP = "urn:ietf:params:xml:ns:yang:ietf-ip"
NS_NA = "http://cisco.com/ns/yang/Cisco-IOS-XE-native"
NS_OP = "http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces-oper"

F_NATIVE = '<native xmlns="%s"><hostname/><version/></native>' % NS_NA
F_IF = '<interfaces xmlns="%s"/>' % NS_IF
F_OPER = ('<interfaces xmlns="%s"><interface><name/><admin-status/>'
          '<oper-status/></interface></interfaces>' % NS_OP)

usuario = os.environ.get("NETDEV_USER")
clave = os.environ.get("NETDEV_PASS")
if not usuario or not clave:
    sys.exit("Faltan NETDEV_USER y NETDEV_PASS")

with manager.connect(host=HOST, port=830, username=usuario, password=clave,
                     hostkey_verify=False, look_for_keys=False,
                     allow_agent=False, timeout=60) as m:
    r_nat = m.get(filter=("subtree", F_NATIVE))
    r_if = m.get(filter=("subtree", F_IF))
    r_op = m.get(filter=("subtree", F_OPER))

for nombre_archivo, resp in (("fase4_dispositivo.xml", r_nat),
                             ("fase4_interfaces.xml", r_if),
                             ("fase4_estado_oper.xml", r_op)):
    with open(RUTA + nombre_archivo, "w") as f:
        f.write(resp.xml)

nat = ET.fromstring(r_nat.xml)
host = nat.findtext(".//{%s}hostname" % NS_NA)
ver = nat.findtext(".//{%s}version" % NS_NA)
print("=== IDENTIFICACION DEL DISPOSITIVO ===")
print("Hostname :", host)
print("Version  : IOS XE", ver)
print("Gestion  :", HOST)
print()

TRADUCE = {"if-oper-state-ready": "up", "if-oper-state-no-pass": "down"}
oper = {}
for i in ET.fromstring(r_op.xml).iter("{%s}interface" % NS_OP):
    est = i.findtext("{%s}oper-status" % NS_OP) or "-"
    oper[i.findtext("{%s}name" % NS_OP)] = TRADUCE.get(est, est)

print("=== INTERFACES ===")
fila = "%-22s %-8s %-8s %-16s %-16s"
print(fila % ("Interfaz", "Admin", "Oper", "IP", "Mascara"))
print("-" * 74)
for i in ET.fromstring(r_if.xml).iter("{%s}interface" % NS_IF):
    nombre = i.findtext("{%s}name" % NS_IF)
    habil = i.findtext("{%s}enabled" % NS_IF)
    admin = "up" if habil == "true" else "down"
    estado = oper.get(nombre, "-")
    ipv4 = i.find("{%s}ipv4" % NS_IP)
    direcciones = []
    if ipv4 is not None:
        for a in ipv4.iter("{%s}address" % NS_IP):
            direcciones.append((a.findtext("{%s}ip" % NS_IP),
                                a.findtext("{%s}netmask" % NS_IP)))
    if not direcciones:
        direcciones = [("sin IP", "-")]
    for ip, mascara in direcciones:
        print(fila % (nombre, admin, estado, ip, mascara))
