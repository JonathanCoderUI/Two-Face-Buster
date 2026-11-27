"""Fixture bersama untuk semua file tes."""

# Pemilik: Pelapor.

import pytest

from situs_uji.app import jalankan_di_latar


@pytest.fixture(scope="session")
def alamat_uji():
    """Nyalakan situs uji sekali untuk seluruh sesi tes dan kembalikan alamatnya, misalnya http://127.0.0.1:51234."""
    server, alamat = jalankan_di_latar()
    yield alamat
    server.shutdown()
    server.server_close()
