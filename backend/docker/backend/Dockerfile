################################
# BASE
# Sets up all our shared environment variables and non-root user
################################
FROM bitnamilegacy/python:3.11.6-debian-11-r9 as base

ARG UID
ARG GID
ARG USER_NAME

ENV USER_NAME=${USER_NAME} \
    USER_HOME=/home/$USER_NAME/app \
    VIRTUAL_ENV=/opt/venv \
    # app directory
    TGLOAD_PATH=/opt/tgload \
    # install a handler for SIGSEGV, SIGFPE, SIGABRT, SIGBUS and SIGILL signals
    # to dump the Python traceback
    PYTHONFAULTHANDLER=1 \
    # Overrides the encoding used for stdin/stdout/stderr, in the syntax
    # encodingname:errorhandler./home/mmakov/prj/pet_projects/sstool/home/mmakov/prj/pet_projects/sstool
    PYTHONIOENCODING=UTF-8 \
    # Force python output to sent straight to terminal (e.g. your container log)
    # without being first buffered
    PYTHONUNBUFFERED=True \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Update the package list, install sudo, create a non-root user, and grant password-less sudo permissions
RUN apt update \
    && apt install -y sudo \
    && addgroup --gid $GID $USER_NAME \
    && adduser --uid $UID --gid $GID --disabled-password --gecos "" $USER_NAME \
    && echo "$USER_NAME ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# Set the non-root user as the default user
USER $USER_NAME
WORKDIR $USER_HOME

################################
# BUILDER
# Contains all staff needed to set up and configure the Python environment
################################
FROM base as builder

ARG POETRY_VERSION
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_OPTIONS_NO_PIP=1

RUN sudo mkdir $VIRTUAL_ENV
RUN sudo chown $UID:$GID $VIRTUAL_ENV

RUN python -m venv $VIRTUAL_ENV

RUN pip install poetry==$POETRY_VERSION
COPY pyproject.toml poetry.lock ./

# Install dependencies based on the environment
RUN poetry --no-cache install --no-root


################################
# ENV-BASE
# Contains common configuration for all environments (such as supervisor and entrypoint)
################################
FROM base as env-base

ENV ENV_PATH=/opt/venv

# Install supervisord and pillow-simd dependencies
RUN sudo apt update \
    && sudo apt clean -y \
    && sudo apt install -y \
        supervisor \
       --no-install-recommends ffmpeg ca-certificates tzdata \
    && sudo apt-get clean \
    && sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR $TGLOAD_PATH

# Copy poetry environment from builder image
COPY --from=builder --chown=$USER_NAME:$USER_NAME \
    $VIRTUAL_ENV $ENV_PATH
# Copy codebase
COPY --chown=$USER_NAME:$USER_NAME ./src $TGLOAD_PATH
RUN chmod -R 755 $TGLOAD_PATH

ENTRYPOINT [ "sudo", "--preserve-env", "/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf", "-n" ]

################################
# Dev
# Contains configuration for dev environment
################################
FROM env-base as dev
EXPOSE 5000

# install supervisord plugins
# supervisord-dependent-startup: allows dependent start of programs
RUN pip install \
    supervisord-dependent-startup==1.4.0

# Copy Supervisord config file into configuration directory
COPY --chown=$USER_NAME:$USER_NAME \
    docker/backend/config/supervisord/supervisord.local.conf /etc/supervisor/conf.d/supervisord.conf
# Copy Supervisord dev configs into configuration directory
COPY --chown=$USER_NAME:$USER_NAME docker/backend/config/supervisord/*.local.cfg  /etc/supervisor/conf.d/
