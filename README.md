# filmcollection

## Environment

```
export DATABASE_URL=sqlite:///../data/db.sqlite
export MEDIA_ROOT=../media
export OMDB_API_KEY=<api_key>
```

## Development

```sh
uvicorn main:app --reload --lifespan on
```
