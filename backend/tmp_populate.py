import requests

imdbids = [
    "tt0118785", # Budbringeren
    "tt0206634", # Children of Men
]

for fid in imdbids:
    r = requests.get("http://127.0.0.1:8000/films/import", params={
        "imdb_id": fid,
    })
    print(r.status_code)
