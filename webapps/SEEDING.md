This is an overview of how the seeding of web applications is done.

Purpose:
- Deterministic initial data for all app and testcases.
- Avoid data setup time and error.
- Avoid using test scripts to create data, which may be slow and unreliable.

Implementation:
- All apps have seed.sql file, i.e. indico/seed.sql, ...
- Then feed the seed.sql file to db through start_app.sh.

To develop seed.sql, few ways:
- Populate data through web UI / Run existing Playwright setup scripts to create data. / Use data seeder such as db:seed.
- (Optional) might need to open the port in docker-compose.yml to access it from host.
- Dump the sql database.
- Dump command:
- ```
mysqldump --host=127.0.0.1 --port=3306 --default-character-set=utf8 --user=root --protocol=tcp --extended-insert=FALSE --single-transaction=TRUE --column-statistics=0 --skip-triggers "prestashop"
```
- Pick the relevant insert statements.

Existing implementation:
- indico/seed.sql, load_indico_seed_data in start_app.sh

Apps with existing seeding data:

For bookstack
```bash
docker compose up
docker compose run --rm -w /var/www/bookstack app php artisan db:seed --class=DummyContentSeeder
```

For invoiceninja
```bash
docker compose up
docker compose run --rm php artisan db:seed --class=RandomDataSeeder
```