#!bin/bash

minikube start --driver=docker

#building images
minikube image build -t frontend -f frontend/Dockerfile .
minikube image build -t backend  -f backend/Dockerfile .
minikube image build -t sqlserver -f sql/Dockerfile .

#create rabbbitmq cluster
kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"
kubectl apply -f kubernetes/rabbitmq-cluster.yaml

#create memcache service
kubectl apply -f kubernetes/memcached.yaml
kubectl apply -f kubernetes/memcached-service.yaml

#create sql server
kubectl apply -f kubernetes/mysql.yaml

#create the container of the application
kubectl apply -f kubernetes/frontend.yaml
kubectl apply -f kubernetes/frontend-service.yaml
kubectl apply -f kubernetes/backend.yaml

#retrieve the expose ip of the frontend service
minikube service frontend-service --url

