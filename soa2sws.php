<?php
$class = 'ALL';
$indexday = 0;
$class = $_POST['class'];
$indexday = $_POST['indexday'];
$cwd =getcwd();
$rc=0;
if  ( ! is_numeric($indexday)) {
   die;
   }
if(strpos($class, ';') !== false){
    echo "Wrong class!";
   die;
   }
   
echo 'Class='.$class.' Indexday='.$indexday.'<br><br>';
ob_start();
if ($indexday != 0)
	{
	passthru('/usr/bin/python3 '.$cwd.'/soa2sws.py '.$indexday.' '.$class, $rc);
	}
else
	{
	system('/usr/bin/python3 '.$cwd.'/soa2sws.py ', $rc);
        echo "RC: ";
        echo $rc;
	}
$output = ob_get_clean(); 
echo nl2br($output);
?>
