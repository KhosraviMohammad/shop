FROM python:3.10
WORKDIR /shop
SHELL ["/bin/bash", "-c"]
COPY . .
# COPY . . :THE first one indicate working dir and the second one demonstrate where to past in containr file system
#ENV VENV_PATH /Exchange/dockervenv
#RUN python -m venv $VENV_PATH
#ENV PATH "$VENV_PATH/bin:$PATH"
RUN pip install -r requirements.txt
RUN pip install gunicorn
#CMD source dockervenv/bin/activate && gunicorn --workers=1 -b 0.0.0.0:8000 'Exchange.wsgi:application'
#CMD gunicorn --workers=1 -b 0.0.0.0:8000 'Exchange.wsgi:application'

CMD python manage.py runserver 0.0.0.0:8000
EXPOSE 8000