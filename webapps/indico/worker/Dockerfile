FROM python:3.12.3-bookworm


ENV INDICO_VIRTUALENV="/opt/indico/.venv" INDICO_CONFIG="/opt/indico/etc/indico.conf"

ARG pip="${INDICO_VIRTUALENV}/bin/pip"
ARG tag="latest"

# create indico user, install apt dependencies as root and setup uwsgi etc.
USER root



RUN set -ex && \
	groupadd -r indico && \
	useradd -r -g indico -m -d /opt/indico indico

RUN set -ex && \
    rm -f /etc/apt/sources.list.d/debian.sources && \
    echo "deb http://mirrors.cloud.tencent.com/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://mirrors.cloud.tencent.com/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.cloud.tencent.com/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get -y install texlive-xetex libpq-dev postgresql-client vim less gcc gettext libldap2-dev && \
    apt-get clean



COPY uwsgi.ini /etc/uwsgi.ini
WORKDIR /opt/indico

RUN set -ex && \
    mkdir -p --mode=750 /opt/indico/etc && \
    mkdir -p --mode=777 /opt/indico/tmp && \
    mkdir -p --mode=750 /opt/indico/log && \
    mkdir -p --mode=750 /opt/indico/cache && \
    mkdir -p --mode=750 /opt/indico/archive && \
    chown -R indico:indico /opt/indico

# XXX do we still need this?
RUN chmod g=u /etc/passwd

# all the installations etc can be done using the unprivileged indico user
USER indico

RUN set -ex && \
    python -m venv ${INDICO_VIRTUALENV} && \
    ${pip} install -i https://mirrors.cloud.tencent.com/pypi/simple --upgrade pip setuptools wheel && \
    ${pip} install -i https://mirrors.cloud.tencent.com/pypi/simple uwsgi


RUN if [ "$tag" = "latest" ]; then \
    ${pip} install -i https://mirrors.cloud.tencent.com/pypi/simple indico; \
else \
    ${pip} install -i https://mirrors.cloud.tencent.com/pypi/simple indico==${tag}; \
fi;


RUN ${INDICO_VIRTUALENV}/bin/indico setup create-symlinks /opt/indico

COPY --chown=indico:indico run_indico.sh run_celery.sh docker_entrypoint.sh /opt/indico/
RUN chmod 755 /opt/indico/*.sh

ENTRYPOINT ["/opt/indico/docker_entrypoint.sh"]
EXPOSE 59999
