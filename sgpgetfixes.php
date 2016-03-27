<?php
$trackid="0";
if (isset($_GET['id']))
        $id = $_GET['id'];
$since="0";
if (isset($_GET['since']))
        $since = $_GET['since'];
$compression='none';
if (isset($_GET['compression']))
        $compression = $_GET['compression'];
$cwd =getcwd();
$rc=0;
ob_start();
passthru('/usr/bin/python2.7 '.$cwd.'/sgpgetfixes.py '.$id.' '.$since, $rc);
$output = ob_get_clean(); 
if ($compression == "gzip")
                {
                print gzencode($output);
                }
        else    {
                print $output;
                }
?>
