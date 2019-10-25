FROM python:3.7-stretch

ENV GO_VERSION 1.12.9
ENV GO_TAR go${GO_VERSION}.linux-amd64.tar.gz
ENV GOROOT /usr/local/go
ENV GOPATH /root/go
ENV PATH ${GOPATH}/bin:${GOROOT}/bin:${PATH}

# rmapi
RUN wget https://dl.google.com/go/${GO_TAR} \
    && tar -xf ${GO_TAR} \
    && mv go ${GOROOT} \
    && rm ${GO_TAR} \
    && go get -u github.com/juruen/rmapi

# pdftk & pdfcrop
RUN apt-get update \
    && apt-get install -y \
        pdftk \
        texlive-extra-utils  # contains pdfcrop

RUN pip install paper2remarkable

ENTRYPOINT ["p2r"]
