<?php
//$username    = $_GET['username'];
//$cpassword   = $_GET['cpassword'];
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
if ($syear == date('ymd'))
	{
	$DBpath='/nfs/OGN/SWdata/';
	//echo "Today";
	}
else 
	{
	$DBpath='/nfs/OGN/SWdata/archive/';
	}
	
$DB=$DBpath.'SWiface.db';
// echo $DB; 
// phpinfo();
if ($querytype == "getintfixes")
	{
	$output= "{datadelay}0{/datadelay}\n";
	$query1="SELECT idflarm, date, time, latitude, longitude, altitude FROM OGNDATA WHERE idflarm = '".$trackerid."'";
	$query2=" and date = '".$syear."' and time >= '".$stime."' and time <= '".$etime."'";
	$query=$query1.$query2;
	 // echo $query;
	$db = new SQLite3($DB, SQLITE3_OPEN_READONLY);
	// echo var_dump($db); 
	$results = $db->query($query);
	// echo var_dump($results); 
	while ($row = $results->fetchArray()) 
		{
	    	// echo var_dump($row);
		// echo count($row); 
		$idflarm=$row[0];
		$date   =$row[1];
		$time   =$row[2];
		$lati   =$row[3];
		$long   =$row[4];
		$alti   =$row[5];
		$output .= $idflarm.',20'. $date. $time. ','. $lati. ','. $long. ','. $alti. ",1\n";
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
