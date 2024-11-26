#!/bin/bash

docker build -t danbit2024/frontend-app:v1 .

docker push danbit2024/frontend-app:v1
