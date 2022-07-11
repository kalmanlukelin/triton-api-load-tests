FROM docker-remote.artifactory.oci.oraclecorp.com/oraclelinux:7-slim
COPY --from=odo-docker-signed-local.artifactory.oci.oraclecorp.com/odo/base-image-support:ol7x-1.6 / /

EXPOSE 8089

ENV LANG=en_US.utf8
ENV LC_ALL=en_US.utf8

RUN yum install python3 && \
    rm -rf /var/cache/yum && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1 && \
    python3 -m ensurepip && \
    pip3 install -U pip

# =============================================================================
# Chainsaw2
# =============================================================================
# Configure runit to manage Chainsaw
#
# Executable : Chainsaw : Service Directory Entry
RUN mkdir -p /etc/sv/chainsaw

COPY /etc/sv/chainsaw/run /etc/sv/chainsaw/run
RUN chmod +x /etc/sv/chainsaw/run

# Executable : Chainsaw : Activation
RUN ln -s /etc/sv/chainsaw /etc/service/chainsaw

# -----------------------------------------------------------------------------
# Executable : vision-service-model-load-tests
# -----------------------------------------------------------------------------
WORKDIR /etc/runit/
RUN mkdir -p output_stats
COPY . .
RUN python3 -m pip install --upgrade pip --no-cache-dir
RUN python3 -m pip install -r requirements.txt --no-cache-dir

WORKDIR /
RUN mkdir -p /logs
# Fix ownership for files/paths that are written to at runtime
RUN chown -R odosvc /etc/{sv,service,runit} /var/{log,cache} /run /logs

WORKDIR /etc/runit
ENTRYPOINT ["./run.sh"]