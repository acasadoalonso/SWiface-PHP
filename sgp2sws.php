<?php
$compid = $_POST['compid'];
$indexday = $_POST['indexday'];
if ($indexday == '')
   $indexday=0;

$cwd =getcwd();
$rc=0;
echo 'COMPid='.$compid.' Indexday='.$indexday.'<br><br>';
if  ( ! is_numeric($compid)) {
   die;
   }
ob_start();
if (is_numeric($indexday)){
	passthru('/usr/bin/python3 '.$cwd.'/sgp2sws.py '.$compid.' '.$indexday, $rc);
	} 
else {
	passthru('/usr/bin/python3 '.$cwd.'/sgp2sws.py '.$compid.' "'.$indexday.'"', $rc);
	}
$output = ob_get_clean(); 
echo nl2br($output);
?>
