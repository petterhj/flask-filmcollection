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

```sh
pip install aerich # await 0.5.7; https://github.com/tortoise/aerich/issues/188db

aerich init -t db.TORTOISE_ORM # Initialize the config file and migrations location
aerich init-db

aerich migrate # Make migrations
aerich upgrade # Apply migrations
```

### References

* https://github.com/testdrivenio/fastapi-tortoise-aerich
