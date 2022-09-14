<?php
$compid = $_POST['compid'];
$indexday = $_POST['indexday'];
$cwd =getcwd();
$rc=0;
if  ( ! is_numeric($indexday)) {
   die;
   }
if(strpos($compid, ';') !== false){
    echo "Wrong compid!";
   die;
   }

echo 'COMPid='.$compid.' Indexday='.$indexday.'<br><br>';
ob_start();
if (is_numeric($indexday)){
	passthru('/usr/bin/python3 '.$cwd.'/str2sws.py '.$compid.' '.$indexday, $rc);
	} 
else {
	passthru('/usr/bin/python3 '.$cwd.'/str2sws.py '.$compid.' "'.$indexday.'"', $rc);
	}
$output = ob_get_clean(); 
echo nl2br($output);
?>
