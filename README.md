# filmcollection

## Environment

```
export DATABASE_URL=sqlite:///../data/db.sqlite
export MEDIA_ROOT=../media
export OMDB_API_KEY=<api_key>
```

## Development

```sh
cd backend/

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload --lifespan on
```
