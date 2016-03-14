<?php
$rc=0;
ob_start();
passthru('/usr/bin/python2.7 /var/www/html/eventgroups.py ', $rc);
$output = ob_get_clean(); 
echo $output;
?>
