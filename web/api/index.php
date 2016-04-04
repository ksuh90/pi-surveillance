<?php
require_once 'config.php';

if (strtolower($_SERVER['REQUEST_METHOD']) !== 'post') {
    header('Location: ' . REDIRECT);
    exit;
}


echo "hello from api";