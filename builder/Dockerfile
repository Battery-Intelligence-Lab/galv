FROM node:lts

RUN apt update && apt install -y build-essential protobuf-compiler curl python3.5-dev python3-venv && \
mkdir /workdir && python3 -m venv /workdir/venv && \
npm install -g pnpm && \
bash -c "source /workdir/venv/bin/activate && pip install wheel pyyaml"

WORKDIR /workdir

CMD ["bash", "/workdir/project/builder/build.sh"]
