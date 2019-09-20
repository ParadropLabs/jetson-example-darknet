FROM openhorizon/aarch64-tx2-darknet
RUN apt-get install -y python-flask python-opencv
COPY example.py /darknet/example.py
COPY static /darknet/static
EXPOSE 5000
CMD ["python", "-u", "example.py"]
