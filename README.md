# filmcollection

## Environment

```
export DATABASE_URL=sqlite:///../data/db.sqlite
export MEDIA_ROOT=../media
export OMDB_API_KEY=<api_key>
export LB_USERNAME=<letterboxd_username>
export LB_LISTS=<media_type>:<list_slug>,[<media_type>:<list_slug>]
```

## Development

```sh
cd backend/

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload --lifespan on
```

```sh
cd frontend/

npm install
npm run dev
```
