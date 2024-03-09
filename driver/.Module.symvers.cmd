cmd_/home/szekler/tmf882x/Module.symvers :=  sed 's/ko$$/o/'  /home/szekler/tmf882x/modules.order | scripts/mod/modpost -m -a    -o /home/szekler/tmf882x/Module.symvers -e -i Module.symvers -T - 
