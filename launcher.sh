#!/bin/bash

launch()
{
    sudo docker-compose up
}

updateSourceFromGit()
{
    # NOTE: This function is for updating fromt Github.

    # container_name="parameter_optimizator"
    # if [ -z $1 ]
    # then
    #     container_name="parameter_optimizator"
    # else
    #     container_name="$1"
    # fi

    # echo "1. Dừng container" $container_name
    # sudo docker stop $container_name

    # echo "2. Fetch code từ branch master"
    # sudo git fetch --all
    # sudo git reset --hard origin/master

    # echo "3. Khởi động lại container" $container_name
    # sudo docker start parameter_optimizator 

}


print_help()
{
    echo "** Usage of Launcher"
    echo "laucher [] []"
    echo "-l or --lauch or no argument  :  Launch the frontend and backend"
    echo "-h or --help                  :  Show help"
}

case $1 in
    -u | --update-git )
        if [ -z $2 ] 
        then
            updateSourceFromGit
        else
            updateSourceFromGit $2
        fi        
        ;;
    -h | --help )
        print_help
        ;;
    * )
        launch
        ;;
esac
