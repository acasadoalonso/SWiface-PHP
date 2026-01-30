<?php
$pilotname='';
$firstname='';
$ioccountry='';
$sl='0';
$args =' -w True ';
if (isset($_GET['ioccountry']))
        $ioccountry=$_GET['ioccountry'];
        $args= $args.' -c '.$ioccountry;
if (isset($_GET['pilotname']))
        $pilotname=$_GET['pilotname'];
        if (strpos($pilotname, ' ')){
           $pilotname=str_replace(' ','#', $pilotname);
           }
        if ($pilotname != ' ' and $pilotname != '') {
           $args= $args.' -n '.$pilotname;
           }
if (isset($_GET['firstname']))
        $firstname=$_GET['firstname'];
        if (strpos($firstname, ' ')){
           $firstname=str_replace(' ','#', $firstname);
           }
        if ($firstname != ' ' and $firstname != '') {
           $args= $args.' -f '.$firstname;
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
