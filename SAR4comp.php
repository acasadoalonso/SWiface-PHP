<?php
$competype='XXX';
$flarmid='NOFLARMID';
$registration ='NOREG';
$sgpid='0';
$clientid='0';
$secretkey='0';
$day='0';
if (isset($_GET['competype']))
        $competype=$_GET['competype'];
if (isset($_GET['flarmid']))
        $flarmid=$_GET['flarmid'];
if (isset($_GET['registration']))
        $registration=$_GET['registration'];
if (isset($_GET['sgpid']))
        $sgpid=$_GET['sgpid'];
if (isset($_GET['clientid']))
        $clientid=$_GET['clientid'];
if (isset($_GET['secretkey']))
        $secretkey=$_GET['secretkey'];
if (isset($_GET['day']))
        $day=$_GET['day'];
if ($flarmid == '') $flarmid = 'NOFLARMID';        
if ($registration == '') $registration = 'NOREG';        
if ($sgpid == '') $sgpid = '0';        
if ($clientid == '') $clientid = '0';        
if ($secretkey == '') $secretkey = '0';        
if ($day == '') $day = '0';        

$cwd =getcwd();
$rc=0;
ob_start();
$args='-t '.$competype.' -f '.$flarmid.' -r '.$registration.' -g '.$sgpid.' -c'.$clientid.' -s '.$secretkey.' -i '.$day.' -w True ';
//echo $args ;
passthru('/usr/bin/python3  ./SAR4comp.py '.$args, $rc);
$output = ob_get_clean();
echo nl2br($output);
exit;
?>
