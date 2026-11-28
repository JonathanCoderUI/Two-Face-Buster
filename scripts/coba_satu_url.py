"""Coba satu URL situs uji dengan tiga persona lalu cetak hasilnya."""

# Pemilik: Penjelajah.
# Jalankan dengan: python -m scripts.coba_satu_url (situs uji harus sedang hidup).


import asyncio

import aiohttp

from siluman import crawler


async def coba():
    async with aiohttp.ClientSession() as session:
        for persona in ["browser", "googlebot", "dari_google"]:
            k = await crawler.ambil(session, "http://127.0.0.1:5050/cloak-referer/1", persona, putaran=1)
            print(persona, k["status"], k["redirect_ke"], k["html"] == None)


if __name__ == "__main__":
    asyncio.run(coba())