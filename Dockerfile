FROM centos:7

RUN yum -y update \
    && yum -y install centos-release-scl \
    && yum -y install rh-python36 rsync which gcc python-devel\
    && rm -rf /var/cache/yum/*

ENV APPBASEDIR=/cryptochat-server
ENV LC_ALL=en_US.utf-8
ENV LANG=en_US.utf-8

RUN install -m 1777 -d /data
ADD *.sh $APPBASEDIR/
ADD *.py $APPBASEDIR/
ADD scl-enable.sh $APPBASEDIR/
ADD Pipfile* $APPBASEDIR/

RUN adduser --gid 0 -d $APPBASEDIR --no-create-home -c 'cryptochat-server user' cryptochat

RUN chown -R cryptochat $APPBASEDIR
RUN chmod +x $APPBASEDIR/scl-enable.sh

RUN $APPBASEDIR/scl-enable.sh pip install --upgrade pip

RUN $APPBASEDIR/scl-enable.sh pip install pipenv

USER cryptochat
WORKDIR $APPBASEDIR
RUN $APPBASEDIR/scl-enable.sh pipenv --three --verbose install

EXPOSE 8888
RUN mkdir $APPBASEDIR/.data
ENV DATABASE_LOCATION=$APPBASEDIR/.data/db.json
ENV VERSION=0.0.1

ENTRYPOINT ["sh", "-c", "$APPBASEDIR/scl-enable.sh pipenv run python app.py"] 
#CMD ["sh", "-c", "$APPBASEDIR/scl-enable.sh $APPBASEDIR/entrypoint.sh"]
