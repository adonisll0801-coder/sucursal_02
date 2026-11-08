import os
import sys
import yaml
import xml.etree.ElementTree as ET
from ncclient import manager

HOST = "192.168.16.10"
PADRE = "2"
VLAN = int(sys.argv[1]) if len(sys.argv) > 1 else 20
BASE = os.path.expanduser("~/sucursal_02/")
NA = "http://cisco.com/ns/yang/Cisco-IOS-XE-native"

usuario = os.environ.get("NETDEV_USER")
clave = os.environ.get("NETDEV_PASS")
if not usuario or not clave:
    sys.exit("Faltan NETDEV_USER y NETDEV_PASS")

with open(BASE + "datos/sucursal_02_generada.yml") as f:
    datos = yaml.safe_load(f)
v = next((x for x in datos["vlans"] if x["vlan"] == VLAN), None)
if v is None:
    sys.exit("La VLAN %s no esta en el YAML" % VLAN)

SUB = "%s.%s" % (PADRE, VLAN)
FILTRO = ('<native xmlns="%s"><interface><GigabitEthernet><name>%s</name>'
          '</GigabitEthernet></interface></native>' % (NA, SUB))
CONFIG = ('<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">'
          '<native xmlns="%s"><interface><GigabitEthernet><name>%s</name>'
          '<description>VLAN%s-%s</description>'
          '<encapsulation><dot1Q><vlan-id>%s</vlan-id></dot1Q></encapsulation>'
          '<ip><address><primary><address>%s</address><mask>%s</mask>'
          '</primary></address></ip></GigabitEthernet></interface></native>'
          '</config>' % (NA, SUB, v["vlan"], v["nombre"], v["vlan"],
                         v["gateway"], v["mascara"]))


def resumen(xml):
    g = ET.fromstring(xml).find(".//{%s}GigabitEthernet" % NA)
    if g is None:
        return None
    enc = g.findtext(".//{%s}vlan-id" % NA)
    return {"vlan-id": int(enc) if enc else None,
            "ip": g.findtext(".//{%s}primary/{%s}address" % (NA, NA)),
            "mascara": g.findtext(".//{%s}primary/{%s}mask" % (NA, NA)),
            "admin": "down" if g.find("{%s}shutdown" % NA) is not None
            else "up"}


deseado = {"vlan-id": v["vlan"], "ip": v["gateway"],
           "mascara": v["mascara"], "admin": "up"}

with manager.connect(host=HOST, port=830, username=usuario, password=clave,
                     hostkey_verify=False, look_for_keys=False,
                     allow_agent=False, timeout=60) as m:
    print("=== ESTADO ACTUAL de GigabitEthernet%s (get-config) ===" % SUB)
    antes = m.get_config(source="running", filter=("subtree", FILTRO))
    with open(BASE + "evidencias/estado_inicial/fase6_vlan%s_antes.xml"
              % VLAN, "w") as f:
        f.write(antes.xml)
    ra = resumen(antes.xml)
    print("Actual :", ra if ra else "La subinterfaz no existe todavia")
    print("Se aplicara:", deseado)
    with open(BASE + "datos/netconf_vlan%s.xml" % VLAN, "w") as f:
        f.write(CONFIG)

    if input("Escribe SI para aplicar con edit-config: ").strip() != "SI":
        sys.exit("Cancelado, no se cambio nada")

    resp = m.edit_config(target="running", config=CONFIG)
    print("edit-config ->", "OK" if resp.ok else "ERROR")
    print()
    print("=== ESTADO RESULTANTE (get-config) ===")
    despues = m.get_config(source="running", filter=("subtree", FILTRO))
    with open(BASE + "evidencias/estado_final/fase6_vlan%s_despues.xml"
              % VLAN, "w") as f:
        f.write(despues.xml)

real = resumen(despues.xml)
print("Encontrado:", real)
print("Resultado :", "VERIFICADO" if real == deseado else "DIFERENCIAS")
