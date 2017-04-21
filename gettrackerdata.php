<?php

//$mysql=true;
$dbhost="casadonfs";
$dbuser="ogn";
$dbpass="ogn";
$dbname="SWIFACE";
$dtzlocal= new DateTimeZone('Europe/madrid');
$dtlocal = new DateTime("now", $dtzlocal);
$tslocal = $dtlocal->format("O");

if (isset($_GET['username']))
        $username = $_GET['username'];
if (isset($_GET['cpassord']))
        $cpassword = $_GET['cpassword'];
$contestname = $_GET['contestname'];
$querytype   = $_GET['querytype'];
$trackerid   = $_GET['trackerid'];
$starttime   = $_GET['starttime'];
$endtime     = $_GET['endtime'];
$compression = $_GET['compression'];
$syear = substr($starttime, 2, 6);
$stime = substr($starttime, 8);
$eyear = substr($endtime, 2, 6);
$etime = substr($endtime, 8);
$ini_array = parse_ini_file("/etc/local/SWSconfig.ini");
if ($syear == date('ymd'))
	{
	$DBpath=$ini_array['DBpath'];
	//echo "Today";
	}
else 
	{
	$DBpath=$ini_array['DBpath'].'archive';
	}
	
$DB=$DBpath.'SWiface.db';
if ($querytype == "getintfixes")
	{
	$output= "{datadelay}0{/datadelay}\n";
	$output= $tslocal;
	$query1="SELECT idflarm, date, time, latitude, longitude, altitude FROM OGNDATA WHERE idflarm = '".$trackerid."'";
	$query2=" and date = '".$syear."' and time >= '".$stime."' and time <= '".$etime."'"." order by time";
	$query=$query1.$query2;
	if ($mysql)
		{
		$db = new mysqli($dbhost, $dbuser, $dbpass, $dbname);
		}
	else
		{
		$db = new SQLite3($DB, SQLITE3_OPEN_READONLY);
		}
	 
	$results = $db->query($query);
	 
	if ($results) 
	   {
	   if ($mysql)
		{
	   	$row = $results->fetch_array() ;
		}
	   else
		{
	   	$row = $results->fetchArray() ;
		}
	   while ($row)
		{
		$idflarm=$row[0];
		$date   =$row[1];
		$time   =$row[2];
		$lati   =$row[3];
		$long   =$row[4];
		$alti   =$row[5];
		$output .= $idflarm.',20'. $date. $time. ','. $lati. ','. $long. ','. $alti. ",1\n";
	   	if ($mysql)
			{
	   		$row = $results->fetch_array() ;
			}
	   	else
			{
	   		$row = $results->fetchArray() ;
			}
		}
	    $db->close(); 
	    }
	if ($_GET["compression"] == "gzip") 
		{
      		print gzencode($output);
       		} 
	else 	{
      		print $output;
  	        }
	}
?>
