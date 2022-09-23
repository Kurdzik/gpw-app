###################################################################################
# Script used to stop currently running container, update the code and restart it 
###################################################################################
docker stop gpw-app
docker rm gpw-app
docker image rm gpw:1.0
docker build -t gpw:1.0 .
docker run -d -p 40084:5000 --restart unless-stopped --name gpw-app gpw:1.0