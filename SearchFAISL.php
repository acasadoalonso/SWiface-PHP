<?php
$pilotname='';
$ioccountry='';
$sl='0';
$args =' -w True ';
if (isset($_GET['ioccountry']))
        $ioccountry=$_GET['ioccountry'];
        $args= $args.' -c '.$ioccountry;
if (isset($_GET['pilotname']))
        $pilotname=$_GET['pilotname'];
        //echo "::".$pilotname."::";
        if ($pilotname != ' ' and $pilotname != '') {
           $args= $args.' -n '.$pilotname;
           }
if (isset($_GET['sl']))
        $sl=$_GET['sl'];
        if ($sl != ' ' and $sl != '') {
           if  ( ! is_numeric($sl)) {
            echo "The Sporing License has to be numeric ...";
            die;
           }
           $args= $args.' -s '.$sl;
           }

$cwd =getcwd();
$rc=0;
ob_start();
//echo $args ;
passthru('/usr/bin/python3  ./SearchFAISL.py '.$args, $rc);
$output = ob_get_clean();
echo nl2br($output);
exit;
?>
