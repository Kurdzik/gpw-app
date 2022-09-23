###################################################################################
# Script used to stop currently running container, update the code and restart it 
###################################################################################

# stop runing container
docker stop gpw-app

# remove container 
docker rm gpw-app

# remove image
docker image rm gpw:1.0

# built new image


# start new container
docker build -t gpw:1.0 . && docker run -d -p 40084:5000 --restart unless-stopped --name gpw-app gpw:1.0
