<?php

class Token {


    function __construct() {}


    /**
     * http://stackoverflow.com/users/1698153/scott
     * 
     * Return a random number. A REAL random number.
     * This is used in the function create().
     * 
     * @param  int $min minimum
     * @param  int $max maximum
     * @return int      the random int
     */
    private static function secureRand($min, $max) {

        $range = $max - $min;
        if ($range < 0) return $min;      // not so random...
        $log    = log($range, 2);
        $bytes  = (int) ($log / 8) + 1;    // length in bytes
        $bits   = (int) $log + 1;           // length in bits
        $filter = (int) (1 << $bits) - 1; // set all lower bits to 1
        do {
            $rnd = hexdec(bin2hex(openssl_random_pseudo_bytes($bytes)));
            $rnd = $rnd & $filter; // discard irrelevant bits
        } while ($rnd >= $range);
        return $min + $rnd;
    }


    /**
     * http://stackoverflow.com/users/1698153/scott
     * 
     * Create a new token.
     * 
     * @param  int    $length default length is 32
     * @return string $token  return the randomly generated token
     */
    public static function create($length=32) {

        $token = '';
        $codeAlphabet  = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        $codeAlphabet .= 'abcdefghijklmnopqrstuvwxyz';
        $codeAlphabet .= '0123456789';
        for($i=0; $i<$length; $i++) {
            $token .= $codeAlphabet[self::secureRand(0, strlen($codeAlphabet))];
        }
        return $token;
    }


    /**
     * Get the hash of this token.
     * @return string the hashed token, false otherwise.
     */
    public static function getHash($token) {
        return password_hash($token, PASSWORD_BCRYPT);
    }


    /**
     * Verify the a hashed token.
     * @param  string $token the token.
     * @param  string $hash  the hash.
     * @return boolean       true if verified. false otherwise.
     */
    public static function verifyHashedToken($token, $hash) {
        return password_verify($token, $hash);
    }
}
