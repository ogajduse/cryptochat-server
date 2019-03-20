FROM centos:7

RUN yum -y update \
    && yum -y install centos-release-scl \
    && yum -y install rh-python36 rsync \
    && rm -rf /var/cache/yum/*

ENV APPBASEDIR=/cryptochat-server

RUN install -m 1777 -d /data
ADD *.sh $APPBASEDIR/
ADD *.py $APPBASEDIR/
ADD scl-enable.sh $APPBASEDIR/
ADD Pipfile* $APPBASEDIR/

RUN adduser --gid 0 -d $APPBASEDIR --no-create-home -c 'cryptochat-server user' cryptochat

RUN chown -R cryptochat $APPBASEDIR

RUN $APPBASEDIR/scl-enable.sh pip install --upgrade pip

RUN $APPBASEDIR/scl-enable.sh pip install pipenv

USER cryptochat

EXPOSE 8888

# CMD ["sh", "-c", "$APPBASEDIR/scl-enable.sh $APPBASEDIR/entrypoint.sh"]
