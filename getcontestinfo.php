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
elseif ($contestname == "LIVE")
	{
	$rc=0;
	ob_start();
	passthru('/usr/bin/python2.7 /var/www/gencuc.py >>cucmsgs.log', $rc);
	$output = ob_get_clean(); 
	# echo $output;
	if ($rc == 0)
		{
		$myfile =             fopen("cuc/".$contestname.$cdate.".cuc", "r") or die("Unable to open file!");
		echo fread($myfile,filesize("cuc/".$contestname.$cdate.".cuc"));
		fclose($myfile);
		}
	else
		{echo "No flights found";}
	}
else    {
	$myfile =             fopen("cuc/".$contestname.$cdate.".cuc", "r") or die("Unable to open file!");
	echo fread($myfile,filesize("cuc/".$contestname.$cdate.".cuc"));
	fclose($myfile);
	}
?>
