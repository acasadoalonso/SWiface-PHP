<?php
require_once 'config.php';
$synch = $_GET['synch'];
if ( $synch == 'synch') {
	ob_start();
        $DBpasswd=base64_decode($DBpasswd);
        $e=gzuncompress($DBpasswd, 64);

	passthru("/usr/bin/pt-table-sync  --execute --verbose --user=".$DBuser." --password=".$e." h=chileogn.ddns.net,D=APRSLOG,t=TRKDEVICES h=localhost");
	$var = ob_get_contents();
	ob_end_clean(); 
 	echo "RC=".nl2br($var)."\n";
	//echo "git pull done\n\n";
}
else
	echo "No synch...";
//echo var_dump($synch);
?>hi

