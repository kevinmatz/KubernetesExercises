set appname=stockchartapp
set fullcontainername=kevinmatz/%appname%
REM Remove the existing container; -f forces it to quit if it is running 
REM docker rm -f %fullcontainername%
docker rm -f %appname%
REM Build the docker container
docker build -t %fullcontainername% .
REM Bind port 57732 to the container's port 80
REM Link the present directory to the /var/www directory of the container
REM (-v specifies a Docker volume to mount on the container; the host source is before the colon
REM and the destination source is after the colon)
docker run -d -p 57732:80 --name=%appname% -v .:/app %fullcontainername%
