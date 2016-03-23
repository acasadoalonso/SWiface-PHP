<?php
$cwd =getcwd();
$rc=0;
echo $cwd, "-";
$dtz= new DateTimeZone("UTC");
$dt=  new DateTime("now", $dtz);

$ts= $dt->format("U");
echo  "/", $dt->format("Ymd"),":", $ts;
$ts -=86400; 
$date = date_create_from_format('U', $ts);
$tf =  $date->format("Y-m-d");
echo print  ":", $cwd, ";", $tf;
?>
