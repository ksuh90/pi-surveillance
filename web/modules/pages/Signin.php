<?php
$csrfToken = \Token::create();
$_SESSION['csrfToken'] = $csrfToken;
$onsubmit = $config['URL_BASE'];
?>
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>pi-surveillance</title>
        <meta http-equiv="x-ua-compatible" content="ie=edge">        
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.6/css/bootstrap.min.css">
        <style>
        body{padding-top:40px;padding-bottom:40px;background-color:#eee}.form-signin{max-width:330px;padding:15px;margin:0 auto}.form-signin .checkbox,.form-signin .form-signin-heading{margin-bottom:10px}.form-signin .checkbox{font-weight:400}.form-signin .form-control{position:relative;height:auto;-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box;padding:10px;font-size:16px}.form-signin .form-control:focus{z-index:2}.form-signin input[type=email]{margin-bottom:-1px;border-bottom-right-radius:0;border-bottom-left-radius:0}.form-signin input[type=password]{margin-bottom:10px;border-top-left-radius:0;border-top-right-radius:0}
        </style>
    </head>
    <body>
        <div class="container">
            <form class="form-signin" onsubmit="<?php echo $onsubmit; ?>" method="post">
                <h2 class="form-signin-heading">Please sign in</h2>
                <input type="hidden" name="csrfToken" value="<?php echo $csrfToken; ?>">
                <label for="inputPassword" class="sr-only">Password</label>
                <input type="password" class="form-control" placeholder="Password" name="p" required>
                <button class="btn btn-lg btn-primary btn-block" type="submit">Sign in</button>
            </form>
        </div>
    </body>
</html>