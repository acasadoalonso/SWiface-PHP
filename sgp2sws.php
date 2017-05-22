<?php
$compid = $_GET['compid'];
$indexday = $_GET['indexday'];
$cwd =getcwd();
$rc=0;
echo $compid.' '.$indexday;
ob_start();
passthru('/usr/bin/python2.7 '.$cwd.'/sgp2sws.py '.$compid.' '.$indexday, $rc);
$output = ob_get_clean(); 
echo $output;
?>
