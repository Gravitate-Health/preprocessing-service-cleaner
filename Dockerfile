FROM python:3.12-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

# Disable Python output buffering for real-time logs
ENV PYTHONUNBUFFERED=1

# Feature flags (can be overridden at runtime)
# Set to 'false' to disable HTML optimization
ENV ENABLE_HTML_OPTIMIZATION=true
# Set to 'false' to disable unused HtmlElementLink cleanup
ENV ENABLE_LINK_CLEANUP=true

ENTRYPOINT ["python3"]

CMD ["-m", "preprocessor"]