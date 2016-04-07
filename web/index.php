<?php
//require_once '../../../pi-surveillance-module/bootstrap.php';
require_once '../../pi-surveillance-module/bootstrap.php';
require_once $config['PATH_MODULE'] . 'Password.php';

session_start();
$path_module = $config['PATH_MODULE'];

if (strtolower($_SERVER['REQUEST_METHOD']) === 'post') {
    // verify credentials
    if (
    	password_verify($_POST['p'], $config['PASSWORD_HASH']) &&
    	$_POST['csrfToken'] === $_SESSION['csrfToken']
    ){
    	require_once $path_module . 'pages/Main.php';
        exit;
    }
}

require_once $path_module . 'pages/Signin.php';
?>
