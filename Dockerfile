# Use a Manjaro base image. (Ensure this image is available locally or on Docker Hub)
FROM manjarolinux/base

# Update system and install required tools
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm base-devel wget

# Install Python (Manjaro’s repositories should provide Python 3.11 on a current system)
RUN pacman -S --noconfirm python

# Download and install Mambaforge (which includes mamba)
RUN wget -O /tmp/Mambaforge.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
RUN chmod +x /tmp/Mambaforge.sh && \
    /tmp/Mambaforge.sh -b -p /opt/mambaforge && \
    rm /tmp/Mambaforge.sh

# Add Mambaforge to the PATH
ENV PATH="/opt/mambaforge/bin:$PATH"

WORKDIR /app

COPY environment.yml .

ARG MLFINLAB_API_KEY
# ENV MLFINLAB_API_KEY=${MLFINLAB_API_KEY}

RUN [ "MLFINLAB_API_KEY=$MLFINLAB_API_KEY", "conda", "env", "create", "-f", "environment.yml"]
# && conda clean --all --yes

SHELL [ "/bin/bash", "-c" ]
CMD ["conda", "run", "--no-capture-output", "-n", "mlfinlab_env", "pytest", "-v" ]
