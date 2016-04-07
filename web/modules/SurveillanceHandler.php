<?php
require_once 'phpmailer/PHPMailerAutoload.php';


class SurveillanceHandler {

    private $error_msg = null;
    private $resp = array('ok' => true);


    function __construct(array $data) {

        $this->execute_option($data);
    }

    private function execute_option(array $data) {
        if (isset($data['option'])) {
            $func = $data['option'];
            if (method_exists($this, $func)) {
                $this->$func($data);
                return;
            }
        }        
        $this->set_error_msg('Invalid option.');
    }

    private function get_log(array $data) {
        global $config;
        $auth = $config['CLOUDANT_API_KEY'].':'.$config['CLOUDANT_API_PASS'];
        $host = $config['CLOUDANT_HOST'];
        $db_name = $config['CLOUDANT_DB_NAME'];
        $url = "https://{$auth}@{$host}/{$db_name}/_design/view/_view/log" .
               "?reduce=false&include_docs=true&descending=true";
        $log = json_decode(file_get_contents($url))->rows;
        foreach ($log as $key => $value) {
            unset($value->doc->_rev);
            $log[$key] = $value->doc;
        }
        $this->resp['log'] = $log;
        $this->respond();
    }

    private function email(array $data) {
        global $config;
        if ($config['SECRET_KEY'] !== $data['secret_key']) {
            echo 'Invalid secret post values.';
            return;
        }

        $image_data  = file_get_contents($data['url_img']); 
        $url_webpage = $data['url_webpage'];
        $timestamp   = $data['timestamp'];
        $email       = $data['email'];

        $mail = new PHPMailer();
        $mail->isSendmail();
        $mail->setFrom($email, 'pi-surveillance');
        $mail->addAddress($email, 'pi-owner');
        $mail->Subject = '!!! INTRUDER ALERT !!!';
        $mail->addStringAttachment(
            $image_data, $data['filename'], 'base64', $data['img_type']);
        $body = <<<EOT
<h4>There has been an intruder at {$timestamp} (UTC).</h4><br/>
<h4>Goto <a href="{$url_webpage}" target="_blank">Control Room</a></h4>
EOT;
        $mail->msgHTML($body);
        echo $mail->send() ? 'Email sent.' : 'Failed to send email.';
        return;
    }

    private function set_error_msg($msg) {
        if (!isset($this->error_msg)) {
            $this->error_msg = $msg;
        }
    }

    private function respond() {
        echo json_encode($this->resp);
    }
   
}