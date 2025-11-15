## Conductor Vision

A real-time gesture-controlled music interface built with computer vision, lightweight ML, and a production-style backend. This project explores how conductor-style motion can drive tempo, volume, and musical intensity through a modern CV + ML pipeline.

The goal is simple: use one of my passions—music—to explore a technical area outside my usual work, while demonstrating practical AI/ML, backend architecture, real-time systems design, and MLOps observability.

## Project Overview

Conductor Vision captures hand-motion through a webcam, extracts hand-landmark data using MediaPipe, and interprets this movement as conducting gestures. The system infers tempo (via beat gesture timing), volume (via hand distance), and intensity (via motion energy), then adjusts audio playback in real time. A lightweight ML classifier enhances stability by identifying gesture states (tempo up / tempo down / steady).
All inference runs through a FastAPI backend with Prometheus metrics and a Grafana dashboard for real-time monitoring.

## Features

* Real-time hand-tracking via MediaPipe Hands
* Beat-gesture tempo inference
* Volume and intensity controls from distance and motion velocity
* Lightweight ML classifier trained on captured gesture sequences
* FastAPI backend for model serving and real-time inference
* WebSocket landmark streaming
* Prometheus metrics for inference latency, throughput, BPM stability
* Dockerized Prometheus + Grafana monitoring stack
* Grafana dashboard for production-style ML observability
* `docker-compose up` for a reproducible full-stack system

## Tech Stack

**Computer Vision**

* MediaPipe Hands (real-time hand landmark extraction)
* OpenCV (webcam capture + on-screen overlays)

**Machine Learning**

* scikit-learn (baseline gesture classifiers)
* Optional PyTorch (LSTM / 1D-CNN sequence modeling)
* Custom feature extraction (beat intervals, velocity, motion energy)

**Backend & System Architecture**

* FastAPI (model serving + inference API)
* WebSockets (real-time landmark streaming)
* python-vlc (audio engine for tempo/volume control)
* Docker + Docker Compose (multi-service orchestration)

**MLOps & Observability**

* Prometheus (metrics collection: latency, BPM, inference rate)
* Grafana (dashboard + automatic provisioning)
* Structured logs + runtime model metadata

## Research Foundations & Credits

Conductor Vision builds on existing research in gesture-based musical interaction, conductor motion analysis, and real-time CV models. The following works informed the design:

**MUSE: A Music Conducting Recognition System**
University of Nevada
[https://www.cse.unr.edu/~fredh/papers/conf/173-mamcrs/paper.pdf](https://www.cse.unr.edu/~fredh/papers/conf/173-mamcrs/paper.pdf)
Inspired the idea of mapping conductor motion patterns to musical parameters and using lightweight models for gesture classification.

**Hand Gestures in Music Production**
Berndt et al.
[http://www.cemfi.de/wp-content/papercite-data/pdf/berndt-2016-hand-gestures.pdf](http://www.cemfi.de/wp-content/papercite-data/pdf/berndt-2016-hand-gestures.pdf)
Provided gesture vocabularies and insights on intuitive mappings between hand motion and musical controls such as tempo, dynamics, and expression.

**Real-Time Musical Conducting Gesture Recognition**
Chin-Shyurng et al.
[https://www.mdpi.com/2076-3417/9/3/528](https://www.mdpi.com/2076-3417/9/3/528)
Informed the beat-gesture detection approach and continuous tempo estimation from periodic hand motion.

**MediaPipe Hands: On-device Real-time Hand Tracking**
Zhang et al., Google Research
[https://arxiv.org/pdf/2006.10214](https://arxiv.org/pdf/2006.10214)
Provides the core CV algorithm used for real-time hand landmark detection enabling the entire interaction system.

Each paper helped shape the core idea: musical conducting gestures can be translated into real-time control signals using low-latency CV pipelines and lightweight ML models.

## How It Works

1. **Capture** – Webcam feed processed through MediaPipe to extract 3D hand landmarks.
2. **Stream** – Client sends landmark data to the backend via WebSockets.
3. **Infer** – Backend computes BPM, volume, intensity and runs the ML classifier for gesture state.
4. **Control** – Audio engine adjusts playback rate and volume in real-time.
5. **Monitor** – Prometheus records inference metrics; Grafana visualizes system behavior.

## Goals

* Explore a domain outside my usual focus by combining ML, backend systems, and music
* Demonstrate real-time inference architecture
* Implement a mini MLOps workflow (metrics, dashboards, model versioning)
* Experiment with CV-driven human-computer musical interfaces
* Produce a polished, creative, and technically credible portfolio project

## Running the Project

Full instructions (including Docker setup, dashboard access, and demo scripts) will be provided once implementation stabilizes.

## Future Work

* More expressive gesture classification
* Additional audio effects (filtering, reverb, dynamics)
* Larger gesture dataset & improved sequence models
* Browser-based version with MediaPipe Web
* MIDI output version for DAW control

---
