import os
import sys
import json
import yaml
import requests

requests.packages.urllib3.disable_warnings()

HOST = "192.168.16.10"
PADRE = "2"
VLAN = int(sys.argv[1]) if len(sys.argv) > 1 else 10
BASE = os.path.expanduser("~/sucursal_02/")
H = {"Accept": "application/yang-data+json",
     "Content-Type": "application/yang-data+json"}

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
URL = ("https://%s/restconf/data/Cisco-IOS-XE-native:native/interface/"
       "GigabitEthernet=%s" % (HOST, SUB))
s = requests.Session()
s.auth = (usuario, clave)
s.verify = False


def leer():
    r = s.get(URL, headers=H, timeout=30)
    if r.status_code == 404:
        return r.status_code, None
    r.raise_for_status()
    return r.status_code, r.json()


def resumen(d):
    c = d["Cisco-IOS-XE-native:GigabitEthernet"]
    enc = c.get("encapsulation", {}).get("dot1Q", {}).get("vlan-id")
    prim = c.get("ip", {}).get("address", {}).get("primary", {})
    admin = "down" if "shutdown" in c else "up"
    return {"vlan-id": enc, "ip": prim.get("address"),
            "mascara": prim.get("mask"), "admin": admin}


deseado = {"vlan-id": v["vlan"], "ip": v["gateway"],
           "mascara": v["mascara"], "admin": "up"}
payload = {"Cisco-IOS-XE-native:GigabitEthernet": {
    "name": SUB,
    "description": "VLAN%s-%s" % (v["vlan"], v["nombre"]),
    "encapsulation": {"dot1Q": {"vlan-id": v["vlan"]}},
    "ip": {"address": {"primary": {"address": v["gateway"],
                                   "mask": v["mascara"]}}}}}

print("=== ESTADO ACTUAL de GigabitEthernet%s ===" % SUB)
cod, antes = leer()
print("GET ->", cod)
with open(BASE + "evidencias/estado_inicial/fase5_vlan%s_antes.json" % VLAN,
          "w") as f:
    json.dump(antes if antes else {"estado": "no existe"}, f, indent=2)
if antes:
    print("Actual :", resumen(antes))
else:
    print("La subinterfaz no existe todavia")
print("Se aplicara:", deseado)
print("URL :", URL)
with open(BASE + "datos/restconf_vlan%s.json" % VLAN, "w") as f:
    json.dump(payload, f, indent=2)

if input("Escribe SI para aplicar con PUT: ").strip() != "SI":
    sys.exit("Cancelado, no se cambio nada")

r = s.put(URL, headers=H, data=json.dumps(payload), timeout=30)
print("PUT ->", r.status_code, r.reason)
if r.status_code not in (200, 201, 204):
    sys.exit("Error: " + r.text)

print()
print("=== ESTADO RESULTANTE ===")
cod, despues = leer()
print("GET ->", cod)
with open(BASE + "evidencias/estado_final/fase5_vlan%s_despues.json" % VLAN,
          "w") as f:
    json.dump(despues, f, indent=2)
real = resumen(despues)
print("Encontrado:", real)
print("Resultado :", "VERIFICADO" if real == deseado else "DIFERENCIAS")
