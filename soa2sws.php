<?php
$class = $_POST['class'];
$indexday = $_POST['indexday'];
$cwd =getcwd();
$rc=0;
echo 'Class='.$class.' Indexday='.$indexday.'<br><br>';
ob_start();
if ($indexday != 0)
	{
	passthru('/usr/bin/python3 '.$cwd.'/soa2sws.py '.$indexday.' '.$class, $rc);
	}
else
	{
	system('/usr/bin/python3 '.$cwd.'/soa2sws.py ', $rc);
        echo "ttt";
        echo $rc;
	}
$output = ob_get_clean(); 
echo nl2br($output);
?>
