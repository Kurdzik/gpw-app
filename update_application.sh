###################################################################################
# Script used to stop currently running container, update the code and restart it 
###################################################################################

# remove existing directory
rm -r gpw-app

# clone fresh repo
git clone https://github.com/Kurdzik/gpw-app.git

# stop runing container
docker stop gpw-app

# remove container 
docker rm gpw-app

# remove image
docker image rm gpw:1.0

# built new image
docker build -t gpw:1.0 .

# start new container
docker run -d -it -p 40084:5000 --name gpw-app gpw:1.0
