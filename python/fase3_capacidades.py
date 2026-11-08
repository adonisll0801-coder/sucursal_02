import os
from ncclient import manager

HOST = "192.168.16.10"
SALIDA = os.path.expanduser("~/sucursal_02/evidencias/estado_inicial/capacidades_netconf.txt")

with manager.connect(
    host=HOST,
    port=830,
    username=os.environ["NETDEV_USER"],
    password=os.environ["NETDEV_PASS"],
    hostkey_verify=False,
    allow_agent=False,
    look_for_keys=False,
    timeout=60,
) as m:
    caps = sorted(m.server_capabilities)
    modelos = [c for c in caps if "module=" in c]
    interes = [c for c in modelos if any(k in c for k in (
        "Cisco-IOS-XE-native", "ietf-interfaces", "ietf-ip",
        "openconfig-interfaces", "Cisco-IOS-XE-interfaces-oper"))]
    with open(SALIDA, "w") as f:
        f.write(f"Router: {HOST}\n")
        f.write(f"Total capacidades: {len(caps)}\n")
        f.write(f"Total modelos YANG: {len(modelos)}\n\n")
        f.write("== Modelos de interes ==\n")
        for c in interes:
            f.write(c + "\n")
        f.write("\n== Todas las capacidades ==\n")
        for c in caps:
            f.write(c + "\n")
    print("Capacidades:", len(caps))
    print("Modelos YANG:", len(modelos))
    print("Modelos de interes:")
    for c in interes:
        print(" -", c.split("module=")[1].split("&")[0])
    print("Guardado en:", SALIDA)
