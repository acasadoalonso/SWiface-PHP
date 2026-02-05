<?php
$compid='';
if (isset($_GET['compid']))
        $compid=$_GET['compid'];
$cwd =getcwd();
$rc=0;
ob_start();
$args='-c '.$compid.' -w True ';
//echo "TTTi ".$args ;
passthru('/usr/bin/python3  ./SSextractresults.py '.$args, $rc);
$output = ob_get_clean();
echo nl2br($output);
exit;
?>
