import os
import sys
import json
import requests
import urllib3

urllib3.disable_warnings()

HOST = "192.168.16.10"
BASE = f"https://{HOST}/restconf/data/Cisco-IOS-XE-native:native/ip/route"
SIGUIENTE = "192.168.16.2"
REDES = [
    ("192.168.10.0", "255.255.255.0"),
    ("192.168.20.0", "255.255.255.0"),
    ("192.168.99.0", "255.255.255.0"),
]
HDR = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def credenciales():
    usuario = os.environ.get("NETDEV_USER")
    clave = os.environ.get("NETDEV_PASS")
    if not usuario or not clave:
        sys.exit("Faltan las variables NETDEV_USER o NETDEV_PASS")
    return (usuario, clave)


def consultar(auth):
    r = requests.get(BASE, auth=auth, headers=HDR, verify=False, timeout=15)
    try:
        datos = r.json() if r.text else {}
    except ValueError:
        datos = {}
    return r.status_code, datos


def resumen(datos):
    raiz = datos.get("Cisco-IOS-XE-native:route", {})
    lista = raiz.get("ip-route-interface-forwarding-list", [])
    salida = []
    for x in lista:
        saltos = [f.get("fwd") for f in x.get("fwd-list", [])]
        salida.append((x.get("prefix"), x.get("mask"), saltos))
    return salida


def guardar(carpeta, nombre, datos):
    ruta = os.path.join(RAIZ, "evidencias", carpeta, nombre)
    with open(ruta, "w") as f:
        json.dump(datos, f, indent=2)
    print("Evidencia guardada:", os.path.normpath(ruta))


def main():
    auth = credenciales()

    codigo, previo = consultar(auth)
    print("Estado previo (HTTP %s):" % codigo)
    for fila in resumen(previo):
        print("  ", fila)
    if not resumen(previo):
        print("   sin rutas estaticas")
    guardar("estado_inicial", "fase9_rutas_previo.json", previo)

    cuerpo = {
        "Cisco-IOS-XE-native:route": {
            "ip-route-interface-forwarding-list": [
                {"prefix": p, "mask": m, "fwd-list": [{"fwd": SIGUIENTE}]}
                for p, m in REDES
            ]
        }
    }

    print("\nSe aplicara en R-SUC-02:")
    for p, m in REDES:
        print("   ip route %s %s %s" % (p, m, SIGUIENTE))

    if input("\nEscribe SI para aplicar: ").strip() != "SI":
        sys.exit("Cancelado, no se modifico nada.")

    r = requests.patch(BASE, auth=auth, headers=HDR, json=cuerpo,
                       verify=False, timeout=15)
    print("\nPATCH -> HTTP", r.status_code)
    if r.status_code not in (200, 204):
        sys.exit("Error: " + r.text)

    codigo, final = consultar(auth)
    print("\nEstado final (HTTP %s):" % codigo)
    for fila in resumen(final):
        print("  ", fila)
    guardar("estado_final", "fase9_rutas_final.json", final)

    esperado = {(p, m) for p, m in REDES}
    hallado = {(p, m) for p, m, s in resumen(final) if SIGUIENTE in s}
    print("\nRutas CUMPLE" if esperado <= hallado else "\nRutas NO CUMPLE")


main()
