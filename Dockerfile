FROM python:3.8.13-bullseye
RUN apt-get update \
    && pip install --upgrade pip==22.* \
    && apt-get install -y --no-install-recommends ffmpeg libsm6 libxext6 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tod_simulator/
RUN pip install --no-cache-dir -r /tod_simulator/requirements.txt
COPY . /tod_simulator
WORKDIR /tod_simulator

#CMD /bin/bash 
#CMD ["/bin/bash", "-c", "echo yaaa > /ueue/errr.txt"]
CMD python -m src.carla_omnet.CarlaOmnetSimulator $simulator_configuration_file_path
