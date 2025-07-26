FROM solidnerd/bookstack:25.2.1
COPY bugs/book-create-1.patch /tmp/books.patch
WORKDIR /var/www/bookstack
RUN patch -p0 < /tmp/books.patch
