# pgvector In Sure-AIO

This wrapper now includes the `pgvector` PostgreSQL extension inside the bundled AIO image.

That does not mean pgvector is enabled by default.

## Default Behavior

If you install `sure-aio` and change nothing in the Unraid template:

- Sure boots with the bundled internal PostgreSQL and Redis services
- the `pgvector` extension is available inside the bundled PostgreSQL server
- `pgvector` is **not** activated automatically
- beginners are **not** forced to configure embeddings, vector search, or an external vector database

This is intentional. The extension is installed so the AIO image is capable of using pgvector, but upstream only activates that path when `VECTOR_STORE_PROVIDER=pgvector`.

## Internal pgvector Path

If you want to keep vector search fully inside the AIO:

1. Open the Sure-AIO Unraid template in Advanced View.
2. Set `VECTOR_STORE_PROVIDER=pgvector`.
3. Set an embedding model, such as `EMBEDDING_MODEL=nomic-embed-text`.
4. Set `EMBEDDING_DIMENSIONS` to match that model output.
5. If needed, set `EMBEDDING_URI_BASE` and `EMBEDDING_ACCESS_TOKEN` for your embedding provider.

When that is enabled, Sure uses the bundled internal PostgreSQL service for vector storage.

## External PostgreSQL + pgvector Path

If you already run your own PostgreSQL server:

1. Set the external DB overrides in the template:
   - `DB_HOST`
   - `DB_PORT`
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
2. Set `VECTOR_STORE_PROVIDER=pgvector`.
3. Set the same embedding variables described above.

In this mode, Sure uses your external PostgreSQL server for its main database and its vector storage.

## Important Limitation

Sure-AIO can install `pgvector` into the bundled internal PostgreSQL because that database lives inside this image.

Sure-AIO cannot install `pgvector` into your separate external PostgreSQL server for you.

If you choose the external PostgreSQL path, your external database must already:

- have the `vector` extension available
- allow the Sure database user to use it

## Why This Still Works Well

The wrapper runs `rails db:prepare` on container boot. Upstream's pgvector migration only runs when `VECTOR_STORE_PROVIDER=pgvector`, so enabling pgvector later is not restricted to the very first boot.

That gives you two clean operator paths:

- beginner path: do nothing and ignore vector search entirely
- power-user path: enable internal pgvector, or point Sure at an external PostgreSQL server that already supports pgvector
