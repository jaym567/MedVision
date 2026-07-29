# Technical Decisions

## Backend Framework

Decision:
FastAPI

Reason:
High-performance Python API with excellent ML ecosystem support.


## Frontend Viewer

Decision:
Cornerstone3D

Reason:
Medical imaging focused WebGL viewer.


## Storage

Decision:
Local filesystem initially.

Future:
S3-compatible storage.


## AI Architecture

Decision:
Model registry pattern.

Reason:
Allow adding new imaging models without changing application logic.
