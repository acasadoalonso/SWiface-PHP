<?php
$class = $_POST['class'];
$indexday = $_POST['indexday'];
$cwd =getcwd();
$rc=0;
echo 'Class='.$class.' Indexday='.$indexday.'<br><br>';
ob_start();
passthru('/usr/bin/python2.7 '.$cwd.'/soa2sws.py '.$indexday.' '.$class, $rc);
$output = ob_get_clean(); 
echo nl2br($output);
?>
