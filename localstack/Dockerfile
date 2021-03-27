FROM localstack/localstack:0.12.7

COPY init-resources.sh /docker-entrypoint-initaws.d/

ENV SERVICES=kinesis,sqs
ENV KINESIS_ERROR_PROBABILITY=0.05
