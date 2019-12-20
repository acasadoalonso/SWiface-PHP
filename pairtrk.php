<?php
$action='list';
$trk='ALL';
$flarmid='NOTVALIDFLARMID';
$owner='NOTVALIDOWNER';
if (isset($_GET['action'])){
        $action=$_GET['action'];
}
if (isset($_GET['trk']))
	$trk=$_GET['trk'];
if (isset($_GET['flarmid']))
       	$flarmid=$_GET['flarmid'];
if (isset($_GET['owner']))
       	$owner=$_GET['owner'];
if (isset($_GET['deleteyn']))
       	$deleteyn=$_GET['deleteyn'];
if (isset($_GET['active']))
       	$active=$_GET['active'];
	
#print $trk.$flarmid.$owner.$deleteyn;
if ($action != 'edit'){

	$cwd =getcwd();
	$rc=0;
	ob_start();

	passthru('/usr/bin/python3  ./pairtrk.py '.$action.' '.$trk.' '.$flarmid.' "'.$owner.'" '.$deleteyn.' '.$active.' ', $rc);
	if ($action == 'update' or $action == 'add')
		passthru('/usr/bin/python3  ./pairtrk.py list ', $rc);

	$output = ob_get_clean();
	echo nl2br($output);
	exit;
}
?>

<html>
<head><meta charset="UTF-8"></head>
<title>Pair trackers</title>
<body>
<IMG src="gif/ogn-logo-ani.gif" border=1 alt=[image]>
<H1>Please fill the fields : </H1>
<hr>
<?php #print "Input:".$action.$trk.$flarmid.$owner ?>
<?php $owner=trim($owner, '"'); print $owner; ?>
<form method=GET action="./pairtrk.php">
	<P><B>Enter the selected fields in order to update the pair of the trackers: </B> </P></br> 
	Delete ? [Y/N] <select name=deleteyn> <option>N<option>Y</select>
	</br>
	</br>
	</br>OGNtracker<P>     <input type="text" name="trk"      value="<?php print $trk?>" />
	</br>FlarmID to pair<P><input type="text" name="flarmid"  value="<?php print $flarmid?>"/>
	</br>Owner<P>          <input type="text" name="owner"    value="<?php print $owner?>"/>
	</br>Active<P>         <input type="text" name="active"   value="<?php print $active?>"/>
	</br><P><input type=submit name=action value='update'>
</form>
</body></html>

