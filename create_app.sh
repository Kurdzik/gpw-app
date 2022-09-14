docker build -t gpw .
docker run -d -it -p 40084:5000 --name gpw-app gpw:1.0
