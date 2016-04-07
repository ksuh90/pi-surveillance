<?php
$jsApp = array(
    'pubnub_channel' => $config['PUBNUB_CHANNEL'],
    'pubnub_sub_key' => $config['PUBNUB_SUBSCRIBE_KEY'],
    'pubnub_pub_key' => $config['PUBNUB_PUBLISH_KEY'],
    'url' => array(
        'api' => $config['URL_BASE'] . 'api/?',
        'img' => $config['URL_BASE'] . 'img/?'
    )
);
$js = $config['URL_BASE'] . 'scripts/dist/main.bundle.js';
$style = $config['URL_BASE'] . 'css/style.css';
?>
<!doctype html>
<html class="no-js" lang="">
    <head>
        <meta charset="utf-8">
        <title>pi-surveillance</title>
        <meta http-equiv="x-ua-compatible" content="ie=edge">        
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.6/css/bootstrap.min.css">
        <link rel="stylesheet" href="<?php echo $style; ?>">
    </head>
    <body>
        <script>
        window.APP = <?php echo json_encode($jsApp); ?>;
        </script>
        
        <div id="container"></div>

        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.blockUI/2.70/jquery.blockUI.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.6/js/bootstrap.min.js"></script>
        <script src="https://cdn.pubnub.com/pubnub-3.14.5.min.js"></script>
        <script src="<?php echo $js; ?>"></script>
    </body>
</html>