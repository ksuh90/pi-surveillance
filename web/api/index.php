<?php
require_once '../autoloader.php';
require_once '../config.php';
require_once '../lib/Password.php';
require_once '../lib/Request.php';
require_once '../lib/phpmailer/PHPMailerAutoload.php';
use Pubnub\Pubnub;

if (strtolower($_SERVER['REQUEST_METHOD']) !== 'post') {
    // redirection due to invalid request
    header('Location: ' . REDIRECT);
    exit;
}

$request = new Request();
$option = $request->post('option');
$pubnub_channel = 'pi-surveillance';
$pubnub = new Pubnub(array(
    'publish_key' => PUBNUB_PUBLISH_KEY,
    'subscribe_key' => PUBNUB_SUBSCRIBE_KEY
));

switch($option) {

    case 'take_picture':
    case 'pause':
    case 'resume':
    case 'off':
        // TODO : verify csrf token
        session_start();
        if ($_SESSION['csrf_token'] !== $request->post('csrf_token')) {
            echo 'Invalid post values.';
            break;
        }
        $publish_result = $pubnub->publish($pubnub_channel, $option);
        break;

    case 'email':
        $secret_hash = $request->post('secret_hash')
        if (!password_verify(SECRET_KEY, $secret_hash)) {
            echo 'Invalid post values.';
            break;
        }

        $src         = $request->post('url_img');
        $image_data  = file_get_contents($src);
        $filename    = $request->post('filename');        
        $url_webpage = $request->post('url_webpage');
        $timestamp   = $request->post('timestamp');
        $email       = $request->post('email');

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
}

exit;