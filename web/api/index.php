<?php
require_once '../config.php';
require_once '../lib/Password.php';
require_once '../lib/Request.php';

if (strtolower($_SERVER['REQUEST_METHOD']) !== 'post') {
    // redirection due to invalid request
    header('Location: ' . REDIRECT);
    exit;
}

$request = new Request();
$ok = ($secret_hash = $request->post('secret_hash')) &&
      ($option = $request->post('option')) &&
      password_verify(SECRET_KEY, $secret_hash);

if (!$ok) {
    echo 'Invalid post values.';
    exit;
}

switch($option) {

    case 'email':
        require_once '../lib/phpmailer/PHPMailerAutoload.php';
        $src = $request->post('url_img');
        $filename = $request->post('filename');
        $image_data = file_get_contents($src);
        $url_webpage = $request->post('url_webpage');
        $timestamp = $request->post('timestamp');
        $email = $request->post('email');
        
        $mail = new PHPMailer();
        $mail->isSendmail();
        $mail->setFrom($email, 'pi-surveillance');
        $mail->addAddress($email, 'pi-owner');
        $mail->Subject = '!!! INTRUDER ALERT !!!';
        $mail->addStringAttachment($image_data, $filename, 'base64', 'image/jpeg');
        $body = <<<EOT
<h4>There has been an intruder at {$timestamp} (UTC).</h4>
<br/>
<h4>Goto <a href="{$url_webpage}" target="_blank">Control Room</a></h4>
EOT;
        $mail->msgHTML($body);
        echo $mail->send() ? 'Email sent.' : 'Failed to send email.';
        break;

    /*
    TODO :
    some other options prehaps....
     */
}