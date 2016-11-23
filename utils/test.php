<?php
$dtzlocal=  new DateTimeZone('America/Santiago');
$dtlocal=  new DateTime("now", $dtzlocal);
$tslocal= $dtlocal->format("O");
echo $tslocal,'/';
echo $tslocal*60,'<<<';
$t='09'*3600+45*60+31;
echo '-T-', $t, '-';
$t=$t+$tslocal*60;
$h=intval($t/3600);
$m=intval(($t-$h*3600)/60);
$s=intval($t-$h*3600-$m*60);

echo ':::', $h,':',$m,':',$s,'---', $h*10000+$m*100+$s;

?>
