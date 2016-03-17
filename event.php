<?php
$eventid = $_GET['eventid'];
$cwd =getcwd();
$rc=0;
ob_start();
passthru('/usr/bin/python2.7 '.$cwd.'/event.py '.$eventid, $rc);
$output = ob_get_clean(); 
echo $output;
?>
