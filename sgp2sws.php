<?php
$compid = $_POST['compid'];
$indexday = $_POST['indexday'];
$cwd =getcwd();
$rc=0;
echo 'COMPid='.$compid.' Indexday='.$indexday;
ob_start();
passthru('/usr/bin/python2.7 '.$cwd.'/sgp2sws.py '.$compid.' '.$indexday, $rc);
$output = ob_get_clean(); 
echo $output;
?>
