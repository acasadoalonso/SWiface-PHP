<?php
    $BASE_URL = "http://query.yahooapis.com/v1/public/yql";

    $yql_query = "select * from weather.forecast where woeid in (766273) and u='c'";
    $yql_query_url = $BASE_URL . "?q=" . urlencode($yql_query) . "&format=json";
    // echo $yql_query_url;
    // Make call with cURL
    $session = curl_init($yql_query_url);
    // curl_setopt($session, CURLOPT_URL,$yql_query_url );
    curl_setopt($session, CURLOPT_RETURNTRANSFER,true);
    // set URL and other appropriate options
    curl_setopt($session, CURLOPT_HEADER, 0);
    $json = curl_exec($session);
    // Convert JSON to PHP object
    $phpObj =  json_decode($json);
    //var_dump($phpObj); 
    if(!is_null($phpObj->query->results)){
    	$desc = $phpObj->query->results->channel->item->description;
    	$c    = $phpObj->query->results->channel->wind->chill;
    	$d    = $phpObj->query->results->channel->wind->direction;
    	$s    = $phpObj->query->results->channel->wind->speed;
    	$t    = $phpObj->query->results->channel->item->title;
    	echo '<html><head><title> Test PHP</title></head><body><pre><b>';
    	echo $t; 
    	echo '<br /></b><br />Wind   '; 
    	echo 'Chill: '; 
    	echo $c; 
    	echo ' C Direction: '; 
    	echo $d;
    	echo ' degrees Speed: '; 
    	echo $s;
    	echo ' Km/h.  '; 
    	echo $desc;
    	echo '</pre></body></html>';
    }
?>
