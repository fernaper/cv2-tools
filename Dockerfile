FROM jjanzic/docker-python3-opencv:opencv-4.0.1
WORKDIR /

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENV PROJECTDIR /cv2_tools
WORKDIR $PROJECTDIR

COPY . ./

RUN pip install -U .

#ENTRYPOINT [ "python" ]
