<?php
if (strtolower($_SERVER['REQUEST_METHOD']) !== 'post') {
    // redirection due to invalid request
    header('Location: /');
    exit;
}

//require_once '../../../../pi-surveillance-module/bootstrap.php';
require_once '../../../pi-surveillance-module/bootstrap.php';
require_once $config['PATH_MODULE'] . 'SurveillanceHandler.php';
$handler = new SurveillanceHandler($_POST);