<?php
// Parse config file
$config = parse_ini_file("config.ini");

// PHP config
error_reporting(E_ALL);


/*spl_autoload_register(function($className) {
    $nsLen = strlen(__NAMESPACE__);
    if (!($nsLen) || substr($className, 0, $nsLen + 1) == __NAMESPACE__ . '\\') {
        $path = strtr(substr($className, $nsLen), '\\', '/') . '.php';
        if (file_exists($config['PATH_MODULE'] . $path)) {
            require_once $config['PATH_MODULE'] . $path;
        }
    }
});*/