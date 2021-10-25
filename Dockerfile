# syntax=docker/dockerfile:1
FROM youdiandai/python39_uwsgi_nginx
WORKDIR /app
COPY nginx.conf /etc/nginx/nginx.conf
COPY requirements.txt requirements.txt
RUN pip3 install -r  requirements.txt -i  https://pypi.tuna.tsinghua.edu.cn/simple/
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster main contrib non-free" >/etc/apt/sources.list
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-updates main contrib non-free" >>/etc/apt/sources.list
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-backports main contrib non-free" >>/etc/apt/sources.list
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security buster/updates main contrib non-free" >>/etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y libpcre3 libpcre3-dev
RUN apt-get install -y uwsgi
RUN apt-get install -y uwsgi-plugin-python
RUN apt-get install -y nginx
RUN pip3 install uwsgi -i  https://pypi.tuna.tsinghua.edu.cn/simple/
COPY . .
ENTRYPOINT nginx -g "daemon on;" && uwsgi --ini /app/baiyangdian.ini

