FROM prestashop/prestashop:8

USER root

RUN sed -i 's/deb.debian.org/mirrors.tencent.com/g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update && apt-get install -y patch curl

WORKDIR /var/www/html

ENV PS_DEV_MODE=1
ENV PS_SMARTY_FORCE_COMPILE=1

# Create tools directory and copy our customer creation script
RUN mkdir -p /var/www/html/tools
COPY create_user.php /var/www/html/tools/create_user.php
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Make files executable and set proper permissions
RUN chmod +x /usr/local/bin/entrypoint.sh && \
    chmod 644 /var/www/html/tools/create_user.php && \
    chown www-data:www-data /var/www/html/tools/create_user.php