set app=docker.stockchartapptest
REM Build the docker container
docker build -t %app% .
REM Bind port 56733 to the container's port 80
REM Link the present directory to the /var/www directory of the container
REM (-v specifies a Docker volume to mount on the container; the host source is before the colon
REM and the destination source is after the colon)
docker run -d -p 56733:80 --name=%app% -v .:/app %app%
