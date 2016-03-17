<?php
$username = $_GET['username'];
$cpassword = $_GET['cpassword'];
$version = $_GET['version'];
// Set session variables
$_SESSION["username"] = $username;
$_SESSION["cpassword"] = $cpassword;
$_SESSION["version"] = $version;
echo "{version}1.3{/version}{date}".date('Ymd')."{/date}{time}".time()."{/time}"
?>
