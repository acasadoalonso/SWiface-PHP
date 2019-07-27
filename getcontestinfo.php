<?php
if (isset($_GET['username']))
	$username = $_GET['username'];
if (isset($_GET['cpassord']))
	$cpassword = $_GET['cpassword'];
$contestname = $_GET['contestname'];
if (isset($_GET['date']))
	$cdate = $_GET['date'];
else
	$cdate = 0;

$cwd =getcwd();
$gcucpath=$cwd."/"; 
#{date}20160309{/date}{task}1{/task}{validday}1{/validday} 
$ci1="{date}";
$ci2="{/date}{task}1{/task}{validday}1{/validday}";
if ($cdate == 0)
	{
	$dtz= new DateTimeZone("UTC");
	$dt=  new DateTime("now", $dtz);
	$ts= $dt->format("U");
	$ts -=86400*5;

	$date = date_create_from_format('U', $ts);
	$tf =  $date->format("Ymd");
	echo $ci1,$tf,$ci2;

	$ts += 86400;
	$date = date_create_from_format('U', $ts);
	$tf =  $date->format("Ymd");
	echo $ci1,$tf,$ci2;

	$ts += 86400;
	$date = date_create_from_format('U', $ts);
	$tf =  $date->format("Ymd");
	echo $ci1,$tf,$ci2;

	$ts += 86400;
	$date = date_create_from_format('U', $ts);
	$tf =  $date->format("Ymd");
	echo $ci1,$tf,$ci2;

	$ts += 86400;
	$date = date_create_from_format('U', $ts);
	$tf =  $date->format("Ymd");
	echo $ci1,$tf,$ci2;

	echo $ci1,$dt->format("Ymd"),$ci2;
	}
elseif ($contestname == "LIVE")
	{
	//echo $cdate,"TD:", date('Ymd');
	if ($cdate == date('Ymd'))
		{
		$rc=0;
		
		ob_start();
		passthru('/usr/bin/python3 '.$gcucpath.'gencuc.py '.$_SERVER['REMOTE_ADDR'].' >>cucmsgs.log', $rc);
		$output = ob_get_clean(); 
		#echo $rc, $output;
		if ($rc == 0)
			{
			$myfilename="cuc/".$contestname.$cdate.".cuc";
			$myfile =             fopen("cuc/".$contestname.$cdate.".cuc", "r") or die("Unable to open file!".$myfilename);
			echo fread($myfile,filesize("cuc/".$contestname.$cdate.".cuc"));
			fclose($myfile);
			}
		else
			{echo "No flights found...";}
		}
	else
		{
		$myfilename="cuc/".$contestname.$cdate.".cuc";
		$myfile =             fopen("cuc/".$contestname.$cdate.".cuc", "r") or die("Unable to open file!".$myfilename);
		echo fread($myfile,filesize("cuc/".$contestname.$cdate.".cuc"));
		fclose($myfile);
		}
	}
else    
	{
	$myfilename="cuc/".$contestname.$cdate.".cuc";
	$myfile =             fopen("cuc/".$contestname.$cdate.".cuc", "r") or die("Unable to open file!".$myfilename);
	echo fread($myfile,filesize("cuc/".$contestname.$cdate.".cuc"));
	fclose($myfile);
	}
?>
