<?php
    $BASE_URL = "http://query.yahooapis.com/v1/public/yql";

    $yql_query = 'select wind from weather.forecast where woeid in (766273)';
    $yql_query_url = $BASE_URL . "?q=" . urlencode($yql_query) . "&format=json";

    // Make call with cURL
    $session = curl_init($yql_query_url);
    curl_setopt($session, CURLOPT_RETURNTRANSFER,true);
    $json = curl_exec($session);
    // Convert JSON to PHP object
     $phpObj =  json_decode($json);
    var_dump($phpObj);

?>                                    
