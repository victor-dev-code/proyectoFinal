#! /bin/bash
while [ "$OPC" != "3" ];
do
#menu
echo "elige una opcion"
echo "1.-levantar servidor"
echo "2.-relizar migraciones"
echo "3.-salir"
read OPC 
case $OPC in
1)
echo "escribe el nombre del archvo env"
read FILE
[[ -f $FILE ]] || { echo se esperaba como primer archivo env ; exit 1; }
for linea in $(ccdecrypt -c $FILE); do
	echo export $linea
	export $linea 
done 

python3 manage.py runserver 0.0.0.0:8080
;;
2)
echo "escribe el nombre del archvo env"
read FILE
[[ -f $FILE ]] || { echo se esperaba como primer archivo env ; exit 1; }
for linea in $(ccdecrypt -c $FILE); do
        echo export $linea
        export $linea
done
python3 manage.py makemigrations
python3 manage.py migrate
;;
3)
exit
;;
*)
echo "opcion no valida"
;;

esac 
done 
