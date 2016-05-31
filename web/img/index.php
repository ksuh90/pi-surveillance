<?php
//require_once '../../../../pi-surveillance-module/bootstrap.php';
require_once '../../../pi-surveillance-module/bootstrap.php';
require_once $config['PATH_MODULE'] . 'Sag/Sag.php';

if (!isset($_GET['id']) || !isset($_GET['f'])) exit;

$id = $_GET['id'];
$fname = $_GET['f'];

$sag = new Sag($config['CLOUDANT_HOST'], '443');
$sag->login($config['CLOUDANT_API_KEY'], $config['CLOUDANT_API_PASS']);
$sag->useSSL(true);
$sag->setDatabase($config['CLOUDANT_DB_NAME']);
$sag->decode(true);

$resp = $sag->get(urlencode($id) . '/' . urlencode($fname));
$contentType = $resp->headers->{"content-type"};

header('Content-Type: $contentType');
echo $resp->body;
exit;