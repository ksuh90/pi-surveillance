<?php
/*!
 * Anthony Ferrara <ircmaxell@ircmaxell.com>
 */

class Request {


    protected $get     = array();
    protected $post    = array();
    protected $cookies = array();
    protected $request = array();

    protected $uri    = '';
    protected $url    = '';
    protected $https  = false;
    protected $method = 'get';



    public function getGet()     { return $this->get; }
    public function getPost()    { return $this->post; }
    public function getCookies() { return $this->cookies; }
    public function getRequest() { return $this->request; }



    function __construct() {

        $this->uri = $this->url = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '';
        if (isset($_SERVER['QUERY_STRING'])) {
            $this->uri = str_replace('?' . $_SERVER['QUERY_STRING'], '', $this->uri);
        }
        
        $this->https  = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'];
        $this->method = isset($_SERVER['REQUEST_METHOD']) ? strtolower($_SERVER['REQUEST_METHOD']) : 'get';

        $this->get     = $_GET;
        $this->post    = $_POST;
        $this->cookies = $_COOKIE;
        $this->request = $_REQUEST;
    }

    public function request($name, $default = null) {
        return isset($this->request[$name]) ? $this->request[$name] : $default;
    }

    public function get($name, $default = null) {
        return isset($this->get[$name]) ? $this->get[$name] : $default;
    }

    public function post($name, $default = null) {
        return isset($this->post[$name]) ? $this->post[$name] : $default;
    }

    public function cookie($name, $default = null) {
        return isset($this->cookies[$name]) ? $this->cookies[$name] : $default;
    }

    public function getBody() {
        return file_get_contents('php://input');
    }

    public function getMethod() {
        return $this->method;
    }

    public function getUri() {
        return $this->uri;
    }

    public function getUrl() {
        return $this->url;
    }

    public function isHTTPS() {
        return $this->https;
    }
}