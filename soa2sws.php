<?php
$class = 'ALL';
$indexday = 0;
if (isset($_POST['class']))
   {
   $class = $_POST['class'];
   }
if (isset($_POST['indexday']))
   {
   $indexday = $_POST['indexday'];
   }
$cwd =getcwd();
if ($class == '')
   $class='ALL';
if ($indexday == '')
   $indexday=0;
$rc=0;
if  ( ! is_numeric($indexday)) {
   die;
   }
else {
   $indexday = abs($indexday);
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
