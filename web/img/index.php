<?php
//require_once '../../../../pi-surveillance-module/bootstrap.php';
require_once '../../../pi-surveillance-module/bootstrap.php';

if (!isset($_GET['id']) || !isset($_GET['f'])) exit;

$id = $_GET['id'];
$fname = $_GET['f'];
$auth = $config['CLOUDANT_API_KEY'].':'.$config['CLOUDANT_API_PASS'];
$host = $config['CLOUDANT_HOST'];
$db_name = $config['CLOUDANT_DB_NAME'];
$url = "https://{$auth}@{$host}/{$db_name}/{$id}/{$fname}";
$content = file_get_contents($url);
header('Content-Type: image/jpeg');
echo $content;