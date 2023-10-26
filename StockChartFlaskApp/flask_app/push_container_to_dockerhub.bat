REM Prerequisite: Build container using "build_and_run_docker_container.bat" first
REM Prerequisite: Make sure these constant match "build_and_run_docker_container.bat"
set appname=stockchartapp
set fullcontainername=kevinmatz/%appname%
docker push %fullcontainername%
