<?php
$rc=0;
ob_start();
passthru('/usr/bin/python2.7 /var/www/event.py ', $rc);
$output = ob_get_clean(); 
echo $output;
?>
