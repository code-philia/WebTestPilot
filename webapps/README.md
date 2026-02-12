# Web Applications

This folder contains Docker images of all 4 web applications used in the benchmark.

## Overview

|Web App.|Version|Port|Platform|Source|
|---|---|---|---|---|
|indico|v3.3.6|8080|linux/amd64|[GitHub](https://github.com/indico/indico-containers/pkgs/container/indico/380792119?tag=3.3.6) / [Docker Hub](https://hub.docker.com/layers/getindico/indico/3.3.6/images/sha256-a11a42e4cf956944f1b051e3bff05312b7bdc26392c333e464f6a0fcdebe0d24) |
|bookstack|v25.02.1|8081|linux/amd64|[GitHub](https://github.com/linuxserver/docker-bookstack/releases/tag/v25.02.1-ls198) / [Docker Hub](https://hub.docker.com/layers/linuxserver/bookstack/25.02.1/images/sha256-dfbc9dda2e55d90234f065f13812315d01fb9dbd5c18a7c9683a15fee1a865fb)|
|invoiceninja|v5.11.61|8082|linux/amd64|[GitHub](https://github.com/invoiceninja/dockerfiles/releases/tag/5.11.61-o) / [Docker Hub](https://hub.docker.com/layers/invoiceninja/invoiceninja-debian/5.11/images/sha256-f926beb76b256d7546ed64126c3b56e5a9810e6eeb1fa4d10f2c99ec65bbdf6b)|
|prestashop|v8|8083|linux/amd64|[GitHub](https://github.com/PrestaShop/docker) / [Docker Hub](https://hub.docker.com/layers/prestashop/prestashop/8/images/sha256-3129983d964d3711296048829510a3807b7e68a1c6210e3b8b8d6a8a01600f5c)|

## Accounts

For default user accounts, please refer to `/baselines/setup_function.py`

## Seeding

To generate seeding data:

```bash
python3 webapps/generate_seed.py indico
```

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