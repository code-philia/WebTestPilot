# Web Application Docker Images

This folder contains Docker images of all 4 web applications used in the benchmark.

## Details

|Web App.|Version|Port|Platform|Source|
|---|---|---|---|---|
|indico|v3.3.6|8080|linux/amd64|[GitHub](https://github.com/indico/indico-containers/pkgs/container/indico/380792119?tag=3.3.6) / [Docker Hub](https://hub.docker.com/layers/getindico/indico/3.3.6/images/sha256-a11a42e4cf956944f1b051e3bff05312b7bdc26392c333e464f6a0fcdebe0d24) |
|bookstack|v25.02.1|8081|linux/amd64|[GitHub](https://github.com/linuxserver/docker-bookstack/releases/tag/v25.02.1-ls198) / [Docker Hub](https://hub.docker.com/layers/linuxserver/bookstack/25.02.1/images/sha256-dfbc9dda2e55d90234f065f13812315d01fb9dbd5c18a7c9683a15fee1a865fb)|
|invoiceninja|v5.11.61|8082|linux/amd64|[GitHub](https://github.com/invoiceninja/dockerfiles/releases/tag/5.11.61-o) / [Docker Hub](https://hub.docker.com/layers/invoiceninja/invoiceninja-debian/5.11/images/sha256-f926beb76b256d7546ed64126c3b56e5a9810e6eeb1fa4d10f2c99ec65bbdf6b)|
|prestashop|v8|8083|linux/amd64|[GitHub](https://github.com/PrestaShop/docker) / [Docker Hub](https://hub.docker.com/layers/prestashop/prestashop/8/images/sha256-3129983d964d3711296048829510a3807b7e68a1c6210e3b8b8d6a8a01600f5c)|

## Extra Configs

To seed database with random data for testing

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

## Accounts

|Web App.|Username|Password|
|---|---|---|
|indico|admin@admin.com|webtestpilot|
|bookstack|admin@admin.com|password|
|invoiceninja|user@example.com|password|
|prestashop|admin@admin.com|admin12345|