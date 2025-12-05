FROM ubuntu:22.04

# 维护者信息
LABEL maintainer="Your Name <your.email@example.com>"

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    wget \
    unzip \
    openjdk-11-jdk \
    libgl1-mesa-glx \
    libgles2-mesa-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装buildozer和python-for-android
RUN pip3 install --upgrade pip \
    && pip3 install buildozer python-for-android

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app

# 构建APK
CMD ["buildozer", "--verbose", "--force", "android", "debug"]
