<?php
$myfile = fopen("contests.txt", "r") or die("Unable to open file!");
echo fread($myfile,filesize("contests.txt"));
fclose($myfile);
?>
