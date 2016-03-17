<?php
if (isset($_GET['username']))
        $username = $_GET['username'];
if (isset($_GET['cpassord']))
        $cpassword = $_GET['cpassword'];
if (isset($_GET['session']))
	$version = $_GET['version'];
// Set session variables
// $_SESSION["username"] = $username;
// $_SESSION["cpassword"] = $cpassword;
// $_SESSION["version"] = $version;
echo "{version}1.3{/version}{date}".date('Ymd')."{/date}{time}".time()."{/time}"
?>
