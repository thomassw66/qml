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



RUN [ "conda", "create", "-n", "mlfinlab_env", "python=3.11"]
RUN pacman -Syu --noconfirm git

RUN [ "conda", "init" ]

ARG MLFINLAB_API_KEY
ARG REPOSITORY_HANDLER_URL

RUN /bin/bash -c  "source /root/.bashrc && conda activate mlfinlab_env && pip install \"mlfinlab[all] @ ${REPOSITORY_HANDLER_URL}\""
# RUN [ "conda", "activate", "mlfinlab_env" ]

CMD [ "bash", "-c", "scripts/run_tests_container.sh"]

#COPY environment.yml .
#
## && conda clean --all --yes
#
#SHELL [ "/bin/bash", "-c" ]
#CMD ["conda", "run", "--no-capture-output", "-n", "mlfinlab_env", "pytest", "-v" ]

# FROM hudsonthames/mlfinlab-base:buildx-latest
# ARG MLFINLAB_API_KEY
# 
# CMD [ "bash", "/startup.sh" ]

