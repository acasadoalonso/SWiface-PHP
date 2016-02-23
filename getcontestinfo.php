<?php
$username = $_GET['username'];
$cpassword = $_GET['cpassword'];
$contestname = $_GET['contestname'];
$cdate = $_GET['date'];
if ($cdate == 0)
	{
	$myfile = fopen("contestinfo.txt", "r") or die("Unable to open file!");
	echo fread($myfile,filesize("contestinfo.txt"));
	fclose($myfile);
	}
else    {
	$myfile =             fopen($contestname.$cdate.".cuc", "r") or die("Unable to open file!");
	echo fread($myfile,filesize($contestname.$cdate.".cuc"));
	fclose($myfile);
	}
?>
