FROM golang:stretch AS rmapi

ENV GOPATH /go
ENV PATH ${GOPATH}/bin:/usr/local/go/bin:$PATH
ENV RMAPIREPO github.com/juruen/rmapi

RUN go get -u ${RMAPIREPO}


FROM python:3.7-slim-stretch

# rmapi
COPY --from=rmapi /go/bin/rmapi /usr/bin/rmapi

# imagemagick, pdftk, ghostscript, pdfcrop
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        libmagickwand-dev \
        pdftk \
        ghostscript \
        texlive-extra-utils  # contains pdfcrop

RUN pip install --no-cache-dir paper2remarkable

RUN useradd -u 1000 -m -U user

USER user

ENV USER user

WORKDIR /home/user

ENTRYPOINT ["p2r"]
