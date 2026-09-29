#maak certificaat voor opcua verbinding
import asyncio
import socket
from pathlib import Path

from asyncua.crypto.cert_gen import setup_self_signed_certificate
from cryptography.x509.oid import ExtendedKeyUsageOID

APP_URI = "urn:festo-fussion:python"

async def maak():
    await setup_self_signed_certificate(
        key_file=Path("sleutel.pem"),
        cert_file=Path("certificaat.der"),
        app_uri=APP_URI,
        host_name=socket.gethostname(),
        cert_use=[ExtendedKeyUsageOID.CLIENT_AUTH],
        subject_attrs={"countryName": "NL", "organizationName": "Festo-Fussion"},
    )
    print("Certificaat gemaakt")

asyncio.run(maak())