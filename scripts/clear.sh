docker rmi -f $(docker images --filter "dangling=true" -q --no-trunc)
docker rm $(docker ps -aq)
