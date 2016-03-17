<?php
$rc=0;
$cwd =getcwd();
ob_start();
passthru('/usr/bin/python2.7 '.$cwd.'/eventgroups.py ', $rc);
$output = ob_get_clean(); 
echo $output;
?>
