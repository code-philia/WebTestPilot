FROM prestashop/prestashop:8  
  

USER root  
  

RUN sed -i 's/deb.debian.org/mirrors.tencent.com/g' /etc/apt/sources.list.d/debian.sources  
  

RUN apt-get update && apt-get install -y patch  
  

WORKDIR /var/www/html  
  
  
ENV PS_DEV_MODE=1  
ENV PS_SMARTY_FORCE_COMPILE=1  
  
  
