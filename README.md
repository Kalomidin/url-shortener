# README

## Description

A URL shortening service provides functionality to shorten long URLs into shorter ones and redirect from the shortened URL to the original URL.
**1. Essential Features**

- **Create Shortened URL**
  - `POST /shorten`: Convert the received long URL into a unique short key and store it in the database.
  - Request body: `{"url": "<original_url>"}`
  - Response body: `{"short_url": "<shortened_url>"}`
  - **Algorithm Requirements**:
    - The short key must be unique and generate non-duplicate keys.
    - The key generation algorithm can be implemented freely, but security and efficiency should be considered.
  
- **Redirect to Original URL**
  - `GET /<short_key>`: Redirect to the original URL through the shortened key.
  - Response:
    - If the key exists, redirect to the original URL with a 301 status code.
    - If the key doesn't exist, return an error message with a 404 status code.

**2. Statistics Feature**
- Track the number of views for each short key and add a statistics endpoint to return this information.
- `GET /stats/<short_key>`: Return the number of views for the given key.

## Installation

- To setup the project, install fast-api with uvicorn and sqlachemy for fast-api

```b
pip3 install  'uvicorn[standard]'
pip3 install sqlalchemy  
pip3 install psycopg2   
```

- Run the docker

```b
./docker-start.sh
```

- Run the server

```b
uvicorn main:app
```

## Execution

In this project, PostgreSQL was chosen for its scalability, reliability, and ease of management. PostgreSQL supports both horizontal and vertical scaling, making it suitable for handling increased loads. Its robust replication features ensure high availability. The relational data model of PostgreSQL fits well with the project requirements, providing advanced querying capabilities and ACID compliance. PostgreSQL's comprehensive features and my familiarity with it make it an ideal choice for the database in this application.

### DB Tables

Server consist of two db tables:

- `UrlShortener`
  - to store short url created from given url
- `UrlStats`
  - stores query stats for url

And it supports 3 different endpoints as identified in the description.

#### UrlShortener

Table consist of following columns:

- `id`
- `url`
- `url_id` - A UUID uniquely mapped to the URL
- `expired`
- `expiry_days`
- `created_at`
- `updated_at`

It supports efficient and fast creation of short URLs with expiration. Having a unique index on `(url_id, expired)` helps prevent duplicate entries for the same URL. The `url_id` column is added to enable faster lookups. Although it is possible to set `expired_at` directly, this approach would require a database lock to ensure no duplicates are created. To make it more efficient, a boolean `expired` column is used along with a unique index.

#### UrlStats

Table consist of following columns:

- `id`
- `url_id`
- `status`
- `created_at`

This table stores each url query to one row. It also supports whether it was successful or failed due to various reasons. Querying with short_key is pretty fast since there is index in `url_id`.
