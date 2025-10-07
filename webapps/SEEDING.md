This is an overview of how the seeding of web applications is done.

Purpose:
- Deterministic initial data for all app and testcases.
- Avoid data setup time and error.
- Avoid using test scripts to create data, which may be slow and unreliable.

Implementation:
- All apps have seed.sql file, i.e. indico/seed.sql, ...
- Then feed the seed.sql file to db through start_app.sh.

To develop seed.sql, few ways:
- Develop scripts to seed the data, i.e. seed.py files.
- Run `python3 webapps/generate_seed.py $app_name` to generate seed.sql file.

Existing implementation:
- indico/seed.sql, load_seed_data in start_app.sh
