FROM docker.elastic.co/elasticsearch/elasticsearch:8.12.1

# Add custom configuration
COPY config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml

# Set permissions
USER root
RUN chown elasticsearch:elasticsearch /usr/share/elasticsearch/config/elasticsearch.yml
USER elasticsearch
