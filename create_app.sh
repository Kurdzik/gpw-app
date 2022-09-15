docker build -t gpw:1.0 .
docker run -d -it -p 40084:5000 --name gpw-app gpw:1.0
