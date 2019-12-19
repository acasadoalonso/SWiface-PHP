<?php
require_once 'config.php';
$synch = $_GET['synch'];
if ( $synch == 'synch') {
	ob_start();
	passthru("/usr/bin/pt-table-sync  --execute --verbose --user=".$DBuser." --password=".$DBpasswd." h=chileogn.ddns.net,D=APRSLOG,t=TRKDEVICES h=localhost");
	$var = ob_get_contents();
	ob_end_clean(); 
 	echo "RC=".nl2br($var)."\n";
	//echo "git pull done\n\n";
}
//echo var_dump($synch);
?>hi

