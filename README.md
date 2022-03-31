# filmcollection

## Development

```sh
# backend/.env
DATABASE_URL=sqlite:///../data/db.sqlite
MEDIA_ROOT=../media
OMDB_API_KEY=<api_key>
LB_USERNAME=<letterboxd_username>
LB_LISTS=<media_type>:<list_slug>,[<media_type>:<list_slug>]
ALLOWED_ORIGINS=http://localhost:3000
```
```sh
# frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000
```

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
