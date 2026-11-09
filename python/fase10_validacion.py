import os
import sys
import subprocess
import requests
import urllib3
import yaml

urllib3.disable_warnings()

HOST = "192.168.16.10"
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
YAML = os.path.join(RAIZ, "datos", "sucursal_02_generada.yml")
BASE = "https://%s/restconf/data/" % HOST
HDR = {"Accept": "application/yang-data+json"}
fallos = 0


def resultado(condicion, esperado, hallado):
    global fallos
    if str(esperado) == str(hallado):
        print("CUMPLE     %s" % condicion)
    else:
        fallos += 1
        print("NO CUMPLE  %s | esperado: %s | encontrado: %s"
              % (condicion, esperado, hallado))


def buscar(x):
    r = []
    if isinstance(x, dict):
        if "gateway" in x and "vlan" in x:
            return [x]
        for k, v in x.items():
            if isinstance(v, dict) and "gateway" in v and "vlan" not in v:
                v = dict(v, vlan=k)
            r += buscar(v)
    elif isinstance(x, list):
        for v in x:
            r += buscar(v)
    return r


def obtener(ruta, auth):
    try:
        r = requests.get(BASE + ruta, auth=auth, headers=HDR,
                         verify=False, timeout=15)
    except requests.RequestException as e:
        return 0, str(e)
    try:
        datos = r.json() if r.status_code == 200 else {}
    except ValueError:
        datos = {}
    return r.status_code, datos


def primero(d):
    return next(iter(d.values())) if d else {}


def main():
    usuario = os.environ.get("NETDEV_USER")
    clave = os.environ.get("NETDEV_PASS")
    if not usuario or not clave:
        sys.exit("Faltan las variables NETDEV_USER o NETDEV_PASS")
    auth = (usuario, clave)

    with open(YAML) as f:
        vlans = buscar(yaml.safe_load(f))
    if not vlans:
        sys.exit("No se encontraron VLAN en el YAML")

    print("=== Validacion de R-SUC-02 contra el YAML ===")
    for v in sorted(vlans, key=lambda i: int(i["vlan"])):
        n = int(v["vlan"])
        sub = "2.%d" % n
        print("\n--- VLAN %d (GigabitEthernet%s) ---" % (n, sub))
        cod, nat = obtener(
            "Cisco-IOS-XE-native:native/interface/GigabitEthernet=%s" % sub,
            auth)
        existe = "existe" if cod == 200 else "no existe (HTTP %s)" % cod
        resultado("Subinterfaz %s" % sub, "existe", existe)
        if cod != 200:
            continue
        c = primero(nat)
        dot1q = c.get("encapsulation", {}).get("dot1Q", {}).get("vlan-id")
        resultado("Encapsulacion 802.1Q", n, dot1q)
        prim = c.get("ip", {}).get("address", {}).get("primary", {})
        gw = str(v["gateway"]).split("/")[0]
        resultado("Direccion IP / gateway", gw, prim.get("address"))
        resultado("Mascara", v["mascara"], prim.get("mask"))
        admin = "down" if "shutdown" in c else "up"
        resultado("Estado administrativo", "up", admin)
        cod2, op = obtener(
            "Cisco-IOS-XE-interfaces-oper:interfaces/interface=GigabitEthernet%s"
            % sub, auth)
        estado = str(primero(op).get("oper-status", "desconocido"))
        oper = "up" if "ready" in estado else estado
        resultado("Estado operativo", "up", oper)

    print("\n--- Interfaces programables y administracion ---")
    cod, _ = obtener("Cisco-IOS-XE-native:native/hostname", auth)
    resultado("RESTCONF disponible (HTTPS 443)", 200, cod)
    try:
        from ncclient import manager
        with manager.connect(host=HOST, port=830, username=usuario,
                             password=clave, hostkey_verify=False,
                             timeout=15) as m:
            nc = "disponible" if m.connected else "no conectado"
    except Exception as e:
        nc = "error: %s" % str(e)[:60]
    resultado("NETCONF disponible (SSH 830)", "disponible", nc)
    p = subprocess.run(["ping", "-c", "2", "-W", "2", HOST],
                       capture_output=True)
    resultado("Conectividad de administracion (ping %s)" % HOST,
              "responde", "responde" if p.returncode == 0 else "sin respuesta")

    print("\nRESULTADO GENERAL:",
          "CUMPLE" if fallos == 0 else "NO CUMPLE (%d condiciones)" % fallos)
    sys.exit(1 if fallos else 0)


main()
